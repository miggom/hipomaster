# HipoMaster: arquitectura multiagente (v0.1, borrador)

Estado: propuesta para revisión. Sin código todavía.
Fecha: 2026-11-01.

## 1. Objetivo y alcance del MVP

Encontrar la mejor hipoteca para un cliente en España, explicando por qué.

Dentro del MVP:
- Cliente: persona física residente, comprador español. Extranjeros y empresas quedan para perfiles posteriores.
- Inmuebles: vivienda (habitual y segunda), local comercial, garaje, trastero, terreno, nave.
- Operaciones: compra con hipoteca. Subrogación, cambio de banco y novación quedan fuera del MVP pero el modelo de datos los admite.

Fuera del MVP: no residentes, sociedades, promotores, refinanciaciones complejas, firma o envío de solicitudes al banco.

## 2. Contexto del mercado hipotecario español

La fuente única es [docs/contexto-mercado-hipotecario-es.md](contexto-mercado-hipotecario-es.md) (rama `claude/project-thread-vshamp`). Los parámetros por sector (LTV, plazo, diferencial) están en `config/sectores.yaml`.

Uso en el sistema:
- El documento de contexto se indexa en pgvector y alimenta el RAG del Analista de mercado.
- `sectores.yaml` lo leen el Gestor financiero y la calculadora para filtrar elegibilidad. No se copia en los prompts.

## 3. Arquitectura lógica (LangGraph)

```
                    ┌────────────────────┐
  Cliente / UI ───▶ │  Coordinador       │  (supervisor, router de complejidad)
                    └─────────┬──────────┘
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
 ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐
 │ Analista de    │  │ Buscador de    │  │ Gestor financiero  │
 │ mercado        │  │ ofertas        │  │ (docs del cliente) │
 └────────────────┘  └────────────────┘  └────────────────────┘
          │                   │                   │
          └────────── Estado compartido ──────────┘
                     (Postgres checkpointer)
                              │
                     ┌────────▼────────┐
                     │ Redactor        │  (informe final, edge)
                     └─────────────────┘
```

Patrón: supervisor con subgrafos. Cada agente es un subgrafo con sus herramientas. El Coordinador decide el siguiente paso y el modelo a usar.

### 3.1 Agentes
| Agente | Función | Herramientas |
|---|---|---|
| Coordinador | Entiende la petición, crea el perfil, planifica, delega, valida y decide escalado de modelo | router de complejidad, memoria de sesión |
| Analista de mercado | Contexto: Euríbor, tendencias, normativa, rango razonable de diferenciales por perfil e inmueble | RAG (sección 2), APIs BdE/INE, búsqueda web |
| Buscador de ofertas | Recoge y normaliza ofertas por entidad y producto; filtra por elegibilidad | scrapers/conectores por entidad, BD de ofertas, calculadora de cuota/TAE |
| Gestor financiero | Lee documentos del cliente, extrae datos, calcula solvencia, LTV, gastos, y puntúa cada oferta | OCR, extractor de campos, calculadora financiera determinista |
| Redactor | Informe final y respuestas cortas en lenguaje claro | plantillas |

Regla clave: los números (cuota, TAE, ratios, gastos) los calcula código Python determinista, nunca el LLM. El LLM extrae, razona y explica.

### 3.2 Estado compartido (borrador)
```python
class HipoState(TypedDict):
    perfil: ClientProfile          # ingresos, edad, ahorro, contrato, comunidad
    inmueble: Property             # tipo, precio, uso, ubicación, nuevo/usado
    documentos: list[DocRef]       # rutas cifradas, nunca contenido crudo en el estado
    datos_extraidos: dict          # campos validados del Gestor
    mercado: MarketSnapshot        # Euríbor, rangos, fecha
    ofertas: list[Offer]
    evaluacion: list[ScoredOffer]
    plan: list[Step]
    nivel_modelo: Literal["edge", "mid", "frontier"]
    trazas: list[Trace]
```

### 3.3 Flujo principal
1. Coordinador recibe la consulta y clasifica: pregunta corta, simulación, estudio completo.
2. Pregunta corta: respuesta directa en edge con RAG.
3. Estudio completo: Gestor procesa documentos y perfil; en paralelo, Analista crea el snapshot de mercado y Buscador obtiene ofertas.
4. Gestor puntúa las ofertas elegibles con la calculadora.
5. Coordinador valida coherencia; si falla, reintenta con un modelo de nivel superior.
6. Redactor genera el informe. Interrupción humana (human-in-the-loop) antes de entregar en el MVP.

## 4. Enrutado por complejidad

Tres niveles:

| Nivel | Dónde | Modelos | Tareas |
|---|---|---|---|
| edge | fitlet2 + Ollama (CPU) | Qwen2.5 1.5B/3B, Llama 3.2 3B, Gemma 3 4B (Q4_K_M); embeddings nomic-embed-text o bge-m3 | clasificación de intención, preguntas cortas, resúmenes, redacción con plantilla, extracción simple, embeddings |
| mid | VMs con GPU (Ollama o vLLM) | Qwen 7B/8B instruct, DeepSeek-R1-Distill 7B/14B | extracción de documentos, normalización de ofertas, análisis de mercado, razonamiento medio |
| frontier | API | Claude (Haiku para volumen, Sonnet para análisis, Opus para casos difíciles), DeepSeek API | casos ambiguos, comparación final multi-oferta, validación cruzada, perfiles complejos |

Decisión de nivel:
1. Reglas primero: tipo de tarea, tamaño de entrada, número de documentos, importe.
2. Clasificador edge con salida JSON `{tarea, complejidad 1-5, requiere_pii}`.
3. Escalado automático si: JSON inválido, validación Pydantic falla, baja confianza, o el validador detecta incoherencia.
4. Privacidad: datos personales crudos solo en edge o mid (infra propia). Antes de ir a API externa se anonimiza (nombre, DNI, IBAN, direcciones) y se envían solo campos agregados.

Pasarela única: LiteLLM proxy delante de Ollama, vLLM y APIs. Da un solo endpoint compatible con OpenAI, fallbacks, límites de coste y métricas.

## 5. Parámetros por agente (punto de partida)

| Agente / tarea | Nivel por defecto | temperature | top_p | num_ctx / contexto | max salida |
|---|---|---|---|---|---|
| Coordinador: clasificación | edge | 0.0 | 1.0 | 4k | 256 |
| Coordinador: planificación | mid | 0.2 | 0.9 | 16k | 1k |
| Analista de mercado | mid | 0.3 | 0.9 | 16-32k | 2k |
| Buscador: extracción de ofertas | mid | 0.0 | 1.0 | 16k | 2k |
| Gestor: extracción de documentos | mid | 0.0 | 1.0 | 16-32k | 2k |
| Gestor: evaluación final | frontier | 0.2 | 0.9 | 64k+ | 4k |
| Redactor | edge (mid si largo) | 0.5 | 0.9 | 8k | 2k |
| Q&A corta | edge | 0.3 | 0.9 | 4k | 512 |

Notas:
- Extracción y JSON: temperatura 0 y salida estructurada (format=json en Ollama, tool use en Claude).
- En edge, num_ctx alto consume RAM y baja la velocidad; mantener 4k y como mucho 8k.
- Los system prompts se guardan versionados en `prompts/<agente>/vN.md` con variables. Cada uno define rol, límites (no asesoramiento vinculante, no inventar cifras), formato de salida y fecha de los datos.

### 5.1 System prompts (esqueleto)
- Coordinador: "Eres el coordinador de HipoMaster. Clasificas la petición, planificas pasos y delegas. No calculas cifras. Respondes solo en el JSON indicado."
- Analista: "Eres analista del mercado hipotecario español. Usa solo el contexto aportado y cita fuente y fecha. Si falta un dato, dilo."
- Buscador: "Extraes condiciones de ofertas hipotecarias a este esquema. No infieras valores ausentes; déjalos nulos."
- Gestor: "Eres gestor financiero. Extraes datos de documentos del cliente al esquema y señalas inconsistencias. Las cifras las calcula la herramienta."
- Redactor: "Explicas el resultado en español claro, sin jerga, con avisos legales estándar."

## 6. Infraestructura y dimensionado

### 6.1 Nodos edge (fitlet2)
- CPU Intel Atom x5-E3950 o Celeron J3455, 4 núcleos, sin GPU útil para LLM. RAM hasta 16 GB.
- Rendimiento esperado (estimación, a medir): 3B Q4 unos 3-6 tokens/s; 1.5B Q4 unos 6-12 tokens/s. Sirve para respuestas cortas y clasificación, no para documentos largos.
- Recomendado: 16 GB RAM, SSD, Ollama con `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=2`, `num_thread=4`, un modelo de chat + uno de embeddings por nodo.
- Varios fitlet2 detrás de LiteLLM con balanceo round-robin. Cada nodo atiende una petición a la vez.

### 6.2 VMs mid
- Qwen 7B/8B en Q4: 6-8 GB VRAM. En FP16: unos 16 GB. Una GPU de 16-24 GB permite contexto de 32k y algo de concurrencia.
- DeepSeek-R1-Distill 14B en Q4: unos 10-12 GB VRAM.
- Si no hay GPU, un 7B en CPU va lento (2-5 tokens/s); usar solo en batch.
- Servidor: vLLM para concurrencia, Ollama para simplicidad. RAM del host 32 GB, 8 vCPU, 100 GB disco.

### 6.3 Servicios centrales
- LangGraph server (o FastAPI + LangGraph) en contenedor.
- Postgres (checkpointer, ofertas, perfiles) + pgvector para RAG.
- Redis (colas, caché).
- LiteLLM proxy.
- Almacén de documentos cifrado (MinIO o disco cifrado).
- Observabilidad: Langfuse (trazas, coste, evaluación) + Prometheus/Grafana.
- Despliegue inicial: Docker Compose. Más adelante k3s si crecen los nodos.

## 7. Seguridad y cumplimiento
- Cifrado en reposo y en tránsito. Acceso mínimo por servicio.
- PII nunca sale de infraestructura propia sin anonimizar. Registro de qué datos van a cada proveedor.
- Retención y borrado de documentos según RGPD; consentimiento explícito.
- Aviso: la herramienta da información y comparativas, no asesoramiento financiero regulado ni oferta vinculante.

## 8. Evaluación
- Conjunto de casos de prueba: perfiles sintéticos por tipo de inmueble.
- Métricas: precisión de extracción por campo, acierto del router, coste por estudio, latencia, % de escalados.
- Comparar edge vs mid vs frontier en cada tarea para ajustar el router.

## 9. Fases
1. Fase 0: este documento, decisiones abiertas cerradas.
2. Fase 1: esqueleto LangGraph, LiteLLM con un nodo edge y Claude, calculadora financiera, RAG con sección 2.
3. Fase 2: Gestor financiero con extracción de nóminas e IRPF, anonimización.
4. Fase 3: Buscador con 5-10 entidades, normalización y puntuación.
5. Fase 4: router aprendido con métricas reales, más nodos, perfiles extranjeros y empresas.

## 10. Preguntas abiertas
1. ¿Cuántos fitlet2 hay y con cuánta RAM cada uno?
2. ¿Las VMs tienen GPU? ¿Qué modelo y VRAM?
3. "DeepSeek pro": ¿API de DeepSeek (V3/R1) o modelo autoalojado (distill 7B/14B)?
4. ¿Presupuesto mensual para APIs (Claude, DeepSeek)?
5. ¿Fuente de ofertas: scraping de webs de bancos, datos introducidos a mano, o acuerdos con entidades o brókers?
6. ¿Interfaz del MVP: web, chat (Telegram/WhatsApp), o API?
7. ¿Uso interno (asesor) o directo al cliente final? Afecta a requisitos legales.

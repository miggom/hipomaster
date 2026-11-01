# HipoMaster: arquitectura multiagente (v0.1, borrador)

Estado: propuesta para revisión. Sin código todavía.
Fecha: 2026-11-01.

## 1. Objetivo y alcance del MVP

Encontrar la mejor hipoteca para un cliente en España, explicando por qué.

Dentro del MVP:
- Cliente: persona física residente, comprador español. Extranjeros y empresas quedan para perfiles posteriores.
- Inmuebles: vivienda (habitual y segunda), local comercial, garaje, trastero, terreno, nave.
- Operaciones: compra con hipoteca y **subrogación (cambio de banco), prioritaria**: el usuario la testeará con su propia hipoteca. Novación queda fuera del MVP.
- Ámbito geográfico inicial: Madrid (ITP, bonificaciones y programas de la Comunidad de Madrid).

Fuera del MVP: no residentes, sociedades, promotores, novaciones, firma o envío de solicitudes al banco.

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

## 6. Infraestructura y dimensionado (hardware confirmado)

Recursos disponibles:
- 4 fitlet2 con 8 GB RAM cada uno, Ollama, sin GPU.
- 1 VM Ubuntu con 16 GB RAM (sin GPU confirmada). Posible ampliación a AWS.
- API DeepSeek (pro y flash) con saldo. Presupuesto total de APIs: 5 USD.

### 6.1 Nodos edge (fitlet2, 8 GB)
- Modelos recomendados: Qwen2.5 3B Q4_K_M (~2.5 GB) para chat y clasificación; embeddings nomic-embed-text (~0.3 GB). Un 7B Q4 (~5 GB) cabe pero va a 1-3 tokens/s: solo en batch.
- Reparto sugerido: nodo 1-2 chat/clasificación, nodo 3 embeddings y extracción simple, nodo 4 reserva y scraping.
- `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_MAX_LOADED_MODELS=2`, `num_ctx` 4k (máx. 8k).
- Balanceo con LiteLLM.

### 6.2 VM Ubuntu 16 GB (nivel mid local)
- Qwen 7B/8B Q4 (~5 GB) con contexto 16k: cabe. DeepSeek-R1-Distill 14B Q4 (~9 GB) cabe justo, sin margen para otros servicios.
- Sin GPU: 2-5 tokens/s. Usarla para tareas en batch (extracción de documentos, normalización de ofertas), no interactivas.
- En la misma VM: LangGraph, Postgres+pgvector, Redis, LiteLLM, Langfuse. Con 16 GB, limitar el modelo a 7B.
- Si se necesita más: AWS g5.xlarge (A10G 24 GB) bajo demanda, solo cuando haga falta.

### 6.3 Nivel frontier con 5 USD
- DeepSeek flash sustituye al nivel mid cuando se necesita rapidez o contexto largo. DeepSeek pro para razonamiento y evaluación final.
- Claude solo para validación final de casos difíciles, con tope de gasto duro en LiteLLM (budget por día y por mes). Con 5 USD, usar Haiku/Sonnet y entradas cortas anonimizadas.
- Tope sugerido: 0,5 USD/día y alerta al 80%.
- Prioridad de escalado: edge, VM local, DeepSeek flash, DeepSeek pro, Claude.
- Datos personales crudos solo en edge y VM local. A DeepSeek y Claude solo datos anonimizados.

### 6.4 Servicios centrales
LangGraph server, Postgres + pgvector, Redis, LiteLLM proxy, almacén cifrado, Langfuse. Docker Compose en la VM.

### 6.5 Interfaz web
Opción recomendada: **Agent Chat UI** (proyecto abierto de LangChain, Next.js). Se conecta directo a un servidor LangGraph, muestra el chat, las llamadas a herramientas y las interrupciones human-in-the-loop. Sin desarrollo de frontend en el MVP.
Alternativas: LangGraph Studio (solo para desarrollo y depuración) y Open WebUI (más genérica, requiere adaptador).

## 7. Seguridad y cumplimiento
- Cifrado en reposo y en tránsito. Acceso mínimo por servicio.
- PII nunca sale de infraestructura propia sin anonimizar. Registro de qué datos van a cada proveedor.
- Retención y borrado de documentos según RGPD; consentimiento explícito.
- Aviso: la herramienta da información y comparativas, no asesoramiento financiero regulado ni oferta vinculante.

## 8. Evaluación
- Conjunto de casos de prueba: perfiles sintéticos por tipo de inmueble.
- Métricas: precisión de extracción por campo, acierto del router, coste por estudio, latencia, % de escalados.
- Comparar edge vs mid vs frontier en cada tarea para ajustar el router.

## 8b. Flujo prioritario: subrogación

Entrada: datos de la hipoteca actual (capital pendiente, tipo, TIN, diferencial, plazo restante, cuota, vinculaciones) y escritura o último recibo.
1. Gestor financiero extrae los datos del préstamo actual y calcula el coste de seguir como está.
2. Buscador obtiene ofertas de subrogación de entidades en Madrid (scraping) y tipos de referencia del Banco de España.
3. Calculadora determinista: cuota nueva, ahorro mensual y total, comisión de amortización/subrogación de la entidad actual (límites legales de la LCCI), coste de tasación, notaría y registro, y punto de equilibrio en meses.
4. Analista de mercado explica el contexto (Euríbor, tendencia) y riesgos (vinculaciones, seguros).
5. Redactor genera el informe: "compensa o no cambiar" con cifras.

Fuentes: scraping de entidades y Banco de España (research con Opus en hilo aparte). Subrogación entra en la Fase 1.

## 9. Fases
1. Fase 0: este documento, decisiones abiertas cerradas.
2. Fase 1: esqueleto LangGraph, flujo de subrogación para Madrid, LiteLLM con un nodo edge y Claude, calculadora financiera, RAG con sección 2.
3. Fase 2: Gestor financiero con extracción de nóminas e IRPF, anonimización.
4. Fase 3: Buscador con 5-10 entidades, normalización y puntuación.
5. Fase 4: router aprendido con métricas reales, más nodos, perfiles extranjeros y empresas.

## 10. Decisiones y preguntas abiertas

Cerradas (2026-11-01): 4 fitlet2 de 8 GB; VM Ubuntu 16 GB; DeepSeek pro y flash por API; presupuesto 5 USD; ofertas por scraping (hilo de research aparte); interfaz web preexistente (Agent Chat UI).

Abiertas:
1. ¿La VM tiene GPU? Se asume que no.
2. ¿Uso interno (asesor) o cliente final? Afecta a requisitos legales.
3. ¿Qué bancos se priorizan en el primer scraping?

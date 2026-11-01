# Obtención de ofertas hipotecarias (agente Buscador)

Estado: propuesta v0.2 para revisión. Fecha: 2026-11-01.
Prioridades fijadas por doc: Madrid primero, **subrogación prioritaria**, fuentes = scraping + Banco de España.
Relacionado: [ARQUITECTURA.md](ARQUITECTURA.md) (secciones 3.1 y 6).

## 1. Resumen y recomendación

- No hace falta un scraper "masivo". El mercado relevante son unas 25-30 entidades con 2-5 productos cada una. Son menos de 150 páginas, que cambian pocas veces al mes.
- Estrategia en tres capas, de más fiable a menos:
  1. **Fuente agregada estructurada** para arrancar: comparadores que ya publican TIN/TAE por entidad con fecha y fuente (p. ej. `hipotecas.me/llms-full.txt`, pensado para LLMs; solo pide citar la fuente).
  2. **Webs oficiales de cada banco**: páginas de producto y PDF de "información precontractual / ejemplo representativo". Son la fuente de verdad.
  3. **Simuladores con formulario**: fuera del MVP. Requieren rellenar datos y suelen tener antibot.
- Extracción: HTML/PDF a texto, después un modelo local (Qwen2.5 3B o 7B) con temperatura 0 y salida JSON validada con Pydantic. Las cifras derivadas (cuota, TAE de control) las calcula Python.
- Coste API: casi 0 USD. Solo se llama al LLM cuando el contenido de una página cambia (hash). DeepSeek flash es el respaldo si el modelo local falla la validación.
- Dónde corre: fitlet2 nº 4 (Playwright + extractor) y Postgres en la VM.

## 2. Fuentes

### 2.1 Entidades a cubrir (lista inicial, 20)
Santander, BBVA, CaixaBank, Sabadell, Bankinter, ING, Openbank, Unicaja, Kutxabank, Ibercaja, Abanca, Cajamar, Caja Rural (grupo), Laboral Kutxa, MyInvestor, EVO Banco, Deutsche Bank España, UCI, Targobank, Banco Mediolanum.

Se guardan en `config/entidades.yaml` con: id, nombre, URLs de producto, URL de PDF precontractual, método (`http` o `browser`), selector o pista de extracción, frecuencia.

### 2.2 Qué publica cada banco
- Página comercial del producto: TIN, TAE, diferencial, tramo fijo, plazo máximo, financiación máxima, bonificaciones (nómina, seguros, tarjeta, plan de pensiones).
- Ejemplo representativo (obligatorio en publicidad de crédito inmobiliario): importe, plazo, TIN, TAE, coste total, número de cuotas. Suele estar en letra pequeña o en PDF.
- Información general precontractual (Ley 5/2019 y Orden EHA/2899/2011): PDF con condiciones del producto. Es la fuente más completa y estable.
- Lo que no publican: precio para un perfil concreto. Eso solo sale en la FEIN tras estudio. El sistema debe presentar las ofertas como "condiciones publicadas", nunca como oferta vinculante.

### 2.3 Comparadores
| Fuente | Uso | Riesgo |
|---|---|---|
| hipotecas.me (`llms-full.txt`, páginas `/bancos/{producto}`) | Arranque y verificación cruzada. Da TIN, TAE, diferencial, fuente y fecha | Bajo: publica para LLMs y pide citar. Revisar sus términos antes de producción |
| HelpMyCash, Rastreator, Kelisto, idealista/hipotecas | Solo consulta manual o verificación puntual | Medio/alto: términos de uso suelen prohibir extracción; muchos son intermediarios con acuerdos comerciales |
| Banco de España (clientebancario.bde.es, estadísticas) | Euríbor, tipos medios, índices oficiales. Lo usa el Analista, no el Buscador | Ninguno: datos públicos |

## 3. Legalidad (no es asesoramiento jurídico)

- Datos de precios publicados sin login: en España el Tribunal Supremo consideró lícito el screen scraping de Atrápalo sobre Ryanair (2012) al no haber base de datos protegida ni perjuicio sustancial.
- TJUE C-30/14 (Ryanair v PR Aviation, 2015): si la base de datos no está protegida por derecho de autor ni sui generis, el titular **puede** prohibir la extracción por contrato (términos de uso). Por eso los términos de cada web importan.
- No se tratan datos personales al extraer ofertas: el RGPD no aplica a esta parte.
- Reglas operativas que adoptamos:
  1. Respetar `robots.txt` y los términos de uso de cada sitio. Si prohíben extracción automática, la entidad pasa a modo manual o se usa solo su PDF público.
  2. Nada detrás de login, captcha o formulario.
  3. Ritmo bajo: 1 petición cada 10-30 s por dominio, una pasada semanal, caché local.
  4. User-Agent identificable con contacto (`HipoMasterBot/0.1 (+email)`).
  5. Guardar URL, fecha y hash de cada dato, y citar la fuente en el informe.
  6. No republicar las páginas; solo los campos normalizados para uso interno.
- Antes de un uso comercial con clientes, revisarlo con un abogado. Como el sistema compara y recomienda hipotecas, valorar también si la actividad encaja como intermediario de crédito inmobiliario (Ley 5/2019).

## 4. Pipeline

```
scheduler (cron semanal)
   │
   ▼
fetch ── http (httpx) ──┐         si JS o bloqueo → Playwright (Chromium headless)
                        ▼
             normalizar a texto (trafilatura / selectolax; PDF: pdfplumber)
                        │
               hash igual al anterior? ── sí → fin (sin coste LLM)
                        │ no
                        ▼
        extractor LLM local (Qwen2.5 3B/7B, T=0, JSON schema)
                        │
        validación Pydantic + reglas (TAE ≥ TIN, rangos de sectores.yaml)
           │ falla                       │ ok
           ▼                             ▼
   reintento 7B → DeepSeek flash   Postgres: offers + offer_history
           │ falla                       │
           ▼                             ▼
   cola de revisión manual         diff → aviso si cambia TIN/TAE
```

Notas:
- Herramienta del Buscador en LangGraph: `buscar_ofertas(perfil, inmueble)` lee de Postgres. El scraping es un proceso batch aparte, no corre durante la conversación.
- Las ofertas con más de 30 días se marcan como caducadas.
- Para locales, garajes, trasteros, terrenos y naves casi ningún banco publica producto específico. Se aplica la oferta base de vivienda más los ajustes de `sectores.yaml` y se marca como `estimada`.

## 5. Esquema `Offer` normalizado

Alineado con `HipoState.ofertas: list[Offer]` de ARQUITECTURA.md.

```python
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl

class TipoInteres(str, Enum):
    fijo = "fijo"
    variable = "variable"
    mixto = "mixto"

class Sector(str, Enum):
    vivienda_habitual = "vivienda_habitual"
    segunda_vivienda = "segunda_vivienda"
    local = "local"
    garaje = "garaje"
    trastero = "trastero"
    terreno_urbano = "terreno_urbano"
    terreno_rustico = "terreno_rustico"
    nave = "nave"

class Operacion(str, Enum):
    compra = "compra"
    subrogacion = "subrogacion"          # subrogación acreedora (se mantiene la escritura)
    cambio_banco = "cambio_banco"        # cancelación + hipoteca nueva (p. ej. Openbank)

class Bonificacion(BaseModel):
    concepto: str                       # "nómina", "seguro hogar", "seguro vida", "tarjeta", "plan pensiones"
    reduccion_pp: Decimal               # puntos porcentuales que rebaja
    coste_anual_estimado: Decimal | None = None
    condicion: str | None = None        # p. ej. "nómina ≥ 2.000 €"

class Tramo(BaseModel):
    desde_anio: int
    hasta_anio: int | None              # None = hasta el final
    tipo: TipoInteres                   # fijo o variable en ese tramo
    tin: Decimal | None = None          # si fijo
    indice: str | None = None           # "euribor_12m" si variable
    diferencial: Decimal | None = None  # si variable

class EjemploRepresentativo(BaseModel):
    importe: Decimal
    plazo_meses: int
    tin: Decimal
    tae: Decimal
    cuota: Decimal | None = None
    coste_total: Decimal | None = None

class Fuente(BaseModel):
    url: HttpUrl
    tipo: str                           # "web_banco", "pdf_precontractual", "comparador", "manual"
    obtenida: datetime
    hash_contenido: str
    metodo: str                         # "http", "browser", "manual"

class Offer(BaseModel):
    id: str                             # "{entidad}:{producto}:{fecha}"
    entidad: str                        # id de config/entidades.yaml
    producto: str                       # nombre comercial
    tipo: TipoInteres
    sectores: list[Sector] = [Sector.vivienda_habitual]
    operaciones: list[Operacion] = [Operacion.compra]
    ambito: list[str] = ["nacional"]    # o códigos CCAA/provincia, p. ej. ["MD"]
    aval_publico: list[str] = []        # p. ej. ["mi_primera_vivienda_madrid", "ico"]
    paga_tasacion_banco: bool | None = None   # relevante en subrogación
    tramos: list[Tramo]
    tin_bonificado: Decimal | None = None
    tin_sin_bonificar: Decimal | None = None
    tae_bonificada: Decimal | None = None
    tae_sin_bonificar: Decimal | None = None
    bonificaciones: list[Bonificacion] = []
    ltv_max: Decimal | None = None      # % sobre tasación o compraventa
    plazo_max_anios: int | None = None
    edad_max_fin: int | None = None
    importe_min: Decimal | None = None
    ingresos_min: Decimal | None = None
    comision_apertura_pct: Decimal | None = None
    comision_amort_anticipada: str | None = None
    solo_vivienda_habitual: bool | None = None
    requisitos: list[str] = []          # texto libre corto
    ejemplo: EjemploRepresentativo | None = None
    estimada: bool = False              # True si deriva de vivienda + sectores.yaml
    fuente: Fuente
    vigente_desde: date
    caduca: date                        # vigente_desde + 30 días por defecto
    confianza: float = Field(ge=0, le=1)  # del extractor/validador
```

Reglas de validación mínimas:
- `tae >= tin` en cada par (bonificado y no bonificado).
- TIN entre 0,5 % y 8 %; diferencial entre 0 y 4 pp.
- `ltv_max` y `plazo_max_anios` no superan los de `sectores.yaml` para el sector.
- Campos no presentes en la fuente quedan en `None`. El prompt prohíbe inferir.

Tablas: `offers` (vigente por entidad+producto) y `offer_history` (todas las versiones, para ver tendencias).

## 5bis. Subrogación (prioridad 1)

Para comparar un cambio de banco hace falta, además de la `Offer`, la hipoteca actual del cliente y el coste del cambio. Lo calcula código, no el LLM.

```python
class HipotecaActual(BaseModel):
    entidad: str
    fecha_firma: date                   # decide si aplica Ley 5/2019 (desde 16/06/2019)
    capital_pendiente: Decimal
    plazo_restante_meses: int
    tipo: TipoInteres
    tin_actual: Decimal
    indice: str | None = None
    diferencial: Decimal | None = None
    fin_tramo_fijo: date | None = None
    comision_reembolso_pactada: str | None = None   # texto de la escritura
    productos_vinculados: list[Bonificacion] = []
```

Reglas de la calculadora `coste_cambio()` (resumen de la Ley 5/2019, a contrastar con el BOE):
- Hipotecas desde el 16/06/2019. Variable: máximo 0,25 % los 3 primeros años o 0,15 % los 5 primeros (lo pactado), después 0 %. Fija: 2 % los 10 primeros años, 1,5 % después. Mixta: cada tramo con su regla.
- Paso de variable a fija (o mixta con 3+ años fijos): máximo 0,05 % los 3 primeros años, 0 % después. Aplica también a hipotecas anteriores a 2019.
- Hipotecas anteriores a 2019: lo pactado en la escritura (el Gestor lo extrae del documento).
- Notaría, registro, gestoría y AJD los paga el banco. Tasación: el cliente (250-450 €) salvo que el banco la bonifique.
- Resultado: ahorro neto = diferencia de cuotas a plazo restante, menos comisión y tasación, menos coste anual de bonificaciones. Se da también el punto de equilibrio en meses.

Impacto en el scraping:
- En `config/entidades.yaml` cada entidad lleva `acepta_subrogacion` y URL específica de subrogación si existe. Se rastrean primero.
- Entidades conocidas con oferta de subrogación (Rankia, 01/10/2026, a verificar en web oficial): Ibercaja, Sabadell, Kutxabank, ING; Openbank lo hace como cancelación + hipoteca nueva (`cambio_banco`); BBVA también compite según la misma fuente.

## 5ter. Banco de España (fuente oficial)

API JSON pública, sin clave:
- Último dato: `https://app.bde.es/bierest/resources/srdatosapp/favoritas?idioma=es&series=<códigos>`
- Serie histórica: `https://app.bde.es/bierest/resources/srdatosapp/listaSeries?idioma=es&series=<códigos>&rango=30M` (`rango`: 3M/12M/36M diarias; 30M/60M/MAX mensuales; o un año).
- Códigos de serie: buscarlos en BIEST o en los CSV de las tablas de tipos de interés (Euríbor 12m, IRPH, tipos medios de nuevas hipotecas). Tarea pendiente: fijarlos en `config/bde_series.yaml`.

Uso:
| Dato | Agente | Para qué |
|---|---|---|
| Euríbor 12m (mensual oficial) | Analista, calculadora | cuotas de variables y mixtas, revisión de la hipoteca actual |
| Tipo medio de nuevas hipotecas | Analista | ver si una oferta está por encima o debajo del mercado |
| IRPH | Gestor | clientes con hipoteca antigua referenciada a IRPH |
| Registro de entidades | Buscador | validar que la entidad está autorizada |

No es scraping: se llama a la API con cron diario y se guarda en Postgres (`market_series`).

## 5quater. Madrid primero

- `ambito` en `Offer` y en `entidades.yaml`. Se rastrean primero entidades nacionales y las que operan en Madrid.
- Aval público: programa "Mi Primera Vivienda" de la Comunidad de Madrid (aval hasta 95-100 % de financiación; edad ampliada según las últimas reformas, a verificar). Se marca qué entidades están adheridas (`aval_publico`). Fuentes: comunidad.madrid y páginas de los bancos (p. ej. Santander tiene página específica).
- No aplica a subrogación; solo a compra de primera vivienda.

## 6. Frecuencia

| Dato | Frecuencia | Motivo |
|---|---|---|
| Páginas y PDF de bancos | semanal (domingo noche) | cambian pocas veces al mes |
| Comparador agregado | semanal, mismo día | verificación cruzada |
| API Banco de España | diaria | Euríbor, tipos medios, IRPH |
| Páginas de subrogación | 2 veces por semana mientras doc prueba su cambio | prioridad |
| Revisión manual de cola de errores | semanal | 5-15 min |

## 7. Herramientas y recursos

| Pieza | Elección | RAM aprox. |
|---|---|---|
| HTTP | `httpx` + `selectolax` | < 100 MB |
| Navegador (solo si hace falta) | Playwright Chromium headless, 1 instancia, 1 pestaña | 300-600 MB |
| Texto de HTML | `trafilatura` | bajo |
| PDF | `pdfplumber` (tablas) | bajo |
| Extractor LLM | Ollama Qwen2.5 3B Q4 (7B en la VM si falla), `format=json`, T=0, `num_ctx` 8k | 2,5 GB (3B) |
| Orquestación | cron + script Python, o LangGraph cron job si se usa LangGraph Platform | bajo |
| Almacén | Postgres de la VM | ya previsto |
| Observabilidad | Langfuse (ya previsto) | ya previsto |

Opcional: `crawl4ai` integra Playwright y salida markdown para LLM, pero añade dependencias. Empezar sin él.

Despliegue: fitlet2 nº 4 ejecuta fetch y extracción 3B. Cabe en 8 GB con margen. La VM solo recibe el reintento 7B.

## 8. Coste

- Peticiones: unas 150 por semana. Sin proxies de pago.
- LLM local: 0 USD. Con detección por hash, solo se extraen 5-20 páginas por semana.
- DeepSeek flash como respaldo: unos 20 reintentos al mes de ~6k tokens de entrada son ~0,1 M tokens, del orden de céntimos. Tope duro en LiteLLM: 0,20 USD/mes para esta tarea.
- Claude: no se usa en el scraping.

## 9. Riesgos

- Antibot (Akamai, Cloudflare) en grandes bancos: si bloquea, no se evade; la entidad pasa a PDF público o a entrada manual.
- Bonificaciones: textos ambiguos. El LLM las extrae, pero la TAE no bonificada es el dato que se compara.
- Cambios de diseño web: el pipeline no depende de selectores fijos (texto + LLM). La cola de revisión detecta fallos.
- Datos de comparadores pueden ir atrasados: siempre gana la web oficial del banco si la fecha es más reciente.

## 10. Próximos pasos

1. Completar `config/entidades.yaml` (borrador creado) con URLs verificadas, `robots.txt` y términos. La lista de entidades la cierra el hilo de investigación de mercado.
2. Fijar códigos de serie del BdE en `config/bde_series.yaml` y cliente de la API.
3. Calculadora `coste_cambio()` y modelo `HipotecaActual` para que doc pruebe su subrogación.
4. Prototipo de scraping con 4 entidades de subrogación (Ibercaja, Sabadell, Kutxabank, ING) + `llms-full.txt`.
5. Prompt del extractor `prompts/buscador/v1.md` y pruebas con 10 páginas reales.
6. Medir precisión del 3B frente a revisión manual. Si < 90 % de campos correctos, pasar a 7B en la VM.

## Fuentes
- [Banco de España: API de estadísticas](https://www.bde.es/webbe/es/estadisticas/recursos/api-estadisticas-bde.html)
- [Rankia: mejores hipotecas para subrogación (act. 01/10/2026)](https://www.rankia.com/blog/mejores-hipotecas/3505091-mejores-hipotecas-para-subrogacion)
- [hipotecas.me: comisiones de subrogación con la Ley 5/2019](https://www.hipotecas.me/guias/subrogacion-hipoteca/comisiones-subrogacion-ley-2019)
- [Comunidad de Madrid: Mi Primera Vivienda](https://www.comunidad.madrid/node/64190)
- [hipotecas.me, llms-full.txt](https://www.hipotecas.me/llms-full.txt)
- [Banco de España, Portal del Cliente Bancario: tipo de interés de hipotecas fijas](https://clientebancario.bde.es/pcb/es/blog/tipo-de-interes-de-prestamos-hipotecarios-a-tipo-fijo-para-compra-de-vivienda-habitual.html)
- [Ley 5/2019, BOE-A-2019-6301](https://www.boe.es/boe/dias/2019/04/29/pdfs/BOE-A-2019-6301.pdf)
- [ECIJA: Ryanair pierde su batalla frente a las agencias online](https://www.ecija.com/actualidad-insights/ryanair-pierde-su-batalla-legal-frente-a-las-agencias-de-viajes-online/)
- [Caso C-30/14 Ryanair (resumen)](https://eulawradar.com/case-c-3014-ryanair-grounding-a-go-compare-an-airfare-website/)
- [Portolano: TJUE sobre la Directiva de bases de datos y screen scraping](https://portolano.it/news/ecj-clarifies-database-directive-scope-in-screen-scraping-case)

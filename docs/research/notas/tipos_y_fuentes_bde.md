# Tipos de referencia hipotecarios en España y fuentes oficiales/APIs para su actualización automática (a 1 de noviembre de 2026)

> Nota metodológica: el entorno de investigación no podía conectarse directamente a data-api.ecb.europa.eu, app.bde.es ni servicios.ine.es (proxy 403, y la API del BCE bloquea WebFetch por robots.txt). Los valores se tomaron de los CSV oficiales del BdE (bde.es, accesibles), del BOE, de la nota de prensa del INE y de agregadores, que se señalan como tales. Ningún endpoint de API se ha probado en vivo desde aquí; los formatos proceden de la documentación oficial.

## Euríbor 12M: último valor (oct-2026), tendencia y previsiones para 2027

### Takeaway
El Euríbor 12M lleva subiendo todo 2026: de ~2,22 % en feb-2026 a 3,247 % (media oficial de septiembre, BOE) y ~3,24 % en octubre (dato provisional de agregadores; el BdE lo publica oficialmente en el BOE en torno al 2-3 de noviembre). El BCE subió tipos en junio y septiembre de 2026 (facilidad de depósito al 2,50 %). Los analistas esperan otra subida en diciembre y un máximo del 3,00 % en primavera de 2027. No se encontró una previsión explícita del Euríbor 12M para 2027 en fuentes fiables.

### Cited Findings
- **Septiembre 2026, valor oficial:** la Resolución del BdE de 1-oct-2026 (BOE 2-oct-2026) fija para septiembre 2026: Euríbor 1 año **3,247 %**, 6 meses 2,922 %, 3 meses 2,635 %, 1 mes 2,414 %, 1 semana 2,289 %, IRS 5 años 3,450 %, €STR a 1 año 2,034 % y Míbor 1 año 3,247 % (el Míbor solo es oficial para préstamos anteriores a 2000). — [BOE-A-2026-20519](https://boe.es/boe/dias/2026/10/02/pdfs/BOE-A-2026-20519.pdf)
- **Medias mensuales 2026 (agregador):** ene 2,245; feb 2,221; mar 2,565; abr 2,747; may 2,804; jun 2,798; jul 2,855; ago 2,954; **sep 3,247; oct 3,239** (provisional). Media anual 2025: 2,223 %. — [euribor.com.es](https://www.euribor.com.es/valores/historico/2026)
- Idealista da cifras casi iguales con pequeñas diferencias (mar 2,567; jun 2,795; jul 2,839; ago 2,951; sep 3,243; **oct 3,238**) y un titular del 30-oct-2026: "el euríbor cierra octubre en el 3,23 %". — [idealista](https://www.idealista.com/news/euribor/anual/evolucion-ano-actual/). *Discrepancia de hasta 0,016 pp con euribor.com.es (por ejemplo, julio 2,855 frente a 2,839). Hay que usar el dato oficial del BdE/BOE.*
- **BCE:** el 10-sep-2026 subió los tres tipos oficiales 25 pb, con efecto el 16-sep: facilidad de depósito 2,50 %, MRO 2,65 % y facilidad marginal de crédito 2,90 %. Fue la segunda subida de 2026, tras la de junio. Ese día el Euríbor diario estaba en 3,138 %. El supuesto técnico del BCE para el Euríbor a 3 meses es 2,4 % en 2026 y 3,0 % en 2027-2028. — [Futur Finances, 10-sep-2026](https://futurfinances.com/?p=51479); confirmación en el [BdE: "El BCE sube los tipos 25 puntos básicos en septiembre"](https://www.bde.es/wbe/es/noticias-eventos/actualidad-bce/decisiones-politica-monetaria/el-bce-sube-los-tipos-25-puntos-basicos-en-septiembre-2026.html)
- **Previsión de CaixaBank Research (22-oct-2026):** espera que el BCE mantenga tipos en la reunión del 29-oct, suba en diciembre hasta el 2,75 % (el mercado lo descuenta en torno al 90 %) y alcance un máximo del 3,00 % en primavera de 2027, con posibles recortes antes de fin de 2027. El mercado descuenta un depósito del 3,25 % en verano de 2027. En ese momento el Euríbor 12M estaba "ligeramente por encima del 3,2 %". — [CaixaBank Research](https://www.caixabankresearch.com/en/publications/notas-breves-actualidad-economica-y-financiera/central-banks-observatory/bce-pausa-0)
- **Previsión de BBVA (oct-2026):** el BCE mantiene en octubre y vuelve a subir en diciembre de 2026. No da cifra de Euríbor. — [BBVA](https://www.bbva.es/empresas/productos/negocio-internacional/noticias-comex/perspectivas-y-previsiones-oct26.html)
- **Previsiones para diciembre de 2026 (anteriores al ciclo de subidas):**
  - Futur Finances (1-sep-2026): escenario central 3,05-3,20 %.
  - Bankinter (junio 2026): 2,65-2,75 %.
  - Panel Funcas (julio 2026): ~2,7 %.
  - Las previsiones de Bankinter y Funcas quedaron desfasadas por la subida de septiembre. — [Futur Finances](https://futurfinances.com/?p=51471)
- Contexto: la subida responde a un shock energético e inflacionista. Las proyecciones del BCE de septiembre de 2026 sitúan la inflación de 2027 en el 2,5 %. — [Futur Finances](https://futurfinances.com/?p=51479)

### Inferences
- La tendencia es alcista, aunque se estabiliza en oct-2026 (3,24 frente a 3,247 en septiembre). Si el BCE sube al 2,75 % en diciembre y al 3,00 % en 2027, el Euríbor 12M, que anticipa la senda, se mantendría probablemente en un rango del 3,0-3,4 % durante buena parte de 2027. Es una inferencia, no una previsión publicada.
- Las hipotecas que se revisan con el dato de octubre de 2026 suben aproximadamente 1 pp frente a octubre de 2025 (2,187 %, según [Última Hora](https://www.ultimahora.es/noticias/local/2025/10/31/2502925/euribor-sube-octubre-187-encarece-hipotecas.html)).

### Gaps
- No se pudo confirmar la decisión real del BCE del 29-oct-2026: las fuentes encontradas son previas a la reunión.
- No se encontró una previsión explícita del Euríbor 12M para 2027 de bancos ni de organismos (Funcas, BdE, AIReF).
- El dato oficial del BdE para octubre de 2026 aún no estaba publicado el 1-nov. Saldrá en la Resolución del BdE del primer día hábil de noviembre y en el BOE del día siguiente.

## Otros índices oficiales del BdE (IRPH Entidades, etc.)

### Takeaway
El IRPH Entidades de septiembre de 2026 es **3,189 %** (BOE 20-oct-2026), muy cerca del Euríbor 12M. El BdE publica el IRPH en torno al día 19 de cada mes, en una resolución distinta a la del Euríbor, que se publica a primeros de mes.

### Cited Findings
- **Resolución del BdE de 19-oct-2026 (BOE 20-oct-2026):**
  - Tipo medio de préstamos hipotecarios a más de 3 años para adquisición de vivienda libre, conjunto de entidades de crédito en España (IRPH Entidades): **3,189 %** (septiembre 2026).
  - Tipo medio de préstamos para vivienda entre 1 y 5 años, zona euro: **3,600 %**. Según el texto corresponde al mes anterior, probablemente agosto de 2026.
  - — [BOE-A-2026-21866](https://boe.es/boe/dias/2026/10/20/pdfs/BOE-A-2026-21866.pdf)
- **Serie IRPH Entidades 2026:** ene 2,762; feb 2,819; mar 2,840; abr 2,882; may 2,986; jun 3,049; jul 3,077; ago 3,134; sep 3,189. — [HelpMyCash (cita el BOE)](https://www.helpmycash.com/hipotecas/irph). El valor de agosto (3,134 %) coincide con [esta noticia sobre el BOE](https://everythingedinburgh.com/es/finanzas/noticias/banco-espana-tipo-hipotecario-boe-3-134/).
- **Lista de tipos oficiales** (art. 27 de la Orden EHA/2899/2011, modificada por la Orden ETD/699/2020, y Circular BdE 5/2012, anejo 8, modificada por la Circular 1/2021):
  - Euríbor a 1 semana, 1, 3, 6 y 12 meses, como medias mensuales de EMMI.
  - Rendimiento de la deuda pública de 2 a 6 años (índice RODE de BME).
  - IRS a 5 años (ICE Benchmark Administration).
  - IRPH Entidades.
  - Tipo medio de préstamos de 1 a 5 años en la zona euro.
  - Tipos de referencia basados en el €STR.
  - El BdE replica el Euríbor mensual que produce EMMI y ya no lo calcula él mismo.
  - — [Cliente Bancario BdE](https://clientebancario.bde.es/pcb/es/menu-horizontal/podemosayudarte/tiposinteres/guia_textual/tiposinteresreferenciaotrostiposfrecuentes/tipo_referencia_oficial_mercado_hipotecario.html)
- **Metodología del IRPH:** media simple de los tipos medios ponderados de préstamos de más de 3 años, a partir del estado 2172. Entran las entidades con más de 10 operaciones al mes. Se publica "en torno al día 19 de cada mes". El BdE emite una nota de prensa el primer día hábil de cada mes. Nota actualizada a 19-oct-2026. — [Nota del BdE sobre índices](https://www.bde.es/webbe/es/estadisticas/compartido/docs/Nota_indices_web_BE.pdf)

### Inferences
- El IRPH (3,189 %) está ya por debajo del Euríbor de septiembre (3,247 %). Para hipotecas IRPH con diferencial bajo, el coste es comparable al de las referenciadas a Euríbor.

### Gaps
- No se obtuvieron los últimos valores del rendimiento de deuda pública de 2 a 6 años.
- No se pudo verificar el mes exacto del tipo zona euro del 3,600 %.

## Tipos medios de las nuevas hipotecas: BdE/BCE (MIR) e INE (H), incluida Madrid

### Takeaway
- **BdE (MIR), agosto 2026:** las nuevas operaciones de crédito a vivienda tienen un **TEDR del 3,04 %** y una **TAE del 3,10 %**, en subida desde el 2,85-2,89 % de mayo a julio.
- **INE, agosto 2026:** 33.841 hipotecas sobre vivienda (+2,3 % interanual), importe medio de 181.285 €, tipo medio del 3,08 %, plazo de 26 años y 64,1 % a tipo fijo.
- **Madrid:** solo se publicó la variación del número de hipotecas (−5,8 % interanual).

### Cited Findings
- **BdE, tabla 19.4 del Boletín Estadístico, TEDR nuevas operaciones de crédito a la vivienda** (serie DN_1TI2T0002): may-2026 2,8534; jun 2,8867; jul 2,8926; **ago 3,0444**. — [be1904.csv](https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be1904.csv)
- **BdE, tabla 19.6, TAE de crédito a la vivienda** (serie DN_1TI2T0082): may 2,9218; jun 2,9385; jul 2,9431; **ago 3,0960**. — [be1906.csv](https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be1906.csv)
- El agregador hipotecas.me coincide: 3,04 % en agosto 2026, 2,89 % en julio 2026 y 2,68 % en agosto 2025. — [hipotecas.me](https://www.hipotecas.me/informe-mensual/septiembre-2026)
- **INE, Estadística de Hipotecas (H), agosto 2026** (publicada el 26-oct-2026):
  - 33.841 hipotecas sobre viviendas (+2,3 % interanual).
  - Importe medio de 181.285 € (+7,7 %).
  - Tipo medio de 3,08 %.
  - Plazo medio de 26 años.
  - 64,1 % a tipo fijo y 35,9 % a variable. Tipo medio al inicio: 3,16 % el fijo y 2,95 % el variable.
  - Comunidad de Madrid: −5,8 % interanual en número de hipotecas sobre vivienda. La nota no da el número absoluto ni el importe para Madrid.
  - Datos provisionales.
  - — [INE nota de prensa H0826 (PDF)](https://www.ine.es/dyngs/Prensa/H0826.pdf)
- *Posible confusión:* un titular de Europa Press/Bolsamanía ("hipotecas suben un 7,5 % en agosto y el interés baja al 2,89 %") corresponde casi con seguridad a agosto de 2025, no de 2026. — [Bolsamanía](https://www.bolsamania.com/noticias_print/mercados/economia--las-hipotecas-sobre-viviendas-suben-un-75-en-agosto-y-el-interes-baja-al-289-el-menor-en-tres-anos--21087097.html)

### Inferences
- **Calendario INE:** la nota de septiembre de 2026 (H0926) debería salir a finales de noviembre de 2026, a juzgar por el patrón de publicación (agosto se publicó el 26-oct, con unos 2 meses de desfase).
- **Diferencia entre fuentes:** el tipo INE (3,08 %) y el TEDR del BdE (3,04 %) están alineados. El INE mide escrituras inscritas en los registros, con desfase respecto a la firma; el BdE mide operaciones nuevas firmadas en el mes.

### Gaps
- No se obtuvieron cifras absolutas de Madrid (número, importe medio, tipo). Hay que extraerlas del anexo de tablas por CCAA del INE o de la API (ver más abajo).
- La serie MIR del BCE para España (house purchase) no se pudo consultar porque la API del BCE estaba bloqueada.

## Cómo obtener los datos programáticamente (BdE, BCE, INE, EMMI)

### Takeaway
- **Banco de España:** API REST JSON oficial (BIEST/"srdatosapp") y CSV estáticos por tabla. Es la vía recomendada para el Euríbor oficial mensual, el IRPH y el tipo medio de nuevas hipotecas.
- **BCE:** API SDMX en data-api.ecb.europa.eu.
- **INE:** API Tempus3 en JSON.
- **EMMI:** sus datos de Euríbor no son de libre reutilización comercial. Para el Euríbor, mejor usar la serie oficial del BdE o del BCE.

### Cited Findings

#### API del Banco de España (oficial, publicada el 22-abr-2025)
- **Base:** `https://app.bde.es/bierest/resources/srdatosapp/`
- **Métodos:**
  - `favoritas`: último dato, con los campos `serie`, `descripcionCorta`, `codFrecuencia`, `decimales`, `simbolo`, `tendencia`, `fechaValor` y `valor`.
  - `listaSeries`: serie completa, con los campos adicionales `descripcion`, `informacion`, `fechaInicio`, `fechaFin`, `fechas` y `valores`.
- **Parámetros:**
  - `idioma`: `es` o `en`.
  - `series`: códigos separados por comas. `#` se escribe `%23` y `%` se escribe `%25`.
  - `rango`: un año (`2024`) o un código. Diaria: 3M, 12M o 36M. Mensual: 30M, 60M o MAX (por defecto 30M). Trimestral: 30M, 60M o MAX. Anual: 60M o MAX.
- **Fechas:** formato `yyyy-mm-ddThh:mm:ssZ`. Los meses se fechan el día 1.
- **Ejemplos oficiales:**
  - `https://app.bde.es/bierest/resources/srdatosapp/favoritas?idioma=en&series=D_1NBAF472`
  - `https://app.bde.es/bierest/resources/srdatosapp/listaSeries?idioma=en&series=D_1NBAF472&rango=30M`
- No documenta límites de uso ni términos específicos. Los ejemplos en Python y R son descargables.
- — [BdE: Statistics web service (API)](https://www.bde.es/webbe/en/estadisticas/recursos/api-estadisticas-bde.html); [anuncio de 22-abr-2025](https://www.bde.es/wbe/en/estadisticas/temas/tipos-de-interes/anuncios-tipos-de-interes/nuevo-servicio-web-api-para-la-descarga-de-datos-del-banco-de-espana.html)
- Existe un cliente en R (`tidyBdE::bde_series_api_latest` / `bde_series_api_load`), donde el código de API es el campo `Nombre_de_la_serie` del catálogo. — [tidyBdE](https://ropenspain.github.io/tidyBdE/reference/bde_series_api.html)

#### Códigos de serie BdE (verificados en las cabeceras de los CSV oficiales)

| Código (para `series=`) | Alias | Descripción | Frecuencia | Fuente CSV | URL de ejemplo |
|---|---|---|---|---|---|
| **D_1NBAF472** | BE_19_1.5 | Euríbor 12 meses, media mensual (tipo oficial del mercado hipotecario) | Mensual | [be1901.csv](https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be1901.csv) | `https://app.bde.es/bierest/resources/srdatosapp/favoritas?idioma=es&series=D_1NBAF472` |
| **D_1T9H0000** | BE_19_1.11 / BE_19_1.34 | Tipo medio de préstamos hipotecarios a más de 3 años para adquisición de vivienda libre, conjunto de entidades en España (= **IRPH Entidades**) | Mensual | be1901.csv | `https://app.bde.es/bierest/resources/srdatosapp/listaSeries?idioma=es&series=D_1T9H0000&rango=60M` |
| **DN_1TI2T0002** | BE_19_4.2 | TEDR nuevas operaciones, hogares e ISFLSH, crédito a la vivienda, tipo medio ponderado | Mensual | [be1904.csv](https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be1904.csv) | `https://app.bde.es/bierest/resources/srdatosapp/listaSeries?idioma=es&series=DN_1TI2T0002&rango=30M` |
| **DN_1TI2T0082** | BE_19_6.1 | TAE nuevas operaciones, hogares e ISFLSH, crédito a la vivienda | Mensual | [be1906.csv](https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be1906.csv) | `https://app.bde.es/bierest/resources/srdatosapp/favoritas?idioma=es&series=DN_1TI2T0082` |
| DN_1TI2T0003 / 0004 / 0005 / 0006 | BE_19_4.3 a 4.6 | TEDR crédito a la vivienda por periodo inicial de fijación: hasta 1 año, de 1 a 5, de 5 a 10 y más de 10 años | Mensual | be1904.csv | (igual, cambiando el código) |
| D_1T9H0010 | BE_19_1.12 | Tipo medio de préstamos de vivienda de 1 a 5 años, zona euro (oficial) | Mensual | be1901.csv | |
| D_1T9H0011 | BE_19_1.13 | IRS 5 años (oficial) | Mensual | be1901.csv | |
| D_1T9H0004 | BE_19_1.14 | Rendimiento interno de la deuda pública de 2 a 6 años (oficial) | Mensual | be1901.csv | |
| D_1NBAE972 / D_1NBAD972 / D_1NBAC972 / D_1NBAS972 | BE_19_1.4 a 1.1 | Euríbor 6M / 3M / 1M / 1 semana, medias mensuales | Mensual | be1901.csv | |
| D_1NBAF572 | BE_19_1.10 | Tipo de referencia €STR a 1 año | Mensual | be1901.csv | |
| D_1T9L0001 | BE_19_1.16 | Interés legal del dinero | | be1901.csv | |
| D_1T9H0000A / B / C | BE_19_1.35 a 1.37 | IRPH: importe agregado, número de operaciones y entidades contribuidoras | Mensual | be1901.csv | |
| D_DNBAF172 | TI_1_7.7 | Euríbor 12 meses, **diario** (no es la media oficial) | Diaria | [ti_1_7.csv](https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/ti_1_7.csv) | `...favoritas?idioma=es&series=D_DNBAF172` |

- **Formato de los CSV del BdE:** las cabeceras incluyen "CÓDIGO DE LA SERIE", "NÚMERO SECUENCIAL", "ALIAS DE LA SERIE", "DESCRIPCIÓN DE LA SERIE", "DESCRIPCIÓN DE LAS UNIDADES" y "FRECUENCIA". Las fechas mensuales tienen el formato `AGO 2026`, los valores vacíos son `_` y el separador decimal es el punto. — be1901.csv, be1904.csv, ti_1_7.csv (ver enlaces de la tabla)
- **Ficheros estáticos del capítulo 19 del Boletín Estadístico:**
  - Patrón CSV: `https://www.bde.es/webbe/es/estadisticas/compartido/datos/csv/be19NN.csv`. Patrón XLSX: `.../xlsx/be19NN.xlsx`.
  - Tabla 19.1: tipos oficiales, Euríbor e IRPH.
  - Tabla 19.4: TEDR de hogares.
  - Tabla 19.6: TAE.
  - Tabla 19.12: volúmenes de nuevas operaciones de hogares.
  - — [BdE capítulo 19](https://www.bde.es/webbe/en/estadisticas/otras-clasificaciones/publicaciones/boletin-estadistico/capitulo-19.html); [capítulo 1 de Tipos de interés (ti_1_1 a ti_1_7)](https://www.bde.es/webbe/en/estadisticas/otras-clasificaciones/publicaciones/tipos-interes/tipos-interes.html)
- **Fuente legal alternativa:** el BOE (resolución del BdE del primer día hábil para el Euríbor y similares; en torno al día 19-20 para el IRPH). Por ejemplo, [BOE-A-2026-20519](https://boe.es/boe/dias/2026/10/02/pdfs/BOE-A-2026-20519.pdf) y [BOE-A-2026-21866](https://boe.es/boe/dias/2026/10/20/pdfs/BOE-A-2026-21866.pdf). El BOE también publica la versión HTML en `https://www.boe.es/diario_boe/txt.php?id=BOE-A-AAAA-NNNNN`. — [ejemplo de BOE txt](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-9792)

#### API del BCE (SDMX)
- Las claves pedidas son el Euríbor 12M, media mensual (`FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA`) y la serie MIR de vivienda para España (`MIR.M.ES.B.A2C.A.R.A.2250.EUR.N`).
- Ninguna de las dos se pudo verificar en esta sesión, porque data-api.ecb.europa.eu devolvió 403 o robots_disallowed.
- Formato estándar, no verificado en vivo: `https://data-api.ecb.europa.eu/service/data/{flujo}/{clave}?format=csvdata&startPeriod=AAAA-MM` (también `format=jsondata`). Ver la sección Gaps.

#### API del INE (Tempus3)
- **Endpoint verificado** para la tabla 24456, "Porcentaje de hipotecas constituidas según tipo de interés, mensual, nacional":
  - JSON: `https://servicios.ine.es/wstempus/js/es/DATOS_TABLA/24456?tip=AM`
  - CSV (tabulador): `https://www.ine.es/jaxiT3/files/t/csv_bd/24456.csv`
  - CSV (punto y coma): `https://www.ine.es/jaxiT3/files/t/csv_bdsc/24456.csv`
  - PC-Axis: `https://www.ine.es/jaxiT3/files/t/px/24456.px`
  - HTML: `https://www.ine.es/jaxiT3/Tabla.htm?t=24456`
  - Operación INE: EA0010587 (H).
  - — [datos.gob.es, ficha 24456](https://datos.gob.es/es/catalogo/ea0010587-porcentaje-de-hipotecas-constituidas-segun-tipo-de-interes-mensual-nacional-estadistica-de-hipotecas-identificador-api-244561.ttl)
- **Otras fichas H en datos.gob.es:**
  - "Tipo de interés medio al inicio de las hipotecas constituidas" (identificador api 76315).
  - "Plazo medio de las hipotecas constituidas, anual, nacional" (identificador api 244611).
  - "Hipotecas constituidas sobre el total de fincas por entidad que concede el préstamo, mensual, CCAA" (138971).
  - "Hipotecas por naturaleza de la finca, meses, provincias, número e importe" (3232).
  - — [datos.gob.es, tipo medio 76315](https://datos.gob.es/en/catalogo/ea0010587-tipo-de-interes-medio-al-inicio-de-las-hipotecas-constituidas-hpt-identificador-api-76315.csv); [plazo medio 244611](https://datos.gob.es/en/catalogo/ea0010587-plazo-medio-de-las-hipotecas-constituidas-anual-nacional-estadistica-de-hipotecas-identificador-api-244611.csv); [3232](https://datos.gob.es/en/catalogo/ea0010587-hipotecas-por-naturaleza-de-la-finca-meses-provincias-y-numero-e-importe-hpt-identificador-api-3232.csv)

#### EMMI (administrador del Euríbor)
- **Datos diferidos gratuitos:** los últimos 25 días de datos con 24 horas de retraso son gratuitos, previo registro. Solo pueden usarse con fines no comerciales: "Delayed data obtained on The European Money Markets Institute's website may only be used for non-commercial purposes."
- **Datos en tiempo real:** usarlos con fines empresariales internos exige una suscripción.
- **Redistribución:** copiarlos o redistribuirlos con fines comerciales exige un contrato de licencia. Una suscripción estándar no permite redistribuir a terceros.
- **Contacto:** subscriptions@emmi-benchmarks.eu.
- — [EMMI FAQ suscripciones](https://www.emmi-benchmarks.eu/faq/subscriptions/); [tarifas 2026-2027](https://www.emmi-benchmarks.eu/globalassets/documents/pdf/subscriptions/d0167a-2026---2027-fee-schedule.pdf); [adenda "limited data sharing" 2026](https://www.emmi-benchmarks.eu/globalassets/documents/pdf/subscriptions/rates-plans/agreements/2026/addendum_addendum-for-limited-data-sharing.pdf)

### Inferences
- **Recomendación para el agente de datos:**
  1. **Diario:** consultar `favoritas` con `D_1NBAF472`, `D_1T9H0000`, `DN_1TI2T0002` y `DN_1TI2T0082`. Solo cambian una vez al mes, pero la consulta es barata.
  2. **Mensual:**
     - Días 1-3 de cada mes: Euríbor oficial del mes anterior.
     - Día ~20: IRPH.
     - Inicio de mes (unos 5 días después del cierre del mes M+1): TEDR/TAE del BdE.
     - Finales de mes: nota H del INE, con unos 2 meses de desfase.
  3. **Si falla la API:** descargar be1901.csv, be1904.csv y be1906.csv y parsear la cabecera de 6 filas.
- **Euríbor diario:** cualquier valor que se muestre debería venir del BdE (D_DNBAF172) o del BCE, citando la fuente. No se deben extraer datos de la web de EMMI para uso comercial.
- El ejemplo de la documentación del BdE (`D_1NBAF472`) es precisamente el Euríbor 12M mensual oficial.
- La serie mensual del Euríbor que publican el BdE y el BCE es una réplica de la de EMMI. Reutilizarla citando al BdE o al BCE es la práctica habitual, pero las condiciones de EMMI sobre productos comerciales podrían seguir aplicándose. Conviene revisarlo legalmente si el producto es comercial.

### Gaps
- **Claves SDMX del BCE sin verificar:** no se pudo comprobar en vivo que existan `FM.M.U2.EUR.RT.MM.EURIBOR1YD_.HSTA` y `MIR.M.ES.B.A2C.A.R.A.2250.EUR.N`, ni sus últimos valores. Hay que verificarlas en https://data.ecb.europa.eu desde un entorno con acceso. La clave MIR suele ser `MIR.M.ES.B.A2C.A.R.A.2250.EUR.N` (nuevas operaciones, vivienda, TEDR) y su análoga APRC (TAE) es `MIR.M.ES.B.A2C.A.C.A.2250.EUR.N`. Ambas proceden de conocimiento previo, no de una fuente verificada aquí.
- **INE:** no se verificaron los ids exactos de las tablas Tempus3 para tipo medio, plazo medio, importe medio y CCAA/Madrid. Los "identificador api" de datos.gob.es parecen ser el id de la tabla seguido de un dígito; 244561 corresponde a la tabla 24456. Es una inferencia. No se verificó la documentación oficial de Tempus3 (https://www.ine.es/dyngs/DAB/index.htm?cid=1099), que incluye parámetros como `nult=N` para los últimos N periodos.
- **API del BdE:** no hay documentación pública de límites de uso.
- **Desfase en be1901.csv:** no se pudieron leer las últimas filas porque el fichero es largo y la descarga se trunca. Los valores recientes de Euríbor e IRPH se tomaron del BOE.

## Licencias y condiciones de reutilización

### Takeaway
- **BdE e INE:** reutilización libre con cita de la fuente.
- **BOE:** documento público.
- **BCE:** reutilización permitida citando la fuente.
- **EMMI:** el dato del Euríbor está sujeto a licencia para cualquier uso comercial; su web solo da datos diferidos para uso no comercial.

### Cited Findings
- **EMMI:** los datos de su web son solo para uso no comercial. Para uso comercial o redistribución hace falta un contrato de licencia. — [EMMI FAQ](https://www.emmi-benchmarks.eu/faq/subscriptions/)
- **INE:** sus tablas están catalogadas en datos.gob.es (catálogo de datos abiertos de la AGE) con el editor "Instituto Nacional de Estadística". En la ficha consultada el campo de licencia aparecía vacío. — [datos.gob.es](https://datos.gob.es/es/catalogo/ea0010587-porcentaje-de-hipotecas-constituidas-segun-tipo-de-interes-mensual-nacional-estadistica-de-hipotecas-identificador-api-244561.ttl)
- **BdE:** la página de la API no establece términos de uso específicos; solo enlaza a "Aviso legal". — [BdE API](https://www.bde.es/webbe/en/estadisticas/recursos/api-estadisticas-bde.html)

### Inferences
- **INE y BdE:** como organismos públicos españoles, se acogen previsiblemente al régimen de la Ley 37/2007 de reutilización de la información del sector público, con reutilización gratuita citando la fuente y sin alterar el dato.
- **Riesgo legal:** el único riesgo relevante es el de EMMI sobre el Euríbor, sobre todo para mostrar valores diarios en un producto comercial.

### Gaps
- No se leyeron los textos literales del aviso legal del BdE, de las condiciones de reutilización del INE ni de la política de reutilización del BCE (ecb.europa.eu/home/disclaimer). Conviene citarlos textualmente en el informe final.

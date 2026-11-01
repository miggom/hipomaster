# Contexto del mercado hipotecario español (MVP)

Documento base para los agentes LangGraph de HipoMaster (analista de mercado, buscador de ofertas, gestor financiero y coordinador).
Los valores numéricos están **fechados a noviembre de 2026** (detalle y fuentes en [research/Hipotecas y subrogación Madrid 2026.md](research/Hipotecas%20y%20subrogaci%C3%B3n%20Madrid%202026.md)).
Región inicial del MVP: **Comunidad de Madrid**. Flujo prioritario: **subrogación / cambio de banco**. Los agentes deben refrescarlos desde las fuentes de la sección 8, nunca darlos por fijos.

## 1. Alcance del MVP

| Dimensión | Incluido | Excluido (fases futuras) |
|---|---|---|
| Comprador | Persona física, residente en España, nacionalidad española | No residentes, extranjeros residentes, empresas/autónomos como sociedad |
| Activos | Vivienda (habitual y segunda), locales, garajes, terrenos, naves, trasteros | Hoteles, edificios completos, suelo para promoción |
| Operación | **Subrogación / cambio de banco (prioritario)**, compra | Promotor, autopromoción compleja, hipoteca inversa |

## 2. Marco normativo clave

- **Ley 5/2019 (LCCI)**, reguladora de los contratos de crédito inmobiliario. Aplica a personas físicas con garantía sobre inmueble residencial **o** para adquirir terrenos/inmuebles construidos o por construir. Cubre por tanto locales, garajes, naves y trasteros comprados por personas físicas.
  - Entrega de **FEIN** (Ficha Europea de Información Normalizada) y **FiAE** (Ficha de Advertencias Estandarizadas) mínimo **10 días naturales** antes de firmar.
  - Visita obligatoria y gratuita al **notario** para asesoramiento (acta de transparencia).
  - Gastos: el banco paga notaría, registro, gestoría e AJD; el cliente paga **tasación** (y copias que pida).
  - **Comisiones de amortización anticipada** máximas:
    - Variable: 0,25 % los 3 primeros años **o** 0,15 % los 5 primeros; 0 % después.
    - Fija: 2 % los 10 primeros años y 1,5 % después.
    - Cambio de variable a fijo: 0,05 % los 3 primeros años (Ley 2/2023 lo ha eliminado en ciertos supuestos de vulnerabilidad; ver Código de Buenas Prácticas).
  - **Vencimiento anticipado**: impagos ≥ 3 % del capital o 12 cuotas (primera mitad del plazo); ≥ 7 % o 15 cuotas (segunda mitad).
  - Prohibidas las cláusulas suelo. Ventas vinculadas prohibidas; **ventas combinadas** (bonificaciones) permitidas si se ofrece también el precio sin bonificar.
- **Orden EHA/2899/2011** de transparencia y **Circular 5/2012 BdE**: obligación de calcular TAE y la evaluación de solvencia.
- **Circular 4/2017 BdE** y guías EBA: evaluación de solvencia; LTV y DTI como indicadores.
- **Real Decreto-ley 19/2022 y Código de Buenas Prácticas** (prorrogado): medidas para deudores vulnerables y cambio a fijo sin coste.
- **Ley 12/2023 de vivienda**: afecta a alquiler, relevante para inversores (rentabilidad), no al crédito directamente.
- **Fiscalidad de la compra** (paga el comprador):
  - Vivienda/locales/garajes **nuevos**: IVA 10 % (vivienda y garaje anexo hasta 2 plazas) o 21 % (locales, naves, terrenos urbanos, garaje/trastero no anexos) + AJD 0,5-1,5 % según CCAA.
  - **Segunda mano**: ITP 6-10 % según CCAA, con tipos reducidos para jóvenes, familias numerosas, discapacidad.
  - Terreno rústico: ITP; terreno urbano por promotor: IVA 21 %.
- **Ayudas públicas**: Aval ICO para jóvenes (< 35 años) y familias con menores, cubre hasta el 20 % del préstamo (LTV hasta 100 %) en vivienda habitual, con límites de ingresos y precio por CCAA. Hay programas autonómicos (Madrid "Mi Primera Vivienda", Galicia, Andalucía, etc.).

## 2b. Subrogación / cambio de banco (flujo prioritario)

- **Base legal**: Ley 2/1994 modificada por Ley 5/2019. No hace falta consentimiento del banco actual.
- **Proceso** (aprox. 40 días):
  1. El cliente pide oferta al banco nuevo (tasación a cargo del cliente, 250-450 €).
  2. El banco nuevo entrega **oferta vinculante** y la notifica al banco actual.
  3. El banco actual entrega certificado de deuda y tiene **15 días naturales** para igualar la oferta (**enervación**, vía novación). Aunque iguale, **decide el cliente**.
  4. Firma ante notario. Si el banco actual no acepta el pago, se deposita ante notario.
- **Qué puede cambiar**: solo tipo de interés y plazo. Más capital exige cancelación + hipoteca nueva.
- **Costes**: escritura **exenta de AJD**; aranceles notariales como documento sin cuantía y registro con 90 % de reducción. El banco nuevo suele pagar notaría, registro y gestoría. El cliente paga tasación y la **comisión del banco de origen**:
  - Variable firmada desde 16/06/2019: 0,15 % (3 años) o 0,25 % (5 años), luego 0 %.
  - Fija desde 16/06/2019: 2 % los 10 primeros años, 1,5 % después.
  - Paso de variable a fija: 0,05 % los 3 primeros años, luego 0 % (la exención total terminó el 31/12/2024).
  - Préstamos anteriores a 2019: según contrato (variable antiguo hasta 1 % o 0,5 %/0,25 %).
- **Alternativas** que el agente debe comparar siempre: novación con el mismo banco (exenta de AJD si solo cambia tipo o plazo), subrogación y cancelación + hipoteca nueva.
- **Entidades con subrogación documentada (nov-2026)**: Ibercaja, Sabadell, Kutxabank, ING, BBVA, Santander (LTV máx. 70 %), CaixaBank, Bankinter, Unicaja, MyInvestor (paga todos los gastos y la comisión de origen; exige 4.000 € netos/mes, 70.000 € pendientes y firma anterior a 10/2018). Openbank solo por cancelación + hipoteca nueva.
- **Ayudas**: Mi Primera Vivienda y aval ICO **no aplican** a subrogación.

## 2c. Comunidad de Madrid (fiscalidad y ayudas 2026)

- **ITP** segunda mano: 6 %. Vivienda habitual ≤ 250.000 €: bonificación del 10 % (5,4 % efectivo). Familia numerosa: 4 %. Menores de 35 en municipios < 2.500 habitantes: 100 %.
- **AJD** obra nueva (comprador particular): 0,4 % hasta 120.000 €, 0,5 % hasta 180.000 €, 0,75 % por encima. La AJD de la escritura de hipoteca la paga el banco.
- **Mi Primera Vivienda** (orden julio 2026): precio ≤ 425.000 €, edad ≤ 50 años (100 % de financiación < 40, 95 % de 40 a 45, 90 % de 45 a 50); sin límite de edad para familias con menores; 2 años de residencia en Madrid; sin otra vivienda. Entidades: CaixaBank, Santander, Ibercaja, ING, Unicaja, Kutxabank, Abanca, Sabadell, Eurocaja Rural (y anunciadas Bankinter, Cajamar, UCI).
- **Aval ICO jóvenes**: prorrogado hasta 31/12/2027; menores de 36 o familias con menores; cubre el tramo por encima del 80 %.
- Pendiente de verificar en BOCM: tipos de ITP/AJD y la tributación de locales, garajes, terrenos y naves.

## 3. Productos

| Tipo | Descripción | Notas para el agente |
|---|---|---|
| **Fijo** | Interés igual toda la vida del préstamo | Dominante en nuevas firmas (aprox. 60-75 % en 2025-26). Comparar TIN y TAE bonificada vs. sin bonificar |
| **Variable** | Euríbor 12M + diferencial, revisión anual o semestral | Diferenciales típicos 0,49 %-1 % bonificado |
| **Mixto** | Fijo 3-15 años y después Euríbor + diferencial | Comparar el escenario variable con varios euríbor |
| Hipoteca **joven / 100 %** | LTV hasta 90-100 % con aval ICO o autonómico | Solo vivienda habitual |
| Hipoteca **verde** | Mejor tipo para certificado energético A/B o reforma eficiente | Pedir certificado energético |
| **Cambio de casa / puente** | Compra antes de vender la actual | Riesgo mayor, perfil con patrimonio |
| **Préstamo con garantía hipotecaria** (no adquisición) | Liquidez sobre inmueble propio | Fuera del foco MVP, pero detectable |

Indicadores a calcular siempre: **TIN, TAE, TAE variable, cuota, coste total, intereses totales, coste de vinculaciones** (seguros, nómina, tarjetas, plan de pensiones) y **ahorro neto** de bonificar vs. no bonificar.

## 4. Condiciones típicas por sector (persona física residente)

Ver detalle estructurado en [`config/sectores.yaml`](../config/sectores.yaml).

| Sector | LTV máx. habitual | Plazo máx. | Diferencial / tipo frente a vivienda | Observaciones |
|---|---|---|---|---|
| Vivienda habitual | 80 % (90-100 % con aval ICO o Mi Primera Vivienda Madrid) | 30-40 años (edad + plazo ≤ 70-75) | Referencia | Mejor condición del mercado |
| Segunda vivienda | 60-70 % | 25-30 años | +0,2 a +0,5 pp | Menos bonificaciones |
| Local comercial | 50-70 % | 15-20 años | +0,5 a +1,5 pp | Valor de tasación muy dependiente de ubicación y rentas |
| Garaje | 50-70 % | 10-20 años | +0,5 a +1,5 pp | Importes bajos: a veces préstamo personal es más barato. Si va con la vivienda, mismas condiciones |
| Trastero | 50-60 % | 10-15 años | +0,5 a +1,5 pp | Mismo caso que garaje; pocas entidades financian solo trastero |
| Terreno urbano | 50-60 % | 10-20 años | +1 a +2 pp | Para construir vivienda habitual: hipoteca autopromotor (disposición por certificaciones) |
| Terreno rústico | 30-50 % | 10-15 años | +1,5 a +3 pp | Muchas entidades no lo financian |
| Nave industrial | 50-60 % | 15-20 años | +1 a +2 pp | Para persona física suele ser inversión: se analiza la renta del alquiler |

Regla común de solvencia:
- **Ratio de endeudamiento (DTI)**: cuotas totales ≤ 30-35 % de ingresos netos (hasta 40 % con ingresos altos).
- **Aportación propia**: (100 % − LTV) + **10-12 % de gastos e impuestos**.
- Tasación oficial (empresa homologada por BdE, Orden ECO/805/2003). El LTV se calcula sobre el **menor** entre precio de compra y tasación.
- Edad máxima al final del préstamo: 70-75 años.
- Antigüedad laboral: indefinido > 1-2 años; autónomos 2-3 años de declaraciones.

## 5. Tipos de interés de referencia

- **Euríbor 12M** (índice principal). Media mensual oficial BdE/BOE: **3,247 % sep-2026**, ~3,24 % oct-2026 (provisional). Sube desde 2,22 % en feb-2026; BCE subió en junio y septiembre 2026 (depósito 2,50 %).
- **IRPH Entidades**: 3,189 % (sep-2026).
- Tipo medio nuevas hipotecas vivienda (BdE, ago-2026): TEDR 3,04 %, TAE 3,10 %. INE ago-2026: tipo medio 3,08 %, 64 % a tipo fijo, plazo medio 26 años.
- Otros índices oficiales: IRPH Entidades, IRPH Cajas (residual), CECA, Mibor (residual), Euríbor a 6M.
- Ofertas de mercado nov-2026 en vivienda habitual (bonificado, según comparadores; confirmar en FEIN):
  - Fijo: 2,55-3,35 % TIN (Ibercaja, Banca March, Sabadell, Openbank, CaixaBank, BBVA, Santander). Sin vinculación: MyInvestor 3,40 % TIN / 3,61 % TAE.
  - Variable: Euríbor + 0,45-0,65 %.
  - Mixto: desde 1,80 % (Sabadell 3 años) y luego Euríbor + 0,70 %.
- **Estos números caducan**. El agente analista los debe refrescar en cada ejecución (ver sección 8).

## 6. Entidades principales

| Grupo | Entidades / marcas | Notas |
|---|---|---|
| Grandes bancos | CaixaBank (incl. imagin), Santander (incl. Openbank), BBVA, Banco Sabadell, Bankinter, Unicaja, Abanca, Kutxabank, Ibercaja, Cajamar | Mayor cuota; ofertas con vinculación |
| Banca online / neobancos | ING, Openbank, MyInvestor, EVO Banco, Pibank (préstamos limitados), imagin | Hipotecas con poca vinculación |
| Cajas rurales y cooperativas | Grupo Caja Rural, Laboral Kutxa, Caja de Ingenieros, Caixa Popular | Muy fuertes regionalmente; buenos en terrenos y naves en su zona |
| Otros | Deutsche Bank, Banca March, Targobank, UCI (vía intermediarios), Bankoa (Abanca), Cajasur (Kutxabank) | UCI y similares para perfiles no estándar |
| Intermediarios de crédito inmobiliario | Brókers (iAhorro, Hipotecas.com, Gibobs, Housfy, Trioteca, Kelisto como comparador) | Registrados en BdE o CCAA (Ley 5/2019) |

## 7. Documentación del cliente (para el agente gestor financiero)

- Identidad: DNI vigente, estado civil, régimen económico matrimonial.
- Ingresos asalariado: 3-6 últimas nóminas, contrato, vida laboral, IRPF último año.
- Autónomos: 2 últimas declaraciones IRPF, modelos 130/303/390, vida laboral.
- Patrimonio: extractos bancarios 6 meses, ahorros y otras propiedades (nota simple).
- Deudas: préstamos vigentes, CIRBE (Central de Información de Riesgos del BdE), tarjetas.
- Inmueble: contrato de arras/reserva, nota simple, tasación, certificado energético, IBI.
- Para locales/naves alquilados: contrato de arrendamiento, rentas cobradas.

Indicadores que debe devolver el agente: ingresos netos mensuales, DTI actual y futuro, LTV, ahorro disponible vs. aportación necesaria, estabilidad laboral, alertas (CIRBE con impagos, ASNEF, contratos temporales).

## 8. Fuentes de datos

| Fuente | Uso | Acceso |
|---|---|---|
| Banco de España (Estadísticas, tipos de referencia oficiales) | Euríbor oficial, IRPH, tipos medios de nuevas operaciones | Web / CSV / API BIE |
| EMMI | Euríbor diario | Web (datos diarios con retraso) |
| BCE Statistical Data Warehouse | Tipos MIR de préstamos vivienda | API SDMX gratuita |
| INE (Hipotecas, H) | Nº de hipotecas, importes, tipo medio, fijo vs. variable | API JSON INE |
| Notariado (Consejo General) y Registradores (Estadística Registral) | Compraventas e hipotecas por tipología e CCAA | Web / informes |
| Ministerio de Vivienda (MIVAU) | Precio vivienda libre, valor tasado | Web / Excel |
| Webs de cada entidad (FEIN / simuladores) | Ofertas reales y bonificaciones | Scraping respetando robots.txt y términos |
| Comparadores (Idealista Hipotecas, Kelisto, Helpmycash, iAhorro, Rankia) | Rankings y cambios de ofertas | Scraping o RSS; validar contra la fuente primaria |
| Portales inmobiliarios (Idealista, Fotocasa, Pisos.com, Habitaclia) | Precios de activos (para LTV y valor estimado) | API (Idealista tiene API con alta previa) |
| Catastro (Sede Electrónica) | Referencia catastral, superficie, uso | Servicios web gratuitos |
| BOE / Banco de España (normativa) | Cambios regulatorios | RSS BOE |

Reglas para el agente buscador:
1. Cada oferta guarda: entidad, producto, tipo, TIN, TAE, diferencial, bonificaciones y su coste, LTV máximo, plazo máximo, comisiones, sectores aceptados, fecha de captura y URL.
2. Se marca como **caducada** si tiene más de 7 días sin verificar.
3. La fuente primaria (web de la entidad) prevalece sobre comparadores.

## 9. Implicaciones para la arquitectura de agentes

| Tarea | Modelo sugerido | Motivo |
|---|---|---|
| Extracción de datos de nóminas/ofertas, normalización, resúmenes cortos, redacción de emails | Edge (Ollama en fitlet2: Qwen2.5 1.5-3B, Llama 3.2 3B, Phi-3.5 mini) | Tareas acotadas, baratas, datos sensibles quedan en local |
| Cálculos (cuota, TAE, DTI, LTV) | **Código Python determinista** (no LLM) | Exactitud y auditabilidad |
| Análisis de oferta vs. perfil, comparación de escenarios | VM: Qwen2.5 7B / 14B, DeepSeek | Razonamiento medio |
| Análisis normativo, casos complejos (terrenos, naves, ingresos mixtos), informe final al cliente, coordinación | Claude (upstream) | Razonamiento largo y alta calidad |

Recomendaciones: temperatura 0-0,2 para extracción y cálculo, 0,3-0,5 para redacción; datos personales (DNI, nóminas) procesados en local y anonimizados antes de enviarlos a modelos upstream (RGPD).

## 10. Próximos pasos

1. Validar este contexto y responder las preguntas abiertas.
2. Ajustar `config/sectores.yaml` (fuente única de parámetros de los agentes, versión inicial creada).
3. Implementar conectores: API BdE (series D_1NBAF472 Euríbor, D_1T9H0000 IRPH, DN_1TI2T0002 TEDR, DN_1TI2T0082 TAE), INE tabla 24456 y scraping de entidades (ver research). No usar datos de EMMI (solo uso no comercial).
4. Diseñar el grafo LangGraph (coordinador + 3 agentes) y el enrutado edge/upstream.

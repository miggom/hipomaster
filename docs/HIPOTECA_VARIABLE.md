# HipoMaster: hipoteca variable y mixta (v0.1)

Estado: propuesta. Fecha: 2026-11-10.
Amplía [ARQUITECTURA.md](ARQUITECTURA.md) §1, §3 y §8b. Código: [`src/hipomaster/calc/hipoteca.py`](../src/hipomaster/calc/hipoteca.py).

## 1. Alcance

- Modalidades: **fija, variable y mixta**, en compra y en subrogación.
- Índice: **Euríbor 12M** (oficial BdE, serie `D_1NBAF472`). IRPH Entidades (`D_1T9H0000`) solo para leer hipotecas antiguas del cliente, no para ofertas nuevas.
- Caso prioritario: hipoteca actual del cliente variable o mixta → ¿pasar a fija, mixta u otra variable?

## 2. Datos que hay que capturar

| Campo | Ejemplo | Origen |
|---|---|---|
| `modalidad` | variable / mixto | oferta o escritura |
| `tin_inicial` | 2,50 % | tramo fijo inicial (variable: 6-12 meses; mixta: 3-15 años) |
| `meses_tramo_fijo` | 12 / 60 | oferta |
| `indice` | euribor_12m | oferta |
| `diferencial` | +0,60 pp bonificado; +1,10 pp sin bonificar | oferta |
| `bonificaciones` | nómina -0,30, seguro vida -0,40 | oferta (se guarda el diferencial con y sin) |
| `periodo_revision_meses` | 12 (a veces 6) | oferta o escritura |
| `desfase_meses` | 2 (índice publicado 2 meses antes de la revisión) | escritura; 2 por defecto |
| `fecha_proxima_revision` | 2027-03 | escritura o recibo (solo hipoteca actual) |

Cambios en código:
- `Offer` (Buscador) y la hipoteca actual (Gestor) añaden estos campos. Diferencial nulo si la web no lo da: no se infiere.
- `MarketSnapshot` (Analista) añade `euribor_12m_ultimo`, `fecha`, serie de 24 meses y nota de expectativas con fuente.
- El Gestor extrae `fecha_proxima_revision` del último recibo: es clave para saber cuándo sube la cuota.

## 3. Cálculo (determinista)

- Sistema francés. En cada revisión se recalcula la cuota con el capital pendiente y el plazo restante.
- Tipo aplicado = índice (con desfase) + diferencial, **nunca negativo** (LCCI art. 21.4). Sin cláusula suelo.
- Funciones: `cuadro_amortizacion`, `comparar_escenarios`, `euribor_equilibrio`.
- **Euríbor de equilibrio**: Euríbor constante con el que la variable o mixta paga los mismos intereses que la fija. Es el número más fácil de explicar al cliente.
- TAE: la de la oferta se toma tal cual. Recalcularla (incluye gastos y seguros) queda para Fase 3.

## 4. Escenarios de Euríbor

Sin previsión fiable a 25 años, se muestran escenarios, no una predicción:

| Escenario | Senda | Para qué |
|---|---|---|
| plano | Euríbor actual constante | base, igual que la TAE variable regulada |
| bajista -1 pp | baja 1 pp en 24 meses | si el BCE recorta |
| alcista +1 pp | sube 1 pp en 24 meses | continuación del ciclo de 2026 |
| estrés +2 pp | actual + 2 pp desde la primera revisión | ¿puede pagar el cliente? |
| referencia 2 % | 2 % constante | nivel neutral; sustituir por la media real de la serie BdE |

Regla de solvencia: la cuota del escenario **estrés** no debe superar el 35-40 % de los ingresos netos. Si lo supera, la variable se marca "riesgo alto" aunque sea la más barata en el escenario plano.

Ejemplo (150.000 €, 25 años, variable 2,50 % el 1.er año y luego E+0,60; fija 2,85 %; Euríbor 3,24 %):

| | Cuota año 1 | Cuota tras revisión | Intereses totales |
|---|---|---|---|
| Fija 2,85 % | 699,67 € | 699,67 € | 59.901 € |
| Variable, plano | 672,93 € | 774,69 € | 81.185 € |
| Variable, bajista | 672,93 € | 742,17 € | 60.178 € |
| Variable, estrés | 672,93 € | 941,23 € | 129.150 € |

Euríbor de equilibrio: **2,28 %**. Con el Euríbor en 3,24 %, la variable solo compensa si el Euríbor medio baja por debajo de 2,28 % durante la vida del préstamo.

## 5. Cambios en agentes

- **Analista**: explica nivel y tendencia del Euríbor con fuente y fecha (BdE, BCE, previsiones citadas). No da un número de futuro como dato; usa los escenarios.
- **Buscador**: normaliza variable y mixta en el mismo esquema; separa diferencial bonificado y sin bonificar.
- **Gestor**: llama a la calculadora con los 5 escenarios para cada oferta y para la hipoteca actual. Puntuación: coste en escenario plano (peso 0,5), coste en estrés (0,3), coste de vinculaciones (0,2). Pesos ajustables.
- **Redactor**: tabla de escenarios + Euríbor de equilibrio + aviso de que la variable traslada el riesgo al cliente.
- Prompt del Analista, añadir: "Nunca afirmes qué valor tendrá el Euríbor. Presenta escenarios y la fuente de cada expectativa."

## 6. Subrogación con hipoteca actual variable

1. Gestor lee del recibo: diferencial, próxima revisión, capital pendiente, plazo restante.
2. Calculadora: coste de seguir (5 escenarios) frente a cada oferta (5 escenarios) + gastos de cambio.
3. Comisión de cambio a fija desde variable: límites de la LCCI (art. 23): 0,15 % los 3 primeros años y 0 % después. Verificar contra la escritura.
4. Informe: ahorro por escenario, punto de equilibrio en meses y Euríbor de equilibrio.

## 7. Pendiente

- Probar la API del BdE para la serie de 24 meses (ya en `config/bde_series.yaml`, rama `vshamp`).
- Recalcular la TAE con gastos (Fase 3).
- Validar los límites de comisión de la LCCI contra la ley vigente antes de mostrarlos al cliente.

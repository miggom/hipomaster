"""Calculadora determinista de hipotecas fija, variable y mixta.

Regla del proyecto: las cifras las calcula este código, nunca el LLM.
Sistema francés (cuota constante entre revisiones). Tipos en % anual nominal (TIN).

Supuestos (ver docs/HIPOTECA_VARIABLE.md):
- En cada revisión la cuota se recalcula con el capital pendiente y el plazo restante.
- El índice aplicado es el publicado `desfase_meses` antes de la revisión (por defecto 2).
- El tipo aplicable nunca es negativo (LCCI, art. 21.4). No hay cláusula suelo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

Senda = Callable[[int], float]  # mes (0 = firma) -> índice en % anual

TipoPrestamo = Literal["fijo", "variable", "mixto"]


@dataclass(frozen=True)
class Prestamo:
    capital: float
    plazo_meses: int
    modalidad: TipoPrestamo
    tin_inicial: float  # % anual del tramo fijo (todo el préstamo si es fijo)
    meses_tramo_fijo: int = 0  # variable: suele ser 6 o 12; mixto: 36-180
    diferencial: float = 0.0  # pp sobre el índice, ya con bonificaciones
    periodo_revision_meses: int = 12
    desfase_meses: int = 2

    def __post_init__(self) -> None:
        if self.capital <= 0 or self.plazo_meses <= 0:
            raise ValueError("capital y plazo deben ser positivos")
        if self.modalidad == "fijo":
            object.__setattr__(self, "meses_tramo_fijo", self.plazo_meses)
        elif self.meses_tramo_fijo >= self.plazo_meses:
            raise ValueError("el tramo fijo no puede cubrir todo el plazo")
        if self.periodo_revision_meses <= 0:
            raise ValueError("periodo de revisión inválido")


@dataclass
class Fila:
    mes: int  # 1..plazo
    tin: float
    cuota: float
    intereses: float
    amortizacion: float
    pendiente: float


@dataclass
class Resumen:
    cuota_inicial: float
    cuota_primera_revision: float | None
    cuota_maxima: float
    total_intereses: float
    total_pagado: float
    cuadro: list[Fila] = field(repr=False, default_factory=list)


def cuota_francesa(capital: float, tin_anual: float, meses: int) -> float:
    if meses <= 0:
        raise ValueError("meses debe ser positivo")
    i = tin_anual / 100 / 12
    if i == 0:
        return capital / meses
    return capital * i / (1 - (1 + i) ** -meses)


def _tin_en(p: Prestamo, mes0: int, senda: Senda | None) -> float:
    """TIN aplicable desde el mes `mes0` (0-index) del préstamo."""
    if mes0 < p.meses_tramo_fijo:
        return p.tin_inicial
    if senda is None:
        raise ValueError("préstamo variable/mixto sin senda de índice")
    indice = senda(max(0, mes0 - p.desfase_meses))
    return max(0.0, indice + p.diferencial)


def _es_revision(p: Prestamo, mes0: int) -> bool:
    if mes0 < p.meses_tramo_fijo:
        return mes0 == 0
    return (mes0 - p.meses_tramo_fijo) % p.periodo_revision_meses == 0


def cuadro_amortizacion(p: Prestamo, senda: Senda | None = None) -> Resumen:
    pendiente = p.capital
    filas: list[Fila] = []
    tin = cuota = 0.0
    cuota_rev: float | None = None
    for mes0 in range(p.plazo_meses):
        if _es_revision(p, mes0):
            tin = _tin_en(p, mes0, senda)
            cuota = cuota_francesa(pendiente, tin, p.plazo_meses - mes0)
            if mes0 == p.meses_tramo_fijo and mes0 > 0:
                cuota_rev = cuota
        intereses = pendiente * tin / 100 / 12
        amort = cuota - intereses
        if mes0 == p.plazo_meses - 1:
            amort = pendiente  # cierra redondeos
            cuota = amort + intereses
        pendiente -= amort
        filas.append(Fila(mes0 + 1, tin, cuota, intereses, amort, max(pendiente, 0.0)))
    total_int = sum(f.intereses for f in filas)
    return Resumen(
        cuota_inicial=filas[0].cuota,
        cuota_primera_revision=cuota_rev,
        cuota_maxima=max(f.cuota for f in filas),
        total_intereses=total_int,
        total_pagado=p.capital + total_int,
        cuadro=filas,
    )


# ---- Sendas de Euríbor (escenarios) ----

def plano(valor: float) -> Senda:
    return lambda _mes: valor


def rampa(desde: float, hasta: float, meses: int) -> Senda:
    """Va de `desde` a `hasta` linealmente en `meses` y se queda ahí."""
    def f(mes: int) -> float:
        if mes >= meses:
            return hasta
        return desde + (hasta - desde) * mes / meses
    return f


def escenarios_estandar(euribor_actual: float) -> dict[str, Senda]:
    """Escenarios por defecto del informe. Ver docs/HIPOTECA_VARIABLE.md §4."""
    return {
        "plano": plano(euribor_actual),
        "bajista_-1pp": rampa(euribor_actual, euribor_actual - 1, 24),
        "alcista_+1pp": rampa(euribor_actual, euribor_actual + 1, 24),
        "estres_+2pp": plano(euribor_actual + 2),
        "referencia_2pct": plano(2.0),  # nivel neutral orientativo; sustituir por media real de la serie BdE
    }


def comparar_escenarios(p: Prestamo, escenarios: dict[str, Senda]) -> dict[str, Resumen]:
    return {nombre: cuadro_amortizacion(p, s) for nombre, s in escenarios.items()}


def euribor_equilibrio(
    p_var: Prestamo, total_intereses_objetivo: float,
    lo: float = -1.0, hi: float = 10.0, tol: float = 1e-4,
) -> float | None:
    """Euríbor constante con el que el variable/mixto cuesta lo mismo en intereses
    que `total_intereses_objetivo` (p. ej. la oferta fija). None si no hay cruce."""
    def f(e: float) -> float:
        return cuadro_amortizacion(p_var, plano(e)).total_intereses - total_intereses_objetivo
    if f(lo) > 0 or f(hi) < 0:
        return None
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if f(mid) > 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2

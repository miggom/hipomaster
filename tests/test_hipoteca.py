import unittest

from hipomaster.calc.hipoteca import (
    Prestamo, cuadro_amortizacion, cuota_francesa, escenarios_estandar,
    comparar_escenarios, euribor_equilibrio, plano,
)


class TestCuota(unittest.TestCase):
    def test_cuota_conocida(self):
        # 150.000 € a 25 años al 3 %: 711,32 €/mes
        self.assertAlmostEqual(cuota_francesa(150_000, 3.0, 300), 711.32, places=2)

    def test_tipo_cero(self):
        self.assertAlmostEqual(cuota_francesa(120_000, 0.0, 240), 500.0)


class TestFija(unittest.TestCase):
    def test_amortiza_todo(self):
        r = cuadro_amortizacion(Prestamo(150_000, 300, "fijo", 3.0))
        self.assertAlmostEqual(r.cuadro[-1].pendiente, 0.0, places=6)
        self.assertAlmostEqual(r.cuota_inicial, r.cuota_maxima, places=6)
        self.assertIsNone(r.cuota_primera_revision)


class TestVariable(unittest.TestCase):
    def setUp(self):
        self.p = Prestamo(150_000, 300, "variable", tin_inicial=2.5,
                          meses_tramo_fijo=12, diferencial=0.6)

    def test_plano_igual_a_indice_mas_diferencial(self):
        r = cuadro_amortizacion(self.p, plano(3.24))
        self.assertAlmostEqual(r.cuadro[12].tin, 3.84, places=6)
        self.assertAlmostEqual(r.cuadro[-1].pendiente, 0.0, places=6)
        self.assertIsNotNone(r.cuota_primera_revision)

    def test_revision_anual(self):
        senda = lambda m: 3.0 if m < 20 else 4.0  # noqa: E731
        r = cuadro_amortizacion(self.p, senda)
        # mes0 12 usa índice de mes 10 (desfase 2) -> 3.0; mes0 24 usa mes 22 -> 4.0
        self.assertAlmostEqual(r.cuadro[12].tin, 3.6)
        self.assertAlmostEqual(r.cuadro[23].tin, 3.6)
        self.assertAlmostEqual(r.cuadro[24].tin, 4.6)

    def test_sin_intereses_negativos(self):
        r = cuadro_amortizacion(self.p, plano(-2.0))
        self.assertEqual(r.cuadro[12].tin, 0.0)

    def test_estres_mas_caro(self):
        res = comparar_escenarios(self.p, escenarios_estandar(3.24))
        self.assertGreater(res["estres_+2pp"].total_intereses, res["plano"].total_intereses)
        self.assertLess(res["bajista_-1pp"].total_intereses, res["plano"].total_intereses)

    def test_sin_senda_falla(self):
        with self.assertRaises(ValueError):
            cuadro_amortizacion(self.p)


class TestMixta(unittest.TestCase):
    def test_tramo_fijo_y_equilibrio(self):
        fija = cuadro_amortizacion(Prestamo(150_000, 300, "fijo", 2.85))
        mixta = Prestamo(150_000, 300, "mixto", tin_inicial=2.10,
                         meses_tramo_fijo=60, diferencial=0.70)
        r = cuadro_amortizacion(mixta, plano(3.0))
        self.assertTrue(all(f.tin == 2.10 for f in r.cuadro[:60]))
        e = euribor_equilibrio(mixta, fija.total_intereses)
        self.assertIsNotNone(e)
        r_eq = cuadro_amortizacion(mixta, plano(e))
        self.assertAlmostEqual(r_eq.total_intereses, fija.total_intereses, delta=5)


if __name__ == "__main__":
    unittest.main()

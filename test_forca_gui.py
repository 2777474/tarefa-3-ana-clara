import tempfile
import unittest
from pathlib import Path
import forca_gui


class ForcaFunctionsTest(unittest.TestCase):
    def test_carregar_palavras(self):
        with tempfile.TemporaryDirectory() as directory:
            arquivo = Path(directory) / "palavras.txt"
            arquivo.write_text("CAVALO\n\nmesa\n", encoding="utf-8")
            self.assertEqual(forca_gui.carregar_palavras(arquivo), ["CAVALO", "MESA"])

    def test_atualizar_display(self):
        self.assertEqual(
            forca_gui.atualizar_display("BANANA", {"B", "A"}),
            "B A _ A _ A",
        )

    def test_verificar_vitoria(self):
        self.assertTrue(forca_gui.verificar_vitoria("JAVA", {"J", "A", "V"}))
        self.assertFalse(forca_gui.verificar_vitoria("JAVA", {"J", "A"}))

    def test_normalizar_acento(self):
        self.assertEqual(forca_gui.normalizar("AVIÃO"), "AVIAO")


if __name__ == "__main__":
    unittest.main()

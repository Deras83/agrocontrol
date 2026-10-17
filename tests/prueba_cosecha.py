import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.lote import Lote
from models.cultivo import Cultivo
from models.plaguicida import Plaguicida
from models.aplicacion_campo import AplicacionCampo
from models.cosecha import Cosecha

lote = Lote(1, "Lote Norte", 2, "franco", 6.5, 45)
maiz = Cultivo("Maíz", "criollo", "cosecha")
cipermetrina = Plaguicida("Cipermetrina", 20, 7, costo_unitario=12, dosis_por_ha=0.5)

# Plaguicida aplicado el 1 de octubre, con 7 días de carencia
aplicacion = AplicacionCampo(1, lote, cipermetrina, 1.0, date(2026, 10, 1))
aplicacion.aplicar()

temprana = Cosecha(1, lote, 5, date(2026, 10, 5), maiz)
print(temprana)
print("¿Cumple carencia el 5 de octubre?", temprana.cumple_carencia([aplicacion]))

tardia = Cosecha(2, lote, 5, date(2026, 10, 10), maiz)
print("¿Cumple carencia el 10 de octubre?", tardia.cumple_carencia([aplicacion]))

try:
    Cosecha(3, lote, 0)
except ValueError as e:
    print("Error esperado:", e)

try:
    Cosecha(4, "no soy un lote", 5)
except TypeError as e:
    print("Error esperado:", e)
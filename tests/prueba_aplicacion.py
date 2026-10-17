import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.lote import Lote
from models.fertilizante import Fertilizante
from models.plaguicida import Plaguicida
from models.aplicacion_campo import AplicacionCampo

lote = Lote(1, "Lote Norte", 2, "franco", 6.5, 45)
urea = Fertilizante("Urea", 100, 46, 0, 0, costo_unitario=0.8, dosis_por_ha=50)
cipermetrina = Plaguicida("Cipermetrina", 20, 7, costo_unitario=12, dosis_por_ha=0.5)

# La dosis sale de la dosis recomendada del insumo para el área del lote
app1 = AplicacionCampo(1, lote, urea, urea.dosis_recomendada(lote.hectareas), date(2026, 10, 1))
print(app1)
app1.aplicar()
print(app1)
print("Inventario de urea:", urea.cantidad_disponible)
print("Dosis por ha:", app1.dosis_por_hectarea())

app2 = AplicacionCampo(2, lote, cipermetrina, 1.0, date(2026, 10, 1))
print("Fecha segura de cosecha:", app2.fecha_segura_cosecha())

try:
    app1.aplicar()   # ya aplicada
except ValueError as e:
    print("Error esperado:", e)

try:
    AplicacionCampo(3, lote, urea, 500).aplicar()   # supera el inventario
except ValueError as e:
    print("Error esperado:", e)

try:
    AplicacionCampo(4, "no soy un lote", urea, 5)
except TypeError as e:
    print("Error esperado:", e)
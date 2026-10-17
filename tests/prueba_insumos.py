import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from models.fertilizante import Fertilizante
from models.plaguicida import Plaguicida
from models.semilla import Semilla

insumos = [
    Fertilizante("Urea", 100, 46, 0, 0, costo_unitario=0.8, dosis_por_ha=50),
    Plaguicida("Cipermetrina", 20, 7, costo_unitario=12, dosis_por_ha=0.5),
    Semilla("Maíz criollo", 40, 80, costo_unitario=3, dosis_por_ha=20),
]

# Polimorfismo: la misma llamada, comportamiento distinto en cada clase
for insumo in insumos:
    print(insumo)
    print("  Para 2 ha:", insumo.dosis_recomendada(2), insumo.unidad_medida)

insumos[0].usar(30)
print("Urea después de usar 30:", insumos[0].cantidad_disponible)

try:
    insumos[0].usar(500)
except ValueError as e:
    print("Error esperado:", e)

try:
    Fertilizante("Malo", 10, 80, 30, 10)   # suma > 100
except ValueError as e:
    print("Error esperado:", e)
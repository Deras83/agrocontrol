import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from models.maquinaria import Maquinaria

tractor = Maquinaria(1, "Tractor John Deere", vida_util_horas=5000, intervalo_mantenimiento=250)
print(tractor)

tractor.registrar_uso(210)
print(tractor)            # próximo (210 >= 80% de 250)

tractor.registrar_uso(60)
print(tractor)            # vencido (270 >= 250)

tractor.registrar_mantenimiento()
print(tractor)            # al día otra vez

try:
    tractor.registrar_uso(-5)
except ValueError as e:
    print("Error esperado:", e)
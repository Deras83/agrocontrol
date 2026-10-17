import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.lote import Lote
from models.maquinaria import Maquinaria
from models.registro_campo import RegistroCampo

lote = Lote(1, "Lote Norte", 2, "franco", 6.5, 45)
tractor = Maquinaria(1, "Tractor John Deere")

riego = RegistroCampo(1, lote, "riego", "Riego por goteo", date(2026, 10, 3))
print(riego)

arado = RegistroCampo(2, lote, "preparacion_suelo", "Arado previo a siembra",
                      date(2026, 10, 4), horas_trabajadas=3, maquinaria=tractor)
print(arado)
arado.completar()
print(arado)
print("Horas del tractor:", tractor.horas_uso)

try:
    arado.completar()   # ya completado
except ValueError as e:
    print("Error esperado:", e)

try:
    RegistroCampo(3, lote, "baile")   # actividad inexistente
except ValueError as e:
    print("Error esperado:", e)

try:
    RegistroCampo(4, lote, "riego", maquinaria=tractor)   # maquinaria sin horas
except ValueError as e:
    print("Error esperado:", e)

try:
    RegistroCampo(5, "no soy un lote", "riego")
except TypeError as e:
    print("Error esperado:", e)
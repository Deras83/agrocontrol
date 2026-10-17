import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from models.cultivo import Cultivo

c = Cultivo("Maíz", "criollo")
print(c)

c.avanzar_dias(30)
c.avanzar_etapa()
print(c)
print("¿Listo para cosecha?", c.listo_para_cosecha())

try:
    Cultivo("Frijol", "rojo", "etapa_falsa")
except ValueError as e:
    print("Error esperado:", e)
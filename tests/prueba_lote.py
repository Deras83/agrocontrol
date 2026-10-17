import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from models.lote import Lote

lote = Lote(1, "Lote Norte", 2.5, "franco", 6.5, 45)
print(lote)

lote.actualizar_sensor(25)
print(lote)

try:
    Lote(2, "Malo", 1, "franco", 20)   # pH inválido
except ValueError as e:
    print("Error esperado:", e)
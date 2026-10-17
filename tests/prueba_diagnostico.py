import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.lote import Lote
from models.diagnostico import Diagnostico

lote = Lote(1, "Lote Norte", 2, "franco", 6.5, 25)

d1 = Diagnostico(1, lote, "riego", "Humedad baja para la etapa actual",
                 "Regar de inmediato", "alta")
print(d1)
print("¿Urgente?", d1.es_urgente())

# Así llegará la respuesta del sistema experto más adelante
respuesta = {"conclusion": "Posible deficiencia de nitrógeno",
             "recomendacion": "Aplicar fertilizante nitrogenado",
             "severidad": "media"}
d2 = Diagnostico.desde_respuesta(2, lote, "plaga_deficiencia", respuesta)
print(d2)
print("¿Urgente?", d2.es_urgente())

d3 = Diagnostico.desde_respuesta(3, lote, "siembra", {"conclusion": "Lote apto para maíz"})
print(d3)

try:
    Diagnostico(4, lote, "horoscopo", "algo")
except ValueError as e:
    print("Error esperado:", e)

try:
    Diagnostico(5, lote, "riego", "   ")
except ValueError as e:
    print("Error esperado:", e)

try:
    Diagnostico(6, "no soy un lote", "riego", "algo")
except TypeError as e:
    print("Error esperado:", e)
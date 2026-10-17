import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.finca import Finca
from models.lote import Lote
from models.cultivo import Cultivo
from models.fertilizante import Fertilizante
from models.semilla import Semilla
from models.maquinaria import Maquinaria
from models.aplicacion_campo import AplicacionCampo
from models.cosecha import Cosecha

finca = Finca("La Esperanza", "Zona central")

lote1 = Lote(1, "Lote Norte", 2, "franco", 6.5, 25)
lote2 = Lote(2, "Lote Sur", 3, "arcilloso", 6.0, 60)
finca.agregar_lote(lote1)
finca.agregar_lote(lote2)

urea = Fertilizante("Urea", 100, 46, 0, 0, costo_unitario=0.8, dosis_por_ha=50)
semilla = Semilla("Maíz criollo", 5, 80, costo_unitario=3, dosis_por_ha=20)
finca.agregar_insumo(urea)
finca.agregar_insumo(semilla)

tractor = Maquinaria(1, "Tractor John Deere")
tractor.registrar_uso(210)
finca.agregar_maquinaria(tractor)

finca.sembrar(lote1, Cultivo("Maíz", "criollo"))
print("Cultivo del lote 1:", finca.cultivo_de(lote1))

aplicacion = AplicacionCampo(1, lote1, urea, 100, date(2026, 10, 1))
aplicacion.aplicar()
finca.agregar_aplicacion(aplicacion)
finca.agregar_cosecha(Cosecha(1, lote2, 6, date(2026, 10, 10)))

print(finca)
print("Insumos bajos:", [i.nombre for i in finca.insumos_bajos(10)])
print("Mantenimiento pendiente:", [m.nombre for m in finca.maquinaria_con_mantenimiento_pendiente()])
print("Costo de aplicaciones:", finca.costo_aplicaciones())
print("Lote 2 encontrado:", finca.buscar_lote(2).nombre)

try:
    finca.agregar_lote(Lote(1, "Duplicado", 1, "franco", 6, 50))
except ValueError as e:
    print("Error esperado:", e)

ajeno = Lote(9, "Lote Ajeno", 1, "franco", 6, 50)
try:
    finca.agregar_aplicacion(AplicacionCampo(2, ajeno, urea, 5))
except ValueError as e:
    print("Error esperado:", e)

try:
    finca.sembrar(lote1, Cultivo("Frijol", "rojo"))
except ValueError as e:
    print("Error esperado:", e)

try:
    finca.agregar_lote("no soy un lote")
except TypeError as e:
    print("Error esperado:", e)
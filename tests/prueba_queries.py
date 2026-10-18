import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_connection import obtener_conexion, crear_tablas
from database import queries as q
from models.lote import Lote
from models.cultivo import Cultivo
from models.insumo import Insumo
from models.fertilizante import Fertilizante
from models.plaguicida import Plaguicida
from models.semilla import Semilla
from models.maquinaria import Maquinaria

conn = obtener_conexion(":memory:")
crear_tablas(conn)

print("--- Lotes ---")
q.guardar_lote(conn, Lote(1, "Lote Norte", 2, "franco", 6.5, 25))
q.guardar_lote(conn, Lote(2, "Lote Sur", 3, "arcilloso", 6.0, 60))
print("Siguiente id:", q.siguiente_id(conn, "lotes"))
for lote in q.listar_lotes(conn):
    print(lote)

lote = q.obtener_lote(conn, 1)
lote.actualizar_sensor(55)
q.guardar_lote(conn, lote)               # mismo id: actualiza
print("Después de actualizar:", q.obtener_lote(conn, 1))

print("--- Cultivo ---")
q.guardar_cultivo(conn, 1, Cultivo("Maíz", "criollo", "vegetativa", 30))
print(q.cargar_cultivo(conn, 1))

print("--- Insumos (polimorfismo) ---")
q.guardar_insumo(conn, Fertilizante("Urea", 100, 46, 0, 0, costo_unitario=0.8, dosis_por_ha=50))
q.guardar_insumo(conn, Plaguicida("Cipermetrina", 20, 7, costo_unitario=12, dosis_por_ha=0.5))
q.guardar_insumo(conn, Semilla("Maíz criollo", 40, 80, costo_unitario=3, dosis_por_ha=20))
for insumo in q.listar_insumos(conn):
    print(type(insumo).__name__, "->", insumo.descripcion())

urea = q.obtener_insumo(conn, "Urea")
urea.usar(30)
q.guardar_insumo(conn, urea)
print("Stock de urea guardado:", q.obtener_insumo(conn, "Urea").cantidad_disponible)

# La unidad de medida debe conservarse al guardar y cargar
q.guardar_insumo(conn, Fertilizante("Compost", 10, 5, 2, 2, unidad_medida="sacos"))
print("Unidad de Compost al cargar:", q.obtener_insumo(conn, "Compost").unidad_medida)

print("--- Maquinaria ---")
tractor = Maquinaria(1, "Tractor John Deere")
tractor.registrar_uso(270)
tractor.registrar_mantenimiento()
tractor.registrar_uso(100)
q.guardar_maquinaria(conn, tractor)
print(q.obtener_maquinaria(conn, 1))

print("--- Eliminar ---")
q.eliminar_lote(conn, 1)
print("Lotes restantes:", len(q.listar_lotes(conn)))
print("Cultivo del lote borrado:", q.cargar_cultivo(conn, 1))
q.eliminar_insumo(conn, "Compost")
print("Insumos restantes:", len(q.listar_insumos(conn)))

print("--- Errores ---")
try:
    q.guardar_insumo(conn, Insumo("Genérico", "otro", 10, "kg"))
except ValueError as e:
    print("Error esperado:", e)

try:
    q.guardar_lote(conn, Lote(7, "Lote Sur", 1, "franco", 6, 50))   # nombre repetido
except sqlite3.IntegrityError as e:
    print("Error esperado:", e)

try:
    q.siguiente_id(conn, "inventario_insumos")   # tabla no permitida
except ValueError as e:
    print("Error esperado:", e)

conn.close()
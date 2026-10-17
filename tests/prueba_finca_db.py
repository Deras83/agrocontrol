import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_connection import obtener_conexion, crear_tablas
from database import queries as q
from models.finca import Finca
from models.lote import Lote
from models.cultivo import Cultivo
from models.fertilizante import Fertilizante
from models.plaguicida import Plaguicida
from models.maquinaria import Maquinaria
from models.aplicacion_campo import AplicacionCampo
from models.cosecha import Cosecha
from models.registro_campo import RegistroCampo
from models.diagnostico import Diagnostico

# --- Se arma una finca completa en memoria ---
finca = Finca("La Esperanza", "Zona central")
lote1 = Lote(1, "Lote Norte", 2, "franco", 6.5, 25)
lote2 = Lote(2, "Lote Sur", 3, "arcilloso", 6.0, 60)
finca.agregar_lote(lote1)
finca.agregar_lote(lote2)

urea = Fertilizante("Urea", 100, 46, 0, 0, costo_unitario=0.8, dosis_por_ha=50)
cipermetrina = Plaguicida("Cipermetrina", 20, 7, costo_unitario=12, dosis_por_ha=0.5)
finca.agregar_insumo(urea)
finca.agregar_insumo(cipermetrina)

tractor = Maquinaria(1, "Tractor John Deere")
finca.agregar_maquinaria(tractor)
finca.sembrar(lote1, Cultivo("Maíz", "criollo", "vegetativa", 30))

app1 = AplicacionCampo(1, lote1, urea, 100, date(2026, 10, 1))
app1.aplicar()
finca.agregar_aplicacion(app1)
finca.agregar_aplicacion(AplicacionCampo(2, lote2, cipermetrina, 1.5, date(2026, 10, 2)))
finca.agregar_cosecha(Cosecha(1, lote2, 6, date(2026, 10, 10)))

registro = RegistroCampo(1, lote1, "preparacion_suelo", "Arado", date(2026, 10, 4),
                         horas_trabajadas=3, maquinaria=tractor)
registro.completar()
finca.agregar_registro(registro)
finca.agregar_diagnostico(Diagnostico(1, lote1, "riego", "Humedad baja",
                                      "Regar de inmediato", "alta"))

# --- Se guarda y se vuelve a cargar en una finca nueva ---
conn = obtener_conexion(":memory:")
crear_tablas(conn)
q.guardar_finca(conn, finca)
q.guardar_finca(conn, finca)          # guardar dos veces no debe dar error
nueva = q.cargar_finca(conn, "La Esperanza", "Zona central")

print(nueva)
print("--- Detalle ---")
print(nueva.cultivo_de(nueva.buscar_lote(1)))
for aplicacion in nueva.aplicaciones:
    print(aplicacion)
print(nueva.cosechas[0])
print(nueva.registros[0])
print(nueva.diagnosticos[0])
print("Stock de urea:", nueva.buscar_insumo("Urea").cantidad_disponible)
print("Costo de aplicaciones:", nueva.costo_aplicaciones())

print("--- Comprobaciones ---")
print("Misma área total:", nueva.area_total() == finca.area_total())
print("Misma cosecha:", nueva.toneladas_cosechadas() == finca.toneladas_cosechadas())
print("Mismo objeto Lote compartido:",
      nueva.aplicaciones[0].lote is nueva.buscar_lote(1))

print("--- Error ---")
try:
    q.guardar_aplicacion(conn, AplicacionCampo(9, lote1, Fertilizante("Fantasma", 5, 10, 0, 0), 1))
except ValueError as e:
    print("Error esperado:", e)

conn.close()
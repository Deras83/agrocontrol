import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database.db_connection import obtener_conexion, crear_tablas

conn = obtener_conexion(":memory:")
crear_tablas(conn)

conn.executemany(
    "INSERT INTO lotes (nombre, area_ha, tipo_suelo, ph, humedad_actual) VALUES (?, ?, ?, ?, ?)",
    [("Lote Norte", 2, "franco", 6.5, 25), ("Lote Sur", 3, "arcilloso", 6.0, 60)],
)
conn.executemany(
    "INSERT INTO inventario_insumos (nombre_producto, tipo, stock, unidad, costo_unitario, dosis_por_ha) "
    "VALUES (?, ?, ?, ?, ?, ?)",
    [("Urea", "fertilizante", 100, "kg", 0.8, 50), ("Cipermetrina", "plaguicida", 20, "l", 12, 0.5)],
)
conn.executemany(
    "INSERT INTO aplicaciones_campo (lote_id, insumo_id, dosis, fecha, aplicada) VALUES (?, ?, ?, ?, ?)",
    [(1, 1, 100, "2026-10-01", 1), (2, 2, 1.5, "2026-10-02", 0)],
)
conn.executemany(
    "INSERT INTO historial_cosechas (lote_id, toneladas_recolectadas, fecha_cosecha) VALUES (?, ?, ?)",
    [(1, 4.0, "2026-10-10"), (1, 1.0, "2026-10-20"), (2, 6.0, "2026-10-12")],
)
conn.commit()

print("--- Aplicaciones (JOIN) ---")
filas = conn.execute(
    "SELECT l.nombre AS lote, i.nombre_producto AS insumo, a.dosis, a.fecha "
    "FROM aplicaciones_campo a "
    "JOIN lotes l ON l.id = a.lote_id "
    "JOIN inventario_insumos i ON i.id = a.insumo_id "
    "ORDER BY a.fecha"
).fetchall()
for f in filas:
    print(f"{f['lote']} | {f['insumo']} | {f['dosis']} | {f['fecha']}")

print("--- Cosechas por lote (GROUP BY) ---")
filas = conn.execute(
    "SELECT l.nombre, SUM(c.toneladas_recolectadas) AS total, "
    "ROUND(SUM(c.toneladas_recolectadas) / l.area_ha, 2) AS rendimiento "
    "FROM historial_cosechas c JOIN lotes l ON l.id = c.lote_id "
    "GROUP BY l.id ORDER BY l.nombre"
).fetchall()
for f in filas:
    print(f"{f['nombre']}: {f['total']} t, {f['rendimiento']} t/ha")

print("--- Restricciones ---")
intentos = [
    ("pH fuera de rango",
     "INSERT INTO lotes (nombre, area_ha, tipo_suelo, ph) VALUES ('Malo', 1, 'franco', 20)"),
    ("lote inexistente",
     "INSERT INTO aplicaciones_campo (lote_id, insumo_id, dosis, fecha) VALUES (99, 1, 5, '2026-10-01')"),
    ("nombre de lote repetido",
     "INSERT INTO lotes (nombre, area_ha, tipo_suelo, ph) VALUES ('Lote Norte', 1, 'franco', 6)"),
]
for descripcion, sql in intentos:
    try:
        conn.execute(sql)
    except sqlite3.IntegrityError as e:
        print(f"Error esperado ({descripcion}):", e)

conn.close()
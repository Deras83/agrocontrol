"""seed.py - Llena agrocontrol.db con datos de EJEMPLO (no verificados).
Uso (desde la raiz del proyecto):  python seed.py
Hace respaldo, borra todo, inserta en una transaccion y verifica."""
import shutil
from datetime import date, timedelta

from config import DB_PATH
from database import queries as q
from database.db_connection import obtener_conexion, crear_tablas
from services import analytics

HOY = date.today()
def f(dias):  # fecha relativa a hoy (dias negativos = futuro)
    return (HOY - timedelta(days=dias)).isoformat()

# --- Lotes: (id, nombre, area_ha, suelo, ph, humedad) ---
LOTES = [(1, "Lote La Ceiba", 3.0, "franco", 6.5, 66), (2, "Lote El Roble", 0.8, "arenoso", 6.3, 24),
         (3, "Parcela Norte", 2.0, "limoso", 5.9, 47), (4, "Parcela Sur", 4.5, "arcilloso", 6.1, 62),
         (5, "Lote Las Palmas", 0.8, "franco", 6.4, 56), (6, "Lote El Mirador", 2.5, "franco", 6.6, 45),
         (7, "Lote Los Pinos", 1.0, "franco", 6.3, 58)]  # Los Pinos: libre, sin cultivo
NOM = {l[0]: l[1] for l in LOTES}

# --- Cultivos: (lote_id, cultivo, variedad, dias desde siembra); la etapa sale de los dias ---
CULTIVOS = [(1, "maiz", "H-59", 35), (2, "frijol", "Rojo de seda", 55), (3, "papa", "Granola", 80),
            (4, "arroz", "Criollo", 30), (5, "tomate", "Río Grande", 85), (6, "maiz", "Criollo amarillo", 120)]
ETAPAS = ((15, "germinacion"), (50, "vegetativa"), (70, "floracion"), (100, "fructificacion"))
def etapa(dias):
    return next((e for limite, e in ETAPAS if dias < limite), "cosecha")

# Conocimiento de Prolog: cultivo -> (ph min, ph max, suelos aptos)
PROLOG = {"maiz": (5.8, 7.0, {"franco", "arcilloso"}), "frijol": (6.0, 7.5, {"franco", "arenoso"}),
          "tomate": (6.0, 6.8, {"franco", "arenoso"}), "papa": (5.0, 6.5, {"franco", "arenoso", "limoso"}),
          "arroz": (5.5, 6.5, {"arcilloso", "limoso"})}

# --- Insumos: (nombre, tipo, stock inicial, unidad, costo, dosis_por_ha, n, p, k, carencia, germinacion) ---
INSUMOS = [
    ("Urea", "fertilizante", 2500, "kg", 0.85, 200, 46, 0, 0, None, None),
    ("DAP", "fertilizante", 2200, "kg", 1.15, 150, 18, 46, 0, None, None),
    ("Cloruro de potasio", "fertilizante", 1000, "kg", 0.95, 120, 0, 0, 60, None, None),
    ("Fórmula 15-15-15", "fertilizante", 1000, "kg", 1.00, 250, 15, 15, 15, None, None),
    ("Sulfato de amonio", "fertilizante", 800, "kg", 0.60, 180, 21, 0, 0, None, None),
    ("Insecticida cipermetrina", "plaguicida", 8, "l", 14.0, 0.5, None, None, None, 7, None),
    ("Fungicida mancozeb", "plaguicida", 20, "kg", 8.5, 2.0, None, None, None, 15, None),
    ("Azufre mojable", "plaguicida", 40, "kg", 4.2, 3.0, None, None, None, 5, None),
    ("Semilla de maíz", "semilla", 300, "kg", 3.2, 20, None, None, None, None, 92),
    ("Semilla de frijol", "semilla", 150, "kg", 2.5, 60, None, None, None, None, 90),
    ("Semilla de tomate", "semilla", 0.24, "kg", 380.0, 0.3, None, None, None, None, 88),
    ("Semilla de papa", "semilla", 5000, "kg", 0.65, 1500, None, None, None, None, 95),
    ("Semilla de arroz", "semilla", 800, "kg", 1.10, 100, None, None, None, None, 85)]

# --- Aplicaciones: (lote, insumo_id, dosis TOTAL, dias atras, aplicada) ---
APLICACIONES = [
    (6, 9, 50, 120, 1), (6, 2, 380, 119, 1), (6, 1, 520, 90, 1), (6, 3, 300, 40, 1),
    (5, 11, 0.24, 85, 1), (5, 2, 125, 84, 1), (5, 4, 200, 55, 1), (5, 1, 160, 40, 1), (5, 3, 96, 16, 1),
    (3, 12, 3000, 80, 1), (3, 4, 500, 78, 1), (3, 1, 400, 50, 1), (3, 3, 240, 10, 1),
    (2, 10, 48, 55, 1), (2, 2, 120, 54, 1), (2, 7, 1.6, 23, 1), (2, 8, 2.4, 12, 1), (2, 3, 100, 4, 1),
    (1, 9, 62, 35, 1), (1, 2, 450, 34, 1), (1, 1, 600, 12, 1), (1, 6, 1.5, 1, 1),
    (4, 13, 460, 30, 1), (4, 2, 700, 29, 1), (4, 5, 800, 10, 1),
    (1, 1, 580, -10, 0), (2, 4, 200, -7, 0), (2, 8, 2.4, -6, 0), (4, 4, 1100, -6, 0), (7, 12, 1500, -14, 0)]

# --- Cosechas: (lote, toneladas, dias atras) ---
COSECHAS = [(4, 18.0, 300), (6, 10.5, 270), (1, 13.8, 230), (3, 11.0, 190), (2, 13.6, 160),
            (6, 3.0, 140), (7, 16.0, 100), (1, 3.6, 60)]

# --- Bitacora: (lote, actividad, descripcion, dias atras, horas, completado) ---
REGISTROS = [
    (6, "cosecha", "Cosecha de frijol", 140, 8, 1), (6, "preparacion_suelo", "Rastreo y surcado del lote", 125, 6, 1),
    (6, "siembra", "Siembra de maíz criollo", 120, 7, 1), (6, "fertilizacion", "Aplicación de urea", 90, 3, 1),
    (6, "mantenimiento", "Limpieza de canales de riego", 20, 4, 1), (6, "cosecha", "Cosecha de maíz programada", -3, 8, 0),
    (5, "preparacion_suelo", "Preparación de camas para tomate", 90, 5, 1),
    (5, "siembra", "Trasplante de plántulas de tomate", 85, 6, 1), (5, "fertilizacion", "Aplicación de DAP", 84, 3, 1),
    (5, "fertilizacion", "Aplicación de cloruro de potasio", 16, 3, 1),
    (3, "preparacion_suelo", "Arado y surcado", 85, 8, 1), (3, "siembra", "Siembra de papa", 80, 9, 1),
    (3, "fertilizacion", "Aplicación de cloruro de potasio", 10, 4, 1), (3, "riego", "Riego por aspersión", 3, 3, 1),
    (2, "preparacion_suelo", "Limpieza y surcado", 60, 3, 1), (2, "siembra", "Siembra de frijol", 55, 4, 1),
    (2, "fumigacion", "Mancozeb contra oídio", 23, 2, 1), (2, "fumigacion", "Azufre mojable contra oídio", 12, 2, 1),
    (2, "riego", "Riego de emergencia por humedad baja", 8, 1.5, 1),
    (2, "fertilizacion", "Aplicación de cloruro de potasio", 4, 2, 1), (2, "riego", "Riego programado", -1, 3, 0),
    (1, "preparacion_suelo", "Rastreo del lote", 40, 6, 1), (1, "siembra", "Siembra de maíz H-59", 35, 7, 1),
    (1, "fertilizacion", "Aplicación de urea", 12, 4, 1), (1, "fumigacion", "Cipermetrina contra gusano cogollero", 1, 3, 1),
    (4, "preparacion_suelo", "Nivelación y diques para arroz", 35, 10, 1), (4, "siembra", "Siembra de arroz", 30, 8, 1),
    (4, "fertilizacion", "Aplicación de sulfato de amonio", 10, 6, 1), (7, "cosecha", "Cosecha de papa", 100, 6, 1)]

# --- Diagnosticos: textos copiados de rules/prolog_bridge.py (no se ejecuto swipl) ---
def apto(lote, cultivo, dias):
    return (lote, "siembra", f"{NOM[lote]} es apto para sembrar {cultivo}", "Puede proceder con la siembra.", "baja", dias)
DIAGNOSTICOS = [
    apto(5, "tomate", 87), apto(3, "papa", 82), apto(2, "frijol", 57), apto(1, "maiz", 36), apto(4, "arroz", 32),
    (2, "plaga_deficiencia", "Causa probable: oídio (enfermedad)",
     "Mejorar la ventilación, evitar el exceso de humedad y aplicar un fungicida autorizado.", "alta", 25),
    (5, "plaga_deficiencia", "Causa probable: deficiencia de potasio (deficiencia)", "Aplicar fertilizante potásico.", "media", 18),
    (3, "riego", "Humedad baja: regar de inmediato", "Fertilización sugerida en esta etapa: potasio.", "media", 12),
    (2, "riego", "Humedad baja con clima cálido: regar de inmediato y en abundancia",
     "Fertilización sugerida en esta etapa: fósforo y potasio.", "alta", 8),
    (7, "siembra", "Lote Los Pinos no es apto para arroz: el tipo de suelo no es apto para el cultivo",
     "Elige otro cultivo o mejora el suelo.", "media", 5),
    (1, "riego", "Humedad adecuada: mantener el riego actual", "Fertilización sugerida en esta etapa: nitrógeno.", "baja", 3),
    (1, "plaga_deficiencia", "Causa probable: gusano cogollero (plaga)",
     "Aplicar un control autorizado (mejor si es biológico) y respetar el periodo de carencia antes de cosechar.", "alta", 2)]

TABLAS = ["diagnosticos", "registros_campo", "aplicaciones_campo", "historial_cosechas",
          "cultivos", "maquinaria", "inventario_insumos", "lotes"]  # orden seguro de borrado


def main():
    shutil.copy(DB_PATH, DB_PATH.with_name(f"agrocontrol.db.{HOY}.bak"))  # 1. respaldo
    conn = obtener_conexion()
    crear_tablas(conn)
    aplic = sorted(APLICACIONES, key=lambda a: -a[3])  # orden cronologico
    consumo = {}
    for _, ins, dosis, _, hecha in aplic:
        if hecha:
            consumo[ins] = consumo.get(ins, 0) + dosis
    stock = {i: round(x[2] - consumo.get(i, 0), 2) for i, x in enumerate(INSUMOS, 1)}
    assert min(stock.values()) >= 0, "stock negativo"
    with conn:  # 2. todo en una transaccion
        for t in TABLAS:
            conn.execute(f"DELETE FROM {t}")
        conn.execute("DELETE FROM sqlite_sequence")
        conn.executemany("INSERT INTO lotes VALUES (?,?,?,?,?,?)", LOTES)
        conn.executemany("INSERT INTO inventario_insumos VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                         [(i, x[0], x[1], stock[i]) + x[3:] for i, x in enumerate(INSUMOS, 1)])
        conn.executemany("INSERT INTO cultivos VALUES (?,?,?,?,?,?)",
                         [(i, l, c, v, f(d), etapa(d)) for i, (l, c, v, d) in enumerate(CULTIVOS, 1)])
        conn.executemany("INSERT INTO aplicaciones_campo VALUES (?,?,?,?,?,?)",
                         [(i, l, ins, ds, f(d), h) for i, (l, ins, ds, d, h) in enumerate(aplic, 1)])
        conn.executemany("INSERT INTO historial_cosechas VALUES (?,?,?,?)",
                         [(i, l, t, f(d)) for i, (l, t, d) in enumerate(sorted(COSECHAS, key=lambda c: -c[2]), 1)])
        conn.executemany("INSERT INTO registros_campo VALUES (?,?,?,?,?,?,?,?)",
                         [(i, l, None, a, ds, f(d), h, ok) for i, (l, a, ds, d, h, ok) in
                          enumerate(sorted(REGISTROS, key=lambda r: -r[3]), 1)])
        conn.executemany("INSERT INTO diagnosticos VALUES (?,?,?,?,?,?,?)",
                         [(i, l, t, c, r, s, f(d)) for i, (l, t, c, r, s, d) in
                          enumerate(sorted(DIAGNOSTICOS, key=lambda x: -x[5]), 1)])
    verificar(conn)


def verificar(conn):
    print("FK errores:", conn.execute("PRAGMA foreign_key_check").fetchall())
    for t in TABLAS:
        print(f"  {t}: {conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]}")
    for lote, cultivo, _, _ in CULTIVOS:  # cada cultivo cumple pH y suelo de Prolog
        mn, mx, suelos = PROLOG[cultivo]
        assert mn <= LOTES[lote - 1][4] <= mx and LOTES[lote - 1][3] in suelos, f"{NOM[lote]}: no cumple"
    hum = [l[5] for l in LOTES]
    print("Humedad promedio:", round(sum(hum) / len(hum), 1), "| criticos:", sum(h < 30 for h in hum),
          "| atencion:", sum(30 <= h < 50 for h in hum), "| optimos:", sum(h >= 50 for h in hum))
    print("Toneladas por lote:", [tuple(r) for r in conn.execute(
        "SELECT l.nombre, ROUND(SUM(c.toneladas_recolectadas),1) FROM historial_cosechas c "
        "JOIN lotes l ON l.id = c.lote_id GROUP BY l.id")])
    print("Agotados:", [r[0] for r in conn.execute("SELECT nombre_producto FROM inventario_insumos WHERE stock = 0")])
    print("Stock bajo (<10):", [r[0] for r in conn.execute(
        "SELECT nombre_producto FROM inventario_insumos WHERE stock > 0 AND stock < 10")])
    print("Ultimos 4 diagnosticos:", [(r[0], r[1]) for r in conn.execute(
        "SELECT tipo, severidad FROM diagnosticos ORDER BY id DESC LIMIT 4")])
    finca = q.cargar_finca(conn, "Mi finca")  # la finca debe cargar sin errores
    print("Resumen (como /api/resumen):", analytics.resumen_finca(finca, 1.0))
    print("Listo. Datos de EJEMPLO, no verificados.")


if __name__ == "__main__":
    main()
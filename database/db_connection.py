"""Conexión a SQLite y creación de tablas (Programación Declarativa - SQL)."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DB_PATH

ESQUEMA = """
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    area_ha REAL NOT NULL CHECK (area_ha > 0),
    tipo_suelo TEXT NOT NULL
        CHECK (tipo_suelo IN ('arcilloso', 'franco', 'arenoso', 'limoso')),
    ph REAL NOT NULL CHECK (ph BETWEEN 0 AND 14),
    humedad_actual REAL NOT NULL DEFAULT 0 CHECK (humedad_actual BETWEEN 0 AND 100)
);

CREATE TABLE IF NOT EXISTS cultivos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lote_id INTEGER NOT NULL UNIQUE REFERENCES lotes(id) ON DELETE CASCADE,
    tipo_cultivo TEXT NOT NULL,
    variedad TEXT NOT NULL DEFAULT '',
    fecha_siembra TEXT NOT NULL,
    etapa TEXT NOT NULL DEFAULT 'germinacion'
        CHECK (etapa IN ('germinacion', 'vegetativa', 'floracion',
                         'fructificacion', 'cosecha'))
);

CREATE TABLE IF NOT EXISTS inventario_insumos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_producto TEXT NOT NULL UNIQUE,
    tipo TEXT NOT NULL CHECK (tipo IN ('fertilizante', 'plaguicida', 'semilla')),
    stock REAL NOT NULL CHECK (stock >= 0),
    unidad TEXT NOT NULL,
    costo_unitario REAL NOT NULL DEFAULT 0 CHECK (costo_unitario >= 0),
    dosis_por_ha REAL NOT NULL DEFAULT 0 CHECK (dosis_por_ha >= 0),
    n REAL, p REAL, k REAL,                       -- solo fertilizantes
    periodo_carencia_dias INTEGER,                -- solo plaguicidas
    tasa_germinacion REAL                         -- solo semillas
);

CREATE TABLE IF NOT EXISTS maquinaria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    vida_util_horas REAL NOT NULL CHECK (vida_util_horas > 0),
    intervalo_mantenimiento REAL NOT NULL CHECK (intervalo_mantenimiento > 0),
    horas_uso REAL NOT NULL DEFAULT 0 CHECK (horas_uso >= 0),
    horas_ultimo_mantenimiento REAL NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS aplicaciones_campo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lote_id INTEGER NOT NULL REFERENCES lotes(id),
    insumo_id INTEGER NOT NULL REFERENCES inventario_insumos(id),
    dosis REAL NOT NULL CHECK (dosis > 0),
    fecha TEXT NOT NULL,
    aplicada INTEGER NOT NULL DEFAULT 0 CHECK (aplicada IN (0, 1))
);

CREATE TABLE IF NOT EXISTS historial_cosechas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lote_id INTEGER NOT NULL REFERENCES lotes(id),
    toneladas_recolectadas REAL NOT NULL CHECK (toneladas_recolectadas > 0),
    fecha_cosecha TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS registros_campo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lote_id INTEGER NOT NULL REFERENCES lotes(id),
    maquinaria_id INTEGER REFERENCES maquinaria(id),
    actividad TEXT NOT NULL
        CHECK (actividad IN ('preparacion_suelo', 'siembra', 'riego', 'fertilizacion',
                             'fumigacion', 'mantenimiento', 'cosecha', 'otro')),
    descripcion TEXT NOT NULL DEFAULT '',
    fecha TEXT NOT NULL,
    horas_trabajadas REAL NOT NULL DEFAULT 0 CHECK (horas_trabajadas >= 0),
    completado INTEGER NOT NULL DEFAULT 0 CHECK (completado IN (0, 1))
);

CREATE TABLE IF NOT EXISTS diagnosticos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lote_id INTEGER NOT NULL REFERENCES lotes(id),
    tipo TEXT NOT NULL CHECK (tipo IN ('riego', 'plaga_deficiencia', 'siembra')),
    conclusion TEXT NOT NULL,
    recomendacion TEXT NOT NULL DEFAULT '',
    severidad TEXT NOT NULL DEFAULT 'baja' CHECK (severidad IN ('baja', 'media', 'alta')),
    fecha TEXT NOT NULL
);
"""


def obtener_conexion(ruta=DB_PATH):
    """Abre una conexión. Usa ':memory:' para una base temporal (pruebas)."""
    conexion = sqlite3.connect(ruta)
    conexion.execute("PRAGMA foreign_keys = ON")   # SQLite lo trae apagado
    conexion.row_factory = sqlite3.Row              # filas accesibles por nombre
    return conexion


def crear_tablas(conexion):
    conexion.executescript(ESQUEMA)
    conexion.commit()


if __name__ == "__main__":
    with obtener_conexion() as conn:
        crear_tablas(conn)
    print(f"Base de datos creada en: {DB_PATH}")
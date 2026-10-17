"""Consultas CRUD parametrizadas para AgroControl."""
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from database.db_connection import obtener_conexion as conectar
from models.lote import Lote
from models.cultivo import Cultivo
from models.insumo import Insumo
from models.fertilizante import Fertilizante
from models.plaguicida import Plaguicida
from models.semilla import Semilla
from models.maquinaria import Maquinaria
from models.finca import Finca
from models.aplicacion_campo import AplicacionCampo
from models.cosecha import Cosecha
from models.registro_campo import RegistroCampo
from models.diagnostico import Diagnostico

TABLAS_CON_ID = (
    "lotes",
    "maquinaria",
    "aplicaciones_campo",
    "historial_cosechas",
    "registros_campo",
    "diagnosticos",
)

# ----------------------------------------------------------------- LOTES
def guardar_lote(conn, lote):
    lote_id = getattr(lote, "id", getattr(lote, "_id", None))
    with conn:
        conn.execute(
            "INSERT INTO lotes (id, nombre, area_ha, tipo_suelo, ph, humedad_actual) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET nombre = excluded.nombre, "
            "area_ha = excluded.area_ha, tipo_suelo = excluded.tipo_suelo, "
            "ph = excluded.ph, humedad_actual = excluded.humedad_actual",
            (lote_id, lote.nombre, lote.hectareas, lote.tipo_suelo, lote.ph, lote.humedad_actual),
        )

def listar_lotes(conn):
    filas = conn.execute("SELECT * FROM lotes ORDER BY id").fetchall()
    return [
        Lote(f["id"], f["nombre"], f["area_ha"], f["tipo_suelo"], f["ph"], f["humedad_actual"])
        for f in filas
    ]

# ------------------------------------------------------------- INSUMOS
def guardar_insumo(conn, insumo):
    insumo_id = getattr(insumo, "id", getattr(insumo, "_id", None))
    tipo = getattr(insumo, "tipo", getattr(insumo, "_tipo", ""))
    
    n = getattr(insumo, "n", getattr(insumo, "_n", None))
    p = getattr(insumo, "p", getattr(insumo, "_p", None))
    k = getattr(insumo, "k", getattr(insumo, "_k", None))
    carencia = getattr(insumo, "periodo_carencia_dias", getattr(insumo, "_periodo_carencia_dias", None))
    germinacion = getattr(insumo, "tasa_germinacion", getattr(insumo, "_tasa_germinacion", None))

    with conn:
        cursor = conn.execute(
            "INSERT INTO inventario_insumos (id, nombre_producto, tipo, stock, unidad, costo_unitario, dosis_por_ha, n, p, k, periodo_carencia_dias, tasa_germinacion) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(nombre_producto) DO UPDATE SET stock = excluded.stock, "
            "unidad = excluded.unidad, costo_unitario = excluded.costo_unitario, "
            "dosis_por_ha = excluded.dosis_por_ha, n = excluded.n, p = excluded.p, k = excluded.k, "
            "periodo_carencia_dias = excluded.periodo_carencia_dias, tasa_germinacion = excluded.tasa_germinacion",
            (
                insumo_id,
                insumo.nombre,
                tipo,
                insumo.cantidad_disponible,
                insumo.unidad_medida,
                insumo.costo_unitario,
                insumo.dosis_por_ha,
                n, p, k, carencia, germinacion
            ),
        )
        # Asignar el ID generado/existente de la BD al objeto insumo si era None
        if insumo_id is None:
            fila = conn.execute("SELECT id FROM inventario_insumos WHERE nombre_producto = ?", (insumo.nombre,)).fetchone()
            if fila:
                new_id = fila["id"]
                if hasattr(insumo, "_id"):
                    insumo._id = new_id
                else:
                    insumo.id = new_id

def fila_a_insumo(fila):
    tipo = fila["tipo"]
    if tipo == "fertilizante":
        return Fertilizante(
            fila["nombre_producto"], fila["stock"],
            fila["n"] or 0, fila["p"] or 0, fila["k"] or 0,
            costo_unitario=fila["costo_unitario"], dosis_por_ha=fila["dosis_por_ha"]
        )
    elif tipo == "plaguicida":
        return Plaguicida(
            fila["nombre_producto"], fila["stock"],
            fila["periodo_carencia_dias"] or 0,
            costo_unitario=fila["costo_unitario"], dosis_por_ha=fila["dosis_por_ha"]
        )
    elif tipo == "semilla":
        return Semilla(
            fila["nombre_producto"], fila["stock"],
            fila["tasa_germinacion"] or 0,
            costo_unitario=fila["costo_unitario"], dosis_por_ha=fila["dosis_por_ha"]
        )
    return Insumo(fila["nombre_producto"], tipo, fila["stock"], fila["unidad"], fila["costo_unitario"], fila["dosis_por_ha"])

# ----------------------------------------------------------- MAQUINARIA
def guardar_maquinaria(conn, maquina):
    maquina_id = getattr(maquina, "id", getattr(maquina, "_id", None))
    horas_ult = getattr(maquina, "horas_ultimo_mantenimiento", getattr(maquina, "_horas_ultimo_mantenimiento", 0.0))

    with conn:
        conn.execute(
            "INSERT INTO maquinaria (id, nombre, vida_util_horas, intervalo_mantenimiento, horas_uso, horas_ultimo_mantenimiento) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET nombre = excluded.nombre, "
            "vida_util_horas = excluded.vida_util_horas, "
            "intervalo_mantenimiento = excluded.intervalo_mantenimiento, "
            "horas_uso = excluded.horas_uso, "
            "horas_ultimo_mantenimiento = excluded.horas_ultimo_mantenimiento",
            (
                maquina_id,
                maquina.nombre,
                maquina.vida_util_horas,
                maquina.intervalo_mantenimiento,
                maquina.horas_uso,
                horas_ult,
            ),
        )

def listar_maquinarias(conn):
    filas = conn.execute("SELECT * FROM maquinaria ORDER BY id").fetchall()
    maquinas = []
    for f in filas:
        m = Maquinaria(f["id"], f["nombre"], f["vida_util_horas"], f["intervalo_mantenimiento"], f["horas_uso"])
        m._horas_ultimo_mantenimiento = f["horas_ultimo_mantenimiento"]
        maquinas.append(m)
    return maquinas

# ------------------------------------------------------------- CULTIVOS
def guardar_cultivo(conn, lote_id, cultivo):
    fecha_siembra = str(getattr(cultivo, "fecha_siembra", date.today().isoformat()))
    with conn:
        conn.execute(
            "INSERT INTO cultivos (lote_id, tipo_cultivo, variedad, fecha_siembra, etapa) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(lote_id) DO UPDATE SET tipo_cultivo = excluded.tipo_cultivo, "
            "variedad = excluded.variedad, fecha_siembra = excluded.fecha_siembra, "
            "etapa = excluded.etapa",
            (
                lote_id,
                cultivo.nombre,
                cultivo.variedad,
                fecha_siembra,
                cultivo.etapa_fenologica,
            ),
        )

def cargar_cultivo(conn, lote_id):
    fila = conn.execute("SELECT * FROM cultivos WHERE lote_id = ?", (lote_id,)).fetchone()
    if not fila:
        return None
    return Cultivo(fila["tipo_cultivo"], fila["variedad"], fila["etapa"], 30)

# ---------------------------------------------------------- APLICACIONES
def guardar_aplicacion_campo(conn, aplicacion):
    app_id = getattr(aplicacion, "id", getattr(aplicacion, "_id", None))
    
    # 1. Resolver Lote ID
    lote = getattr(aplicacion, "lote", getattr(aplicacion, "_lote", None))
    lote_id = getattr(lote, "id", getattr(lote, "_id", None)) if lote else None
    if lote_id is None and lote and hasattr(lote, "nombre"):
        fila_lote = conn.execute("SELECT id FROM lotes WHERE nombre = ?", (lote.nombre,)).fetchone()
        if fila_lote:
            lote_id = fila_lote["id"]

    # 2. Resolver Insumo ID
    insumo = getattr(aplicacion, "insumo", getattr(aplicacion, "_insumo", None))
    insumo_id = getattr(insumo, "id", getattr(insumo, "_id", None)) if insumo else None
    if insumo_id is None and insumo and hasattr(insumo, "nombre"):
        fila_insumo = conn.execute("SELECT id FROM inventario_insumos WHERE nombre_producto = ?", (insumo.nombre,)).fetchone()
        if fila_insumo:
            insumo_id = fila_insumo["id"]

    if insumo_id is None:
        raise ValueError(f"El insumo '{getattr(insumo, 'nombre', 'desconocido')}' no está registrado en la base de datos.")

    aplicada_val = 1 if getattr(aplicacion, "_aplicada", getattr(aplicacion, "aplicada", False)) else 0

    with conn:
        conn.execute(
            "INSERT INTO aplicaciones_campo (id, lote_id, insumo_id, dosis, fecha, aplicada) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET lote_id = excluded.lote_id, "
            "insumo_id = excluded.insumo_id, dosis = excluded.dosis, "
            "fecha = excluded.fecha, aplicada = excluded.aplicada",
            (
                app_id,
                lote_id,
                insumo_id,
                aplicacion.dosis,
                str(aplicacion.fecha),
                aplicada_val,
            ),
        )

def listar_aplicaciones(conn, lotes_por_id, insumos_por_id):
    return [AplicacionCampo(f["id"], lotes_por_id[f["lote_id"]],
                            insumos_por_id[f["insumo_id"]], f["dosis"],
                            date.fromisoformat(f["fecha"]), bool(f["aplicada"]))
            for f in conn.execute("SELECT * FROM aplicaciones_campo ORDER BY id")]

# ------------------------------------------------------------- COSECHAS
def guardar_cosecha(conn, cosecha):
    cos_id = getattr(cosecha, "id", getattr(cosecha, "_id", None))
    lote = getattr(cosecha, "lote", getattr(cosecha, "_lote", None))
    lote_id = getattr(lote, "id", getattr(lote, "_id", None)) if lote else None
    if lote_id is None and lote and hasattr(lote, "nombre"):
        fila = conn.execute("SELECT id FROM lotes WHERE nombre = ?", (lote.nombre,)).fetchone()
        if fila:
            lote_id = fila["id"]

    with conn:
        conn.execute(
            "INSERT INTO historial_cosechas (id, lote_id, toneladas_recolectadas, fecha_cosecha) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET lote_id = excluded.lote_id, "
            "toneladas_recolectadas = excluded.toneladas_recolectadas, "
            "fecha_cosecha = excluded.fecha_cosecha",
            (
                cos_id,
                lote_id,
                cosecha.toneladas,
                str(cosecha.fecha),
            ),
        )

def listar_cosechas(conn, lotes_por_id):
    return [Cosecha(f["id"], lotes_por_id[f["lote_id"]], f["toneladas_recolectadas"],
                    date.fromisoformat(f["fecha_cosecha"]))
            for f in conn.execute("SELECT * FROM historial_cosechas ORDER BY id")]

# ------------------------------------------------------------ REGISTROS
def guardar_registro(conn, registro):
    reg_id = getattr(registro, "id", getattr(registro, "_id", None))
    lote = getattr(registro, "lote", getattr(registro, "_lote", None))
    lote_id = getattr(lote, "id", getattr(lote, "_id", None)) if lote else 1
    if lote_id is None and lote and hasattr(lote, "nombre"):
        fila = conn.execute("SELECT id FROM lotes WHERE nombre = ?", (lote.nombre,)).fetchone()
        if fila:
            lote_id = fila["id"]

    maquina = getattr(registro, "maquinaria", getattr(registro, "_maquinaria", None))
    maquina_id = getattr(maquina, "id", getattr(maquina, "_id", None)) if maquina else None
    if maquina_id is None and maquina and hasattr(maquina, "nombre"):
        fila_m = conn.execute("SELECT id FROM maquinaria WHERE nombre = ?", (maquina.nombre,)).fetchone()
        if fila_m:
            maquina_id = fila_m["id"]

    completado_val = 1 if getattr(registro, "_completado", getattr(registro, "completado", False)) else 0

    with conn:
        if maquina is not None and maquina_id:
            conn.execute("UPDATE maquinaria SET horas_uso = ?, "
                         "horas_ultimo_mantenimiento = ? WHERE id = ?",
                         (maquina.horas_uso, getattr(maquina, "horas_ultimo_mantenimiento", getattr(maquina, "_horas_ultimo_mantenimiento", 0.0)), maquina_id))
        conn.execute(
            "INSERT INTO registros_campo (id, lote_id, maquinaria_id, actividad, "
            "descripcion, fecha, horas_trabajadas, completado) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET lote_id = excluded.lote_id, "
            "maquinaria_id = excluded.maquinaria_id, actividad = excluded.actividad, "
            "descripcion = excluded.descripcion, fecha = excluded.fecha, "
            "horas_trabajadas = excluded.horas_trabajadas, completado = excluded.completado",
            (reg_id, lote_id, maquina_id,
             registro.actividad, registro.descripcion, str(registro.fecha),
             registro.horas_trabajadas, completado_val),
        )

def listar_registros(conn, lotes_por_id, maquinas_por_id):
    return [RegistroCampo(f["id"], lotes_por_id[f["lote_id"]], f["actividad"],
                          f["descripcion"], date.fromisoformat(f["fecha"]),
                          f["horas_trabajadas"], maquinas_por_id.get(f["maquinaria_id"]),
                          bool(f["completado"]))
            for f in conn.execute("SELECT * FROM registros_campo ORDER BY id")]

# --------------------------------------------------------- DIAGNOSTICOS
def guardar_diagnostico(conn, diagnostico):
    diag_id = getattr(diagnostico, "id", getattr(diagnostico, "_id", None))
    lote = getattr(diagnostico, "lote", getattr(diagnostico, "_lote", None))
    lote_id = getattr(lote, "id", getattr(lote, "_id", None)) if lote else 1
    if lote_id is None and lote and hasattr(lote, "nombre"):
        fila = conn.execute("SELECT id FROM lotes WHERE nombre = ?", (lote.nombre,)).fetchone()
        if fila:
            lote_id = fila["id"]

    with conn:
        conn.execute(
            "INSERT INTO diagnosticos (id, lote_id, tipo, conclusion, recomendacion, "
            "severidad, fecha) VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET lote_id = excluded.lote_id, tipo = excluded.tipo, "
            "conclusion = excluded.conclusion, recomendacion = excluded.recomendacion, "
            "severidad = excluded.severidad, fecha = excluded.fecha",
            (diag_id, lote_id, diagnostico.tipo, diagnostico.conclusion,
             diagnostico.recomendacion, diagnostico.severidad, str(diagnostico.fecha)),
        )

def listar_diagnosticos(conn, lotes_por_id):
    return [Diagnostico(f["id"], lotes_por_id[f["lote_id"]], f["tipo"], f["conclusion"],
                        f["recomendacion"], f["severidad"], date.fromisoformat(f["fecha"]))
            for f in conn.execute("SELECT * FROM diagnosticos ORDER BY id")]

# ---------------------------------------------------------------- GENERAL
def eliminar_por_id(conn, tabla, id):
    if tabla not in TABLAS_CON_ID:
        raise ValueError("Tabla no permitida.")
    with conn:
        conn.execute(f"DELETE FROM {tabla} WHERE id = ?", (id,))

# ----------------------------------------------------------------- FINCA
def guardar_finca(conn, finca):
    lotes = getattr(finca, "lotes", getattr(finca, "_lotes", []))
    for lote in lotes:
        guardar_lote(conn, lote)

    insumos = getattr(finca, "insumos", getattr(finca, "_insumos", getattr(finca, "inventario_insumos", [])))
    for insumo in insumos:
        guardar_insumo(conn, insumo)

    maquinarias = getattr(finca, "maquinarias", getattr(finca, "_maquinarias", []))
    for maquina in maquinarias:
        guardar_maquinaria(conn, maquina)

    for lote in lotes:
        lote_id = getattr(lote, "id", getattr(lote, "_id", None))
        cultivo = finca.cultivo_de(lote) if hasattr(finca, "cultivo_de") else None
        if cultivo is not None:
            guardar_cultivo(conn, lote_id, cultivo)

    aplicaciones = getattr(finca, "aplicaciones", getattr(finca, "_aplicaciones", []))
    for aplicacion in aplicaciones:
        guardar_aplicacion_campo(conn, aplicacion)

    cosechas = getattr(finca, "cosechas", getattr(finca, "_cosechas", []))
    for cosecha in cosechas:
        guardar_cosecha(conn, cosecha)

    registros = getattr(finca, "registros", getattr(finca, "_registros", []))
    for registro in registros:
        guardar_registro(conn, registro)

    diagnosticos = getattr(finca, "diagnosticos", getattr(finca, "_diagnosticos", []))
    for diagnostico in diagnosticos:
        guardar_diagnostico(conn, diagnostico)

def cargar_finca(conn, nombre, ubicacion=""):
    finca = Finca(nombre, ubicacion)

    lotes = listar_lotes(conn)
    for lote in lotes:
        finca.agregar_lote(lote)
    lotes_por_id = {getattr(lote, "id", lote._id): lote for lote in lotes}

    insumos_por_id = {}
    for fila in conn.execute("SELECT * FROM inventario_insumos ORDER BY id"):
        insumo = fila_a_insumo(fila)
        if hasattr(finca, "agregar_insumo"):
            finca.agregar_insumo(insumo)
        insumos_por_id[fila["id"]] = insumo

    maquinas_por_id = {}
    for maquina in listar_maquinarias(conn):
        if hasattr(finca, "agregar_maquinaria"):
            finca.agregar_maquinaria(maquina)
        maquinas_por_id[getattr(maquina, "id", maquina._id)] = maquina

    for lote in lotes:
        lote_id = getattr(lote, "id", lote._id)
        cultivo = cargar_cultivo(conn, lote_id)
        if cultivo is not None and hasattr(finca, "sembrar"):
            finca.sembrar(lote, cultivo)

    for aplicacion in listar_aplicaciones(conn, lotes_por_id, insumos_por_id):
        if hasattr(finca, "agregar_aplicacion"):
            finca.agregar_aplicacion(aplicacion)
    for cosecha in listar_cosechas(conn, lotes_por_id):
        if hasattr(finca, "agregar_cosecha"):
            finca.agregar_cosecha(cosecha)
    for registro in listar_registros(conn, lotes_por_id, maquinas_por_id):
        if hasattr(finca, "agregar_registro"):
            finca.agregar_registro(registro)
    for diagnostico in listar_diagnosticos(conn, lotes_por_id):
        if hasattr(finca, "agregar_diagnostico"):
            finca.agregar_diagnostico(diagnostico)
    return finca

# Alias de compatibilidad con el archivo de prueba
guardar_aplicacion = guardar_aplicacion_campo
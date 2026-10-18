"""Consultas CRUD parametrizadas (SQL) y conversión fila <-> objeto."""
from datetime import date, timedelta

from models.lote import Lote
from models.cultivo import Cultivo
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


def siguiente_id(conn, tabla):
    """Próximo id libre. El nombre de tabla no se puede parametrizar con '?',
    por eso solo se aceptan nombres de una lista fija."""
    if tabla not in TABLAS_CON_ID:
        raise ValueError("Tabla no permitida.")
    return conn.execute(f"SELECT COALESCE(MAX(id), 0) + 1 FROM {tabla}").fetchone()[0]


def eliminar_por_id(conn, tabla, id):
    if tabla not in TABLAS_CON_ID:
        raise ValueError("Tabla no permitida.")
    with conn:
        conn.execute(f"DELETE FROM {tabla} WHERE id = ?", (id,))


# ---------------------------------------------------------------- LOTES
def fila_a_lote(fila):
    return Lote(fila["id"], fila["nombre"], fila["area_ha"], fila["tipo_suelo"],
                fila["ph"], fila["humedad_actual"])


def guardar_lote(conn, lote):
    """Inserta el lote, o actualiza sus datos si ya existe ese id."""
    with conn:
        conn.execute(
            "INSERT INTO lotes (id, nombre, area_ha, tipo_suelo, ph, humedad_actual) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET nombre = excluded.nombre, "
            "area_ha = excluded.area_ha, tipo_suelo = excluded.tipo_suelo, "
            "ph = excluded.ph, humedad_actual = excluded.humedad_actual",
            (lote.id, lote.nombre, lote.hectareas, lote.tipo_suelo,
             lote.ph, lote.humedad_actual),
        )


def obtener_lote(conn, id):
    fila = conn.execute("SELECT * FROM lotes WHERE id = ?", (id,)).fetchone()
    return fila_a_lote(fila) if fila else None


def listar_lotes(conn):
    return [fila_a_lote(f) for f in conn.execute("SELECT * FROM lotes ORDER BY id")]


def eliminar_lote(conn, id):
    eliminar_por_id(conn, "lotes", id)


# ------------------------------------------------------------- CULTIVOS
def guardar_cultivo(conn, lote_id, cultivo):
    """Un lote tiene un solo cultivo. En la base se guarda la fecha de siembra,
    no los días: se calcula a partir de los días del objeto."""
    fecha_siembra = date.today() - timedelta(days=cultivo.dias_desde_siembra)
    with conn:
        conn.execute(
            "INSERT INTO cultivos (lote_id, tipo_cultivo, variedad, fecha_siembra, etapa) "
            "VALUES (?, ?, ?, ?, ?) "
            "ON CONFLICT(lote_id) DO UPDATE SET tipo_cultivo = excluded.tipo_cultivo, "
            "variedad = excluded.variedad, fecha_siembra = excluded.fecha_siembra, "
            "etapa = excluded.etapa",
            (lote_id, cultivo.nombre, cultivo.variedad,
             fecha_siembra.isoformat(), cultivo.etapa_fenologica),
        )


def cargar_cultivo(conn, lote_id):
    fila = conn.execute("SELECT * FROM cultivos WHERE lote_id = ?", (lote_id,)).fetchone()
    if not fila:
        return None
    dias = max(0, (date.today() - date.fromisoformat(fila["fecha_siembra"])).days)
    return Cultivo(fila["tipo_cultivo"], fila["variedad"], fila["etapa"], dias)


# -------------------------------------------------------------- INSUMOS
def fila_a_insumo(fila):
    """Según la columna 'tipo' se construye la subclase correspondiente."""
    comunes = (fila["nombre_producto"], fila["stock"])
    extras = dict(unidad_medida=fila["unidad"], costo_unitario=fila["costo_unitario"],
                  dosis_por_ha=fila["dosis_por_ha"])
    if fila["tipo"] == "fertilizante":
        return Fertilizante(*comunes, fila["n"], fila["p"], fila["k"], **extras)
    if fila["tipo"] == "plaguicida":
        return Plaguicida(*comunes, fila["periodo_carencia_dias"], **extras)
    if fila["tipo"] == "semilla":
        return Semilla(*comunes, fila["tasa_germinacion"], **extras)
    raise ValueError(f"Tipo de insumo desconocido: {fila['tipo']}")


def guardar_insumo(conn, insumo):
    """Inserta el insumo, o actualiza stock y datos si ya existe ese nombre."""
    n = p = k = carencia = germinacion = None
    if isinstance(insumo, Fertilizante):
        n, p, k = insumo.n, insumo.p, insumo.k
    elif isinstance(insumo, Plaguicida):
        carencia = insumo.periodo_carencia_dias
    elif isinstance(insumo, Semilla):
        germinacion = insumo.tasa_germinacion
    else:
        raise ValueError("Solo se pueden guardar Fertilizante, Plaguicida o Semilla.")
    with conn:
        conn.execute(
            "INSERT INTO inventario_insumos (nombre_producto, tipo, stock, unidad, "
            "costo_unitario, dosis_por_ha, n, p, k, periodo_carencia_dias, tasa_germinacion) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(nombre_producto) DO UPDATE SET tipo = excluded.tipo, "
            "stock = excluded.stock, unidad = excluded.unidad, "
            "costo_unitario = excluded.costo_unitario, dosis_por_ha = excluded.dosis_por_ha, "
            "n = excluded.n, p = excluded.p, k = excluded.k, "
            "periodo_carencia_dias = excluded.periodo_carencia_dias, "
            "tasa_germinacion = excluded.tasa_germinacion",
            (insumo.nombre, insumo.tipo, insumo.cantidad_disponible, insumo.unidad_medida,
             insumo.costo_unitario, insumo.dosis_por_ha, n, p, k, carencia, germinacion),
        )


def obtener_insumo(conn, nombre):
    fila = conn.execute("SELECT * FROM inventario_insumos WHERE nombre_producto = ?",
                        (nombre,)).fetchone()
    return fila_a_insumo(fila) if fila else None


def listar_insumos(conn):
    return [fila_a_insumo(f)
            for f in conn.execute("SELECT * FROM inventario_insumos ORDER BY id")]


def eliminar_insumo(conn, nombre):
    with conn:
        conn.execute("DELETE FROM inventario_insumos WHERE nombre_producto = ?", (nombre,))


# ----------------------------------------------------------- MAQUINARIA
def fila_a_maquinaria(fila):
    return Maquinaria(fila["id"], fila["nombre"], fila["vida_util_horas"],
                      fila["intervalo_mantenimiento"], fila["horas_uso"],
                      fila["horas_ultimo_mantenimiento"])


def guardar_maquinaria(conn, maquina):
    with conn:
        conn.execute(
            "INSERT INTO maquinaria (id, nombre, vida_util_horas, intervalo_mantenimiento, "
            "horas_uso, horas_ultimo_mantenimiento) VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET nombre = excluded.nombre, "
            "vida_util_horas = excluded.vida_util_horas, "
            "intervalo_mantenimiento = excluded.intervalo_mantenimiento, "
            "horas_uso = excluded.horas_uso, "
            "horas_ultimo_mantenimiento = excluded.horas_ultimo_mantenimiento",
            (maquina.id, maquina.nombre, maquina.vida_util_horas,
             maquina.intervalo_mantenimiento, maquina.horas_uso,
             maquina.horas_ultimo_mantenimiento),
        )


def obtener_maquinaria(conn, id):
    fila = conn.execute("SELECT * FROM maquinaria WHERE id = ?", (id,)).fetchone()
    return fila_a_maquinaria(fila) if fila else None


def listar_maquinarias(conn):
    return [fila_a_maquinaria(f)
            for f in conn.execute("SELECT * FROM maquinaria ORDER BY id")]


def eliminar_maquinaria(conn, id):
    eliminar_por_id(conn, "maquinaria", id)


# ---------------------------------------------------------- APLICACIONES
def _id_insumo(conn, insumo):
    fila = conn.execute("SELECT id FROM inventario_insumos WHERE nombre_producto = ?",
                        (insumo.nombre,)).fetchone()
    if not fila:
        raise ValueError(f"El insumo '{insumo.nombre}' no está registrado en la base de datos.")
    return fila["id"]


def guardar_aplicacion(conn, aplicacion):
    """Guarda la aplicación y sincroniza el stock del insumo en la misma transacción."""
    insumo_id = _id_insumo(conn, aplicacion.insumo)
    with conn:
        conn.execute("UPDATE inventario_insumos SET stock = ? WHERE id = ?",
                     (aplicacion.insumo.cantidad_disponible, insumo_id))
        conn.execute(
            "INSERT INTO aplicaciones_campo (id, lote_id, insumo_id, dosis, fecha, aplicada) "
            "VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET lote_id = excluded.lote_id, "
            "insumo_id = excluded.insumo_id, dosis = excluded.dosis, "
            "fecha = excluded.fecha, aplicada = excluded.aplicada",
            (aplicacion.id, aplicacion.lote.id, insumo_id, aplicacion.dosis,
             aplicacion.fecha.isoformat(), int(aplicacion.aplicada)),
        )


# Nombre anterior, por compatibilidad con código que ya lo use
guardar_aplicacion_campo = guardar_aplicacion


def listar_aplicaciones(conn, lotes_por_id, insumos_por_id):
    """Recibe los objetos ya cargados para reutilizarlos (misma referencia)."""
    return [AplicacionCampo(f["id"], lotes_por_id[f["lote_id"]],
                            insumos_por_id[f["insumo_id"]], f["dosis"],
                            date.fromisoformat(f["fecha"]), bool(f["aplicada"]))
            for f in conn.execute("SELECT * FROM aplicaciones_campo ORDER BY id")]


# ------------------------------------------------------------- COSECHAS
def guardar_cosecha(conn, cosecha):
    with conn:
        conn.execute(
            "INSERT INTO historial_cosechas (id, lote_id, toneladas_recolectadas, fecha_cosecha) "
            "VALUES (?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET lote_id = excluded.lote_id, "
            "toneladas_recolectadas = excluded.toneladas_recolectadas, "
            "fecha_cosecha = excluded.fecha_cosecha",
            (cosecha.id, cosecha.lote.id, cosecha.toneladas, cosecha.fecha.isoformat()),
        )


def listar_cosechas(conn, lotes_por_id):
    return [Cosecha(f["id"], lotes_por_id[f["lote_id"]], f["toneladas_recolectadas"],
                    date.fromisoformat(f["fecha_cosecha"]))
            for f in conn.execute("SELECT * FROM historial_cosechas ORDER BY id")]


# ------------------------------------------------------------ REGISTROS
def guardar_registro(conn, registro):
    """Guarda el registro y sincroniza las horas de la maquinaria usada."""
    maquina = registro.maquinaria
    with conn:
        if maquina is not None:
            conn.execute("UPDATE maquinaria SET horas_uso = ?, "
                         "horas_ultimo_mantenimiento = ? WHERE id = ?",
                         (maquina.horas_uso, maquina.horas_ultimo_mantenimiento, maquina.id))
        conn.execute(
            "INSERT INTO registros_campo (id, lote_id, maquinaria_id, actividad, "
            "descripcion, fecha, horas_trabajadas, completado) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET lote_id = excluded.lote_id, "
            "maquinaria_id = excluded.maquinaria_id, actividad = excluded.actividad, "
            "descripcion = excluded.descripcion, fecha = excluded.fecha, "
            "horas_trabajadas = excluded.horas_trabajadas, completado = excluded.completado",
            (registro.id, registro.lote.id, maquina.id if maquina else None,
             registro.actividad, registro.descripcion, registro.fecha.isoformat(),
             registro.horas_trabajadas, int(registro.completado)),
        )


def listar_registros(conn, lotes_por_id, maquinas_por_id):
    return [RegistroCampo(f["id"], lotes_por_id[f["lote_id"]], f["actividad"],
                          f["descripcion"], date.fromisoformat(f["fecha"]),
                          f["horas_trabajadas"], maquinas_por_id.get(f["maquinaria_id"]),
                          bool(f["completado"]))
            for f in conn.execute("SELECT * FROM registros_campo ORDER BY id")]


# --------------------------------------------------------- DIAGNOSTICOS
def guardar_diagnostico(conn, diagnostico):
    with conn:
        conn.execute(
            "INSERT INTO diagnosticos (id, lote_id, tipo, conclusion, recomendacion, "
            "severidad, fecha) VALUES (?, ?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET lote_id = excluded.lote_id, tipo = excluded.tipo, "
            "conclusion = excluded.conclusion, recomendacion = excluded.recomendacion, "
            "severidad = excluded.severidad, fecha = excluded.fecha",
            (diagnostico.id, diagnostico.lote.id, diagnostico.tipo, diagnostico.conclusion,
             diagnostico.recomendacion, diagnostico.severidad, diagnostico.fecha.isoformat()),
        )


def listar_diagnosticos(conn, lotes_por_id):
    return [Diagnostico(f["id"], lotes_por_id[f["lote_id"]], f["tipo"], f["conclusion"],
                        f["recomendacion"], f["severidad"], date.fromisoformat(f["fecha"]))
            for f in conn.execute("SELECT * FROM diagnosticos ORDER BY id")]


# ----------------------------------------------------------------- FINCA
def guardar_finca(conn, finca):
    """Guarda todos los objetos de la finca (en orden, por las llaves foráneas)."""
    for lote in finca.lotes:
        guardar_lote(conn, lote)
    for insumo in finca.insumos:
        guardar_insumo(conn, insumo)
    for maquina in finca.maquinarias:
        guardar_maquinaria(conn, maquina)
    for lote in finca.lotes:
        cultivo = finca.cultivo_de(lote)
        if cultivo is not None:
            guardar_cultivo(conn, lote.id, cultivo)
    for aplicacion in finca.aplicaciones:
        guardar_aplicacion(conn, aplicacion)
    for cosecha in finca.cosechas:
        guardar_cosecha(conn, cosecha)
    for registro in finca.registros:
        guardar_registro(conn, registro)
    for diagnostico in finca.diagnosticos:
        guardar_diagnostico(conn, diagnostico)


def cargar_finca(conn, nombre, ubicacion=""):
    """Reconstruye una Finca completa. Cada objeto se crea una sola vez y se
    reutiliza donde se necesite (por eso los diccionarios por id)."""
    finca = Finca(nombre, ubicacion)

    lotes = listar_lotes(conn)
    for lote in lotes:
        finca.agregar_lote(lote)
    lotes_por_id = {lote.id: lote for lote in lotes}

    insumos_por_id = {}
    for fila in conn.execute("SELECT * FROM inventario_insumos ORDER BY id"):
        insumo = fila_a_insumo(fila)
        finca.agregar_insumo(insumo)
        insumos_por_id[fila["id"]] = insumo

    maquinas_por_id = {}
    for maquina in listar_maquinarias(conn):
        finca.agregar_maquinaria(maquina)
        maquinas_por_id[maquina.id] = maquina

    for lote in lotes:
        cultivo = cargar_cultivo(conn, lote.id)
        if cultivo is not None:
            finca.sembrar(lote, cultivo)

    for aplicacion in listar_aplicaciones(conn, lotes_por_id, insumos_por_id):
        finca.agregar_aplicacion(aplicacion)
    for cosecha in listar_cosechas(conn, lotes_por_id):
        finca.agregar_cosecha(cosecha)
    for registro in listar_registros(conn, lotes_por_id, maquinas_por_id):
        finca.agregar_registro(registro)
    for diagnostico in listar_diagnosticos(conn, lotes_por_id):
        finca.agregar_diagnostico(diagnostico)
    return finca
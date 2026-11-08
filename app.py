"""API Flask de AgroControl: usa queries.py, prolog_bridge y analytics."""
import sqlite3
from contextlib import contextmanager
from datetime import date

from flask import Flask, jsonify, request
from flask_cors import CORS

from database import queries as q
from database.db_connection import obtener_conexion
from models.aplicacion_campo import AplicacionCampo
from models.cosecha import Cosecha
from models.cultivo import Cultivo
from models.lote import Lote
from models.registro_campo import RegistroCampo
from rules import prolog_bridge as prolog
from services import analytics, report_generator as rg

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.errorhandler(ValueError)
@app.errorhandler(TypeError)
@app.errorhandler(sqlite3.IntegrityError)
def datos_invalidos(error):
    return jsonify({"error": str(error)}), 400


@app.errorhandler(RuntimeError)
def error_prolog(error):
    return jsonify({"error": str(error)}), 500


@contextmanager
def db():
    conn = obtener_conexion()
    try:
        yield conn
    finally:
        conn.close()


def datos(*requeridos):
    d = request.get_json(silent=True) or {}
    faltan = [c for c in requeridos if d.get(c) in (None, "")]
    if faltan:
        raise ValueError(f"Faltan campos: {', '.join(faltan)}")
    return d


def convertir(d, campo, tipo=float):
    try:
        return tipo(d[campo])
    except (TypeError, ValueError):
        raise ValueError(f"'{campo}' debe ser {'un entero' if tipo is int else 'un número'}.")


def lote_a_dict(l):
    return {"id": l.id, "nombre": l.nombre, "area_ha": l.hectareas,
            "tipo_suelo": l.tipo_suelo, "ph": l.ph, "humedad_actual": l.humedad_actual}


def diag(d):
    return jsonify({k: getattr(d, k) for k in ("tipo", "conclusion", "recomendacion", "severidad")})


def fecha_de(d):
    try:
        return date.fromisoformat(str(d.get("fecha") or date.today())[:10])
    except ValueError:
        raise ValueError("fecha debe tener formato AAAA-MM-DD.")


def filas(sql):
    with db() as conn:
        return jsonify([dict(f) for f in conn.execute(sql)])


def lote_de(d):
    with db() as conn:
        lote = q.obtener_lote(conn, convertir(d, "lote_id", int))
    if lote is None:
        raise ValueError("El lote no existe.")
    return lote


@app.route("/api/lotes", methods=["GET"])
def get_lotes():
    with db() as conn:
        return jsonify([lote_a_dict(l) for l in q.listar_lotes(conn)])


@app.route("/api/lotes", methods=["POST"])
def create_lote():
    d = datos("nombre", "area_ha", "tipo_suelo", "ph")
    with db() as conn:
        lote = Lote(q.siguiente_id(conn, "lotes"), str(d["nombre"]).strip(),
                    convertir(d, "area_ha"), str(d["tipo_suelo"]).strip().lower(),
                    convertir(d, "ph"), float(d.get("humedad_actual") or 0))
        if any(l.nombre.lower() == lote.nombre.lower() for l in q.listar_lotes(conn)):
            raise ValueError(f"Ya existe un lote llamado '{lote.nombre}'.")
        q.guardar_lote(conn, lote)
    return jsonify({"message": "Lote registrado", "id": lote.id}), 201


@app.route("/api/lotes/<int:id>", methods=["DELETE"])
def delete_lote(id):
    with db() as conn:
        if q.obtener_lote(conn, id) is None:
            return jsonify({"error": "El lote no existe."}), 404
        q.eliminar_lote(conn, id)
    return jsonify({"message": "Lote eliminado (y su cultivo, si tenía)."})


@app.route("/api/cultivos", methods=["GET"])
def get_cultivos():
    with db() as conn:
        return jsonify([dict(f) for f in conn.execute(
            "SELECT c.*, l.nombre AS nombre_lote FROM cultivos c "
            "JOIN lotes l ON c.lote_id = l.id")])


@app.route("/api/cultivos", methods=["POST"])
def create_cultivo():
    d = datos("lote_id", "tipo_cultivo")
    try:                                      # los días se calculan desde la fecha
        dias = (date.today() - date.fromisoformat(str(d.get("fecha_siembra") or date.today())[:10])).days
    except ValueError:
        raise ValueError("fecha_siembra debe tener formato AAAA-MM-DD.")
    if dias < 0:
        raise ValueError("La fecha de siembra no puede ser futura.")
    cultivo = Cultivo(str(d["tipo_cultivo"]).strip(), str(d.get("variedad") or "").strip(),
                      str(d.get("etapa") or "germinacion").strip().lower(), dias)
    lote = lote_de(d)
    with db() as conn:
        q.guardar_cultivo(conn, lote.id, cultivo)
    return jsonify({"message": "Cultivo registrado"}), 201


@app.route("/api/insumos", methods=["GET"])
def get_insumos():
    with db() as conn:
        return jsonify([{"id": f["id"], "nombre": f["nombre_producto"], "unidad": f["unidad"],
                         "stock": f["stock"]} for f in conn.execute("SELECT * FROM inventario_insumos")])


@app.route("/api/aplicaciones", methods=["POST"])
def create_aplicacion():
    d = datos("lote_id", "insumo_id", "dosis")
    with db() as conn:
        fila = conn.execute("SELECT nombre_producto FROM inventario_insumos WHERE id = ?",
                            (convertir(d, "insumo_id", int),)).fetchone()
        if fila is None:
            raise ValueError("El insumo no existe.")
        finca = q.cargar_finca(conn, "Mi finca")
        lote = next((l for l in finca.lotes if l.id == convertir(d, "lote_id", int)), None)
        insumo = next((i for i in finca.insumos if i.nombre == fila["nombre_producto"]), None)
        if lote is None or insumo is None:
            raise ValueError("El lote o el insumo no existen.")
        nueva_id = q.siguiente_id(conn, "aplicaciones_campo")
        aplicacion = AplicacionCampo(nueva_id, lote, insumo, convertir(d, "dosis"))
        aplicacion.aplicar()                  # descuenta el stock; valida que alcance
        q.guardar_aplicacion(conn, aplicacion)
    return jsonify({"message": "Aplicación registrada", "id": nueva_id}), 201


@app.route("/api/diagnostico/siembra", methods=["POST"])
def diagnostico_siembra():
    d = datos("lote_id", "cultivo")
    lote = lote_de(d)
    with db() as conn:
        res = prolog.diagnosticar_siembra(q.siguiente_id(conn, "diagnosticos"), lote, d["cultivo"])
        q.guardar_diagnostico(conn, res)
    return diag(res)


@app.route("/api/diagnostico/riego", methods=["POST"])
def diagnostico_riego():
    d = datos("lote_id", "temperatura")
    lote = lote_de(d)
    with db() as conn:
        cultivo = q.cargar_cultivo(conn, lote.id)
        if cultivo is None:
            raise ValueError("El lote no tiene cultivo sembrado.")
        res = prolog.diagnosticar_riego(q.siguiente_id(conn, "diagnosticos"), lote, cultivo,
                                        convertir(d, "temperatura"))
        q.guardar_diagnostico(conn, res)
    return diag(res)


@app.route("/api/diagnostico/plagas", methods=["POST"])
def diagnostico_plagas():
    d = datos("lote_id", "sintomas")
    if not isinstance(d["sintomas"], list):
        raise TypeError("'sintomas' debe ser una lista.")
    lote = lote_de(d)
    with db() as conn:
        res = prolog.diagnosticar_plagas(q.siguiente_id(conn, "diagnosticos"), lote, d["sintomas"])
        q.guardar_diagnostico(conn, res)
    return diag(res)


@app.route("/api/sintomas", methods=["GET"])
def get_sintomas():
    return jsonify(list(prolog.sintomas_conocidos()))


@app.route("/api/resumen", methods=["GET"])
def get_resumen():
    with db() as conn:
        finca = q.cargar_finca(conn, "Mi finca")
    return jsonify(analytics.resumen_finca(finca, float(request.args.get("factor", 1.0))))


@app.route("/api/reporte-general", methods=["GET"])
def get_reporte_general():
    with db() as conn:
        finca = q.cargar_finca(conn, "Mi finca")
    return jsonify({"reporte": rg.reporte_completo(finca)})


@app.route("/api/aplicaciones", methods=["GET"])
def get_aplicaciones():
    return filas("SELECT a.id, l.nombre AS lote, i.nombre_producto AS insumo, a.dosis, a.fecha, "
                 "a.aplicada FROM aplicaciones_campo a JOIN lotes l ON a.lote_id = l.id "
                 "JOIN inventario_insumos i ON a.insumo_id = i.id ORDER BY a.id DESC")


@app.route("/api/diagnosticos", methods=["GET"])
def get_diagnosticos():
    return filas("SELECT d.id, l.nombre AS lote, d.tipo, d.conclusion, d.recomendacion, "
                 "d.severidad, d.fecha FROM diagnosticos d JOIN lotes l ON d.lote_id = l.id "
                 "ORDER BY d.id DESC")


@app.route("/api/bitacora", methods=["GET"])
def get_bitacora():
    return filas("SELECT r.id, l.nombre AS lote, r.actividad, r.descripcion, r.fecha, "
                 "r.horas_trabajadas, r.completado FROM registros_campo r "
                 "JOIN lotes l ON r.lote_id = l.id ORDER BY r.id DESC")


@app.route("/api/bitacora", methods=["POST"])
def create_bitacora():
    d = datos("lote_id", "actividad")
    lote = lote_de(d)
    with db() as conn:
        nueva_id = q.siguiente_id(conn, "registros_campo")
        registro = RegistroCampo(nueva_id, lote, str(d["actividad"]).strip().lower(),
                                 str(d.get("descripcion") or "").strip(), fecha_de(d),
                                 convertir(d, "horas_trabajadas") if d.get("horas_trabajadas") else 0.0,
                                 None, bool(d.get("completado", False)))
        q.guardar_registro(conn, registro)
    return jsonify({"message": "Actividad registrada", "id": nueva_id}), 201


@app.route("/api/cosechas", methods=["GET"])
def get_cosechas():
    return filas("SELECT c.id, l.nombre AS lote, c.toneladas_recolectadas AS toneladas, "
                 "c.fecha_cosecha AS fecha FROM historial_cosechas c "
                 "JOIN lotes l ON c.lote_id = l.id ORDER BY c.id DESC")


@app.route("/api/cosechas", methods=["POST"])
def create_cosecha():
    d = datos("lote_id", "toneladas")
    lote = lote_de(d)
    with db() as conn:
        nueva_id = q.siguiente_id(conn, "historial_cosechas")
        q.guardar_cosecha(conn, Cosecha(nueva_id, lote, convertir(d, "toneladas"), fecha_de(d)))
    return jsonify({"message": "Cosecha registrada", "id": nueva_id}), 201


if __name__ == "__main__":
    app.run(port=5000)
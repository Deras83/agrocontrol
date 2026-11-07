"""API Flask de AgroControl: usa queries.py, prolog_bridge y analytics."""
import sqlite3
from contextlib import contextmanager
from datetime import date

from flask import Flask, jsonify, request
from flask_cors import CORS

from database import queries as q
from database.db_connection import obtener_conexion
from models.aplicacion_campo import AplicacionCampo
from models.cultivo import Cultivo
from models.lote import Lote
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
    return diag(prolog.diagnosticar_siembra(0, lote_de(d), d["cultivo"]))


@app.route("/api/diagnostico/riego", methods=["POST"])
def diagnostico_riego():
    d = datos("lote_id", "temperatura")
    lote = lote_de(d)
    with db() as conn:
        cultivo = q.cargar_cultivo(conn, lote.id)
    if cultivo is None:
        raise ValueError("El lote no tiene cultivo sembrado.")
    return diag(prolog.diagnosticar_riego(0, lote, cultivo, convertir(d, "temperatura")))


@app.route("/api/diagnostico/plagas", methods=["POST"])
def diagnostico_plagas():
    d = datos("lote_id", "sintomas")
    if not isinstance(d["sintomas"], list):
        raise TypeError("'sintomas' debe ser una lista.")
    return diag(prolog.diagnosticar_plagas(0, lote_de(d), d["sintomas"]))


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


if __name__ == "__main__":
    app.run(port=5000)
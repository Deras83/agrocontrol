"""API Flask de AgroControl: usa queries.py, prolog_bridge y analytics."""

import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS

from database import queries as q
from database.db_connection import obtener_conexion
from models.cultivo import Cultivo
from models.lote import Lote
from rules import prolog_bridge as prolog
from services import analytics
from services import report_generator as rg

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return '', 204
CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.errorhandler(Exception)
def manejar_error(error):
    """Errores de datos -> JSON 400. Cualquier otro se deja pasar."""
    if isinstance(error, (ValueError, TypeError, KeyError, sqlite3.IntegrityError, RuntimeError)):
        return jsonify({"error": str(error)}), 400
    raise error


def datos():
    return request.get_json(silent=True) or {}


def lote_a_dict(lote):
    return {"id": lote.id, "nombre": lote.nombre, "area_ha": lote.hectareas,
            "tipo_suelo": lote.tipo_suelo, "ph": lote.ph,
            "humedad_actual": lote.humedad_actual}


def diagnostico_a_dict(d):
    return {"tipo": d.tipo, "conclusion": d.conclusion,
            "recomendacion": d.recomendacion, "severidad": d.severidad}


# ---------------------------------------------------------------- lotes


@app.route("/api/lotes", methods=["GET"])
def get_lotes():
    with obtener_conexion() as conn:
        return jsonify([lote_a_dict(l) for l in q.listar_lotes(conn)])


@app.route("/api/lotes", methods=["POST"])
def create_lote():
    d = datos()
    conn = obtener_conexion()
    try:
        lote = Lote(q.siguiente_id(conn, "lotes"), d.get("nombre"), float(d["area_ha"]),
                    d.get("tipo_suelo"), float(d["ph"]), float(d.get("humedad_actual", 0)))
        q.guardar_lote(conn, lote)
    finally:
        conn.close()
    return jsonify({"message": "Lote registrado", "id": lote.id}), 201


@app.route("/api/lotes/<int:id>", methods=["DELETE"])
def delete_lote(id):
    conn = obtener_conexion()
    try:
        q.eliminar_lote(conn, id)
    finally:
        conn.close()
    return jsonify({"message": "Lote eliminado"})


# -------------------------------------------------------------- cultivos
@app.route("/api/cultivos", methods=["GET"])
def get_cultivos():
    with obtener_conexion() as conn:
        # Asegurar que devuelva diccionarios si el row_factory no está global
        conn.row_factory = sqlite3.Row
        filas = conn.execute(
            "SELECT c.*, l.nombre AS nombre_lote FROM cultivos c "
            "JOIN lotes l ON c.lote_id = l.id"
        ).fetchall()
    return jsonify([dict(f) for f in filas])


@app.route("/api/cultivos", methods=["POST"])
def create_cultivo():
    d = datos()
    etapa = str(d.get("etapa") or "germinacion").strip().lower()
    cultivo = Cultivo(d.get("tipo_cultivo"), d.get("variedad"), etapa, 0)
    conn = obtener_conexion()
    try:
        if q.obtener_lote(conn, d.get("lote_id")) is None:
            raise ValueError("El lote no existe.")
        q.guardar_cultivo(conn, d["lote_id"], cultivo)
    finally:
        conn.close()
    return jsonify({"message": "Cultivo registrado"}), 201


# ----------------------------------------------------------- diagnósticos
def lote_de(conn, d):
    lote = q.obtener_lote(conn, d.get("lote_id"))
    if lote is None:
        raise ValueError("El lote no existe.")
    return lote


@app.route("/api/diagnostico/siembra", methods=["POST"])
def diagnostico_siembra():
    d = datos()
    with obtener_conexion() as conn:
        lote = lote_de(conn, d)
    return jsonify(diagnostico_a_dict(
        prolog.diagnosticar_siembra(0, lote, d.get("cultivo", ""))))


@app.route("/api/diagnostico/riego", methods=["POST"])
def diagnostico_riego():
    d = datos()
    with obtener_conexion() as conn:
        lote = lote_de(conn, d)
        cultivo = q.cargar_cultivo(conn, lote.id)
    if cultivo is None:
        raise ValueError("El lote no tiene cultivo sembrado.")
    return jsonify(diagnostico_a_dict(
        prolog.diagnosticar_riego(0, lote, cultivo, float(d["temperatura"]))))


@app.route("/api/diagnostico/plagas", methods=["POST"])
def diagnostico_plagas():
    d = datos()
    with obtener_conexion() as conn:
        lote = lote_de(conn, d)
    
    resultado = prolog.diagnosticar_plagas(0, lote, d.get("sintomas", []))
    
    # Maneja de forma segura si Prolog devuelve una lista o un solo objeto
    if isinstance(resultado, list):
        return jsonify([diagnostico_a_dict(item) for item in resultado])
    return jsonify(diagnostico_a_dict(resultado))

@app.route("/api/sintomas", methods=["GET"])
def get_sintomas():
    return jsonify(list(prolog.sintomas_conocidos()))

# ---------------------------------------------------------------- aplicaciones
@app.route("/api/aplicaciones", methods=["POST"])
def create_aplicacion():
    d = datos()
    conn = obtener_conexion()
    try:
        finca = q.cargar_finca(conn, "Mi finca")
        lote = next((l for l in finca.lotes if l.id == int(d.get("lote_id"))), None)
        insumo = next((i for i in finca.insumos if i.id == int(d.get("insumo_id"))), None)
        
        if not lote or not insumo:
            raise ValueError("El lote o el insumo no existen.")
            
        from models.aplicacion_campo import AplicacionCampo
        aplicacion_id = q.siguiente_id(conn, "aplicaciones_campo")
        nueva_app = AplicacionCampo(aplicacion_id, lote, insumo, float(d["dosis"]))
        nueva_app.aplicar()  # Descuenta el inventario
        q.guardar_aplicacion(conn, nueva_app)
    finally:
        conn.close()
    return jsonify({"message": "Aplicación registrada con éxito", "id": aplicacion_id}), 201
    
@app.route("/api/insumos", methods=["GET"])
def get_insumos():
    with obtener_conexion() as conn:
        conn.row_factory = sqlite3.Row
        filas = conn.execute("SELECT * FROM inventario_insumos").fetchall()

    insumos_data = [
        {
            "id": i["id"],
            "nombre": i["nombre_producto"],
            "unidad": i["unidad"],
            "stock": i["stock"] if "stock" in i.keys() else 0
        } for i in filas
    ]
    return jsonify(insumos_data)
# ---------------------------------------------------------------- resumen
@app.route("/api/resumen", methods=["GET"])
def get_resumen():
    factor = float(request.args.get("factor", 1.0))
    with obtener_conexion() as conn:
        finca = q.cargar_finca(conn, "Mi finca")
    return jsonify(analytics.resumen_finca(finca, factor))

@app.route("/api/reporte-general", methods=["GET"])
def get_reporte_general():
    with obtener_conexion() as conn:
        finca = q.cargar_finca(conn, "Mi finca")
    texto_reporte = rg.reporte_completo(finca)
    return jsonify({"reporte": texto_reporte})

if __name__ == "__main__":
    app.run(port=5000)
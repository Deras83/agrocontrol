"""Smoke test de todos los endpoints de AgroControl.

Uso local (levanta la app en proceso con una BD SQLite temporal, sin tocar tu BD):
    python tests/smoke_api.py

Uso contra una app desplegada (solo lecturas y diagnósticos, sin borrados):
    python tests/smoke_api.py --base-url https://mi-app.onrender.com

Los diagnósticos del sistema experto requieren SWI-Prolog en el PATH.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

FALLOS = []
TIENE_PROLOG = shutil.which("swipl") is not None


def revisar(nombre, esperado, obtenido):
    if obtenido == esperado:
        print(f"OK     {nombre} -> {obtenido}")
    else:
        print(f"FALLO  {nombre} -> {obtenido} (esperado {esperado})")
        FALLOS.append(f"{nombre}: esperado {esperado}, obtenido {obtenido}")


class ClienteLocal:
    """Usa el cliente de pruebas de Flask con una BD temporal."""

    def __init__(self, flask_app):
        self._cliente = flask_app.test_client()

    def pedir(self, metodo, ruta, datos=None):
        respuesta = self._cliente.open(ruta, method=metodo, json=datos)
        return respuesta.status_code, respuesta.get_json(silent=True)


class ClienteRemoto:
    """Habla HTTP contra la URL desplegada (Render)."""

    def __init__(self, base):
        self.base = base.rstrip("/")

    def pedir(self, metodo, ruta, datos=None):
        cuerpo = json.dumps(datos).encode() if datos is not None else None
        peticion = urllib.request.Request(
            self.base + ruta, data=cuerpo, method=metodo,
            headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(peticion, timeout=90) as respuesta:
                return respuesta.status, json.loads(respuesta.read() or b"null")
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read() or b"null")


def probar_lecturas(cliente):
    for ruta in ("/api/lotes", "/api/cultivos", "/api/insumos", "/api/aplicaciones",
                 "/api/diagnosticos", "/api/bitacora", "/api/cosechas",
                 "/api/resumen", "/api/reporte-general", "/api/sintomas"):
        estado, _ = cliente.pedir("GET", ruta)
        revisar(f"GET {ruta}", 200, estado)


def probar_diagnosticos(cliente):
    if not TIENE_PROLOG:
        print("AVISO  swipl no encontrado: se omiten los diagnósticos del sistema experto.")
        return

    estado, lotes = cliente.pedir("GET", "/api/lotes")
    if estado != 200 or not lotes:
        print("AVISO  no hay lotes: se omiten los diagnósticos.")
        return
    lote_id = lotes[0]["id"]

    estado, cultivos = cliente.pedir("GET", "/api/cultivos")
    lote_riego = cultivos[0]["lote_id"] if cultivos else None

    estado, _ = cliente.pedir("POST", "/api/diagnostico/siembra",
                              {"lote_id": lote_id, "cultivo": "maiz"})
    revisar("POST /api/diagnostico/siembra", 200, estado)

    if lote_riego is not None:
        estado, _ = cliente.pedir("POST", "/api/diagnostico/riego",
                                  {"lote_id": lote_riego, "temperatura": 25})
        revisar("POST /api/diagnostico/riego", 200, estado)
    else:
        print("AVISO  sin cultivos: se omite el diagnóstico de riego.")

    estado, _ = cliente.pedir("POST", "/api/diagnostico/plagas",
                              {"lote_id": lote_id,
                               "sintomas": ["hojas_amarillas", "hojas_viejas_primero",
                                            "crecimiento_lento"]})
    revisar("POST /api/diagnostico/plagas", 200, estado)

    estado, _ = cliente.pedir("POST", "/api/diagnostico/plagas",
                              {"lote_id": lote_id, "sintomas": "no_es_lista"})
    revisar("POST /api/diagnostico/plagas (inválido)", 400, estado)


def probar_escrituras(cliente):
    sufijo = str(int(time.time() * 1000))
    lote = {"nombre": f"Lote Smoke {sufijo}", "area_ha": 1.0, "tipo_suelo": "franco",
            "ph": 6.5, "humedad_actual": 40}
    estado, cuerpo = cliente.pedir("POST", "/api/lotes", lote)
    revisar("POST /api/lotes", 201, estado)
    lote_id = cuerpo["id"] if estado == 201 else None

    if lote_id is None:
        return

    estado, _ = cliente.pedir("PUT", f"/api/lotes/{lote_id}/humedad", {"humedad": 55})
    revisar("PUT /api/lotes/<id>/humedad", 200, estado)

    estado, _ = cliente.pedir("POST", "/api/cultivos",
                               {"lote_id": lote_id, "tipo_cultivo": "maiz",
                                "variedad": "smoke", "etapa": "germinacion",
                                "fecha_siembra": date.today().isoformat()})
    revisar("POST /api/cultivos", 201, estado)

    estado, _ = cliente.pedir("POST", "/api/cultivos",
                               {"lote_id": lote_id, "tipo_cultivo": "frijol",
                                "variedad": "dup", "etapa": "germinacion",
                                "fecha_siembra": date.today().isoformat()})
    revisar("POST /api/cultivos (duplicado)", 400, estado)

    estado, cultivos = cliente.pedir("GET", "/api/cultivos")
    cultivo = next((c for c in cultivos if c["lote_id"] == lote_id), None)
    if cultivo:
        cultivo_id = cultivo["id"]
        estado, _ = cliente.pedir("PUT", f"/api/cultivos/{cultivo_id}/etapa",
                                  {"etapa": "vegetativa"})
        revisar("PUT /api/cultivos/<id>/etapa", 200, estado)

        estado, _ = cliente.pedir("DELETE", f"/api/cultivos/{cultivo_id}",
                                  {"motivo": "inexistente"})
        revisar("DELETE /api/cultivos/<id> (motivo inválido)", 400, estado)

        estado, _ = cliente.pedir("DELETE", "/api/cultivos/999999999",
                                  {"motivo": "perdido"})
        revisar("DELETE /api/cultivos/<id> (no existe)", 404, estado)

        estado, cuerpo = cliente.pedir("DELETE", f"/api/cultivos/{cultivo_id}",
                                       {"motivo": "error", "nota": "smoke"})
        revisar("DELETE /api/cultivos/<id>", 200, estado)
        bitacora_id = cuerpo.get("bitacora_id") if estado == 200 else None

        estado, cultivos = cliente.pedir("GET", "/api/cultivos")
        revisar("cultivo eliminado", False,
                any(c["id"] == cultivo_id for c in cultivos))

        estado, bitacora = cliente.pedir("GET", "/api/bitacora")
        registro = next((r for r in bitacora if r["id"] == bitacora_id), None)
        revisar("bitácora eliminación", "otro", registro["actividad"] if registro else None)
        revisar("bitácora completado", 1, registro["completado"] if registro else None)
        revisar("bitácora motivo", True,
                bool(registro and "error" in registro["descripcion"].lower()))

    estado, _ = cliente.pedir("POST", "/api/insumos",
                              {"nombre": f"Fert Smoke {sufijo}", "tipo": "fertilizante",
                               "stock": 100, "unidad": "kg", "n": 46, "p": 0, "k": 0})
    revisar("POST /api/insumos", 201, estado)
    estado, insumos = cliente.pedir("GET", "/api/insumos")
    insumo = next((i for i in insumos if i["nombre"] == f"Fert Smoke {sufijo}"), None)

    if insumo:
        estado, _ = cliente.pedir("POST", f"/api/insumos/{insumo['id']}/reabastecer",
                                  {"cantidad": 50})
        revisar("POST /api/insumos/<id>/reabastecer", 200, estado)
        estado, _ = cliente.pedir("POST", "/api/aplicaciones",
                                  {"lote_id": lote_id, "insumo_id": insumo["id"], "dosis": 5})
        revisar("POST /api/aplicaciones", 201, estado)

    estado, _ = cliente.pedir("POST", "/api/bitacora",
                              {"lote_id": lote_id, "actividad": "riego",
                               "descripcion": "smoke", "horas_trabajadas": 1})
    revisar("POST /api/bitacora", 201, estado)

    estado, _ = cliente.pedir("POST", "/api/cosechas",
                              {"lote_id": lote_id, "toneladas": 1.5})
    revisar("POST /api/cosechas", 201, estado)

    estado, _ = cliente.pedir("POST", "/api/insumos",
                              {"nombre": f"Insumo Borrar {sufijo}", "tipo": "semilla",
                               "stock": 10, "unidad": "kg", "tasa_germinacion": 90})
    revisar("POST /api/insumos (borrar)", 201, estado)
    estado, insumos = cliente.pedir("GET", "/api/insumos")
    borrar = next((i for i in insumos if i["nombre"] == f"Insumo Borrar {sufijo}"), None)
    if borrar:
        estado, _ = cliente.pedir("DELETE", f"/api/insumos/{borrar['id']}")
        revisar("DELETE /api/insumos/<id>", 200, estado)

    estado, cuerpo = cliente.pedir("POST", "/api/lotes",
                                   {"nombre": f"Lote Borrar {sufijo}", "area_ha": 0.5,
                                    "tipo_suelo": "arenoso", "ph": 6.0})
    revisar("POST /api/lotes (borrar)", 201, estado)
    if estado == 201:
        estado, _ = cliente.pedir("DELETE", f"/api/lotes/{cuerpo['id']}")
        revisar("DELETE /api/lotes/<id>", 200, estado)

    estado, _ = cliente.pedir("POST", "/api/lotes", {})
    revisar("POST /api/lotes (inválido)", 400, estado)


def main():
    analizador = argparse.ArgumentParser(description="Smoke test de la API de AgroControl")
    analizador.add_argument("--base-url", default=os.environ.get("SMOKE_BASE_URL", ""),
                            help="URL desplegada; si se omite, usa una BD SQLite temporal")
    opciones = analizador.parse_args()

    if opciones.base_url:
        print(f"Probando app desplegada: {opciones.base_url}")
        cliente = ClienteRemoto(opciones.base_url)
        probar_lecturas(cliente)
        probar_diagnosticos(cliente)
    else:
        directorio = tempfile.mkdtemp(prefix="agrocontrol_smoke_")
        os.environ["AGROCONTROL_DB_PATH"] = os.path.join(directorio, "smoke.db")
        os.environ["AGROCONTROL_AUTO_SEED"] = "1"
        os.environ.pop("DATABASE_URL", None)
        import app  # importa Flask (crea tablas y siembra la BD temporal)
        print("Probando app local con una base SQLite temporal")
        cliente = ClienteLocal(app.app)
        probar_lecturas(cliente)
        probar_diagnosticos(cliente)
        probar_escrituras(cliente)

    print()
    if FALLOS:
        print(f"{len(FALLOS)} FALLO(S):")
        for fallo in FALLOS:
            print(" -", fallo)
        return 1
    print("TODO OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Menú de consola (Programación Estructurada): secuencia, selección (if/elif),
iteración (while) y funciones con validación (try/except). Los datos viven en SQL,
se usan como objetos (POO), Prolog diagnostica y los reportes son funcionales."""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DB_PATH
from database.db_connection import obtener_conexion, crear_tablas
from database import queries as q
from models.lote import Lote
from models.cultivo import Cultivo
from models.fertilizante import Fertilizante
from models.plaguicida import Plaguicida
from models.semilla import Semilla
from models.aplicacion_campo import AplicacionCampo
from rules import prolog_bridge as pb
from services import report_generator as rg

# --- entrada de datos con validación ---
def leer_texto(mensaje):
    texto = ""
    while not texto:
        texto = input(mensaje).strip()
    return texto

def leer_numero(mensaje):
    valor = None
    while valor is None:
        try:
            valor = float(input(mensaje).strip().replace(",", "."))
        except ValueError:
            print("Ingresa un número válido.")
    return valor

def elegir(titulo, elementos):
    elegido = None
    if not elementos:
        print(f"No hay {titulo}.")
    else:
        for numero, elemento in enumerate(elementos, 1):
            print(f"{numero}. {elemento}")
        opcion = ""
        while elegido is None and opcion != "0":
            opcion = input("Número (0 = cancelar): ").strip()
            if opcion.isdigit() and 1 <= int(opcion) <= len(elementos):
                elegido = elementos[int(opcion) - 1]
            elif opcion != "0":
                print("Opción inválida.")
    return elegido

def ejecutar(accion, conn):
    """Corre una opción del menú; si falla, muestra el motivo y el programa sigue."""
    try:
        accion(conn)
    except (ValueError, TypeError, sqlite3.IntegrityError, RuntimeError) as error:
        print(f"No se pudo completar: {error}")

def cargar(conn):
    return q.cargar_finca(conn, "Mi finca")      # la base es la fuente de verdad

# --- lotes, cultivos e inventario ---
def registrar_lote(conn):
    nombre = leer_texto("Nombre del lote: ")
    hectareas = leer_numero("Hectáreas: ")
    suelo = elegir("tipos de suelo", Lote.TIPOS_SUELO) or ""
    ph = leer_numero("pH (0-14): ")
    humedad = leer_numero("Humedad (0-100): ")
    lote = Lote(q.siguiente_id(conn, "lotes"), nombre, hectareas, suelo, ph, humedad)
    q.guardar_lote(conn, lote)
    print(f"Registrado: {lote}")

def listar_lotes(conn):
    print("\n".join(map(str, cargar(conn).lotes)) or "No hay lotes.")

def actualizar_humedad(conn):
    lote = elegir("lotes", cargar(conn).lotes)
    if lote is not None:
        lote.actualizar_sensor(leer_numero("Nueva humedad (0-100): "))
        q.guardar_lote(conn, lote)
        print(lote)

def sembrar_cultivo(conn):
    finca = cargar(conn)
    lote = elegir("lotes", finca.lotes)
    if lote is not None:
        cultivo = Cultivo(leer_texto("Cultivo: "), input("Variedad (opcional): "))
        finca.sembrar(lote, cultivo)             # avisa si el lote ya tiene cultivo
        q.guardar_cultivo(conn, lote.id, cultivo)
        print(f"Sembrado en {lote.nombre}: {cultivo}")

def registrar_insumo(conn):
    tipo = elegir("tipos de insumo", ("fertilizante", "plaguicida", "semilla"))
    if tipo is None:
        raise ValueError("Registro cancelado.")
    nombre = leer_texto("Nombre del producto: ")
    if cargar(conn).buscar_insumo(nombre) is not None:
        raise ValueError("Ya existe un insumo con ese nombre.")
    cantidad = leer_numero("Cantidad disponible: ")
    extra = dict(costo_unitario=leer_numero("Costo por unidad: "),
                 dosis_por_ha=leer_numero("Dosis por hectárea: "))
    if tipo == "fertilizante":
        npk = [leer_numero(f"% de {nutriente}: ") for nutriente in "NPK"]
        insumo = Fertilizante(nombre, cantidad, *npk, **extra)
    elif tipo == "plaguicida":
        insumo = Plaguicida(nombre, cantidad, int(leer_numero("Días de carencia: ")), **extra)
    else:
        insumo = Semilla(nombre, cantidad, leer_numero("% de germinación: "), **extra)
    q.guardar_insumo(conn, insumo)
    print(f"Registrado: {insumo}")

def registrar_aplicacion(conn):
    finca = q.cargar(conn)
    lote = elegir("lotes", finca.lotes)
    insumo = elegir("insumos", finca.insumos) if lote is not None else None
    if lote is not None and insumo is not None:
        print(f"Dosis recomendada: {insumo.dosis_recomendada(lote.hectareas):.2f} {insumo.unidad_medida}")
        aplicacion = AplicacionCampo(
            q.siguiente_id(conn, "aplicaciones_campo"),
            lote, insumo, leer_numero("Dosis a aplicar: ")
        )
        aplicacion.aplicar()  # Descuenta el inventario
        q.guardar_aplicacion(conn, aplicacion)
        print(aplicacion)

def ver_bodega(conn):
    finca = q.cargar_finca(conn, "Mi finca")
    print("\n========================================")
    print("       INVENTARIO DE BODEGA / INSUMOS    ")
    print("========================================")
    if not finca.insumos:
        print("  No hay insumos registrados en la bodega.")
    else:
        for i in finca.insumos:
            stock = getattr(i, 'stock', 'N/D')
            print(f"  - {i.nombre} | Stock: {i.cantidad_disponible} {i.unidad_medida}")
    print("========================================")
# --- diagnóstico (sistema experto en Prolog) ---
def guardar_y_mostrar(conn, diagnostico):
    q.guardar_diagnostico(conn, diagnostico)
    print(diagnostico)

def diagnostico_siembra(conn):
    lote = elegir("lotes", cargar(conn).lotes)
    if lote is not None:
        print("Cultivos aptos:", ", ".join(pb.cultivos_aptos(lote.ph, lote.tipo_suelo)) or "ninguno")
        cultivo = leer_texto("Cultivo a evaluar: ")
        guardar_y_mostrar(conn, pb.diagnosticar_siembra(q.siguiente_id(conn, "diagnosticos"), lote, cultivo))

def diagnostico_riego(conn):
    finca = cargar(conn)
    lote = elegir("lotes", finca.lotes)
    if lote is not None:
        cultivo = finca.cultivo_de(lote)
        if cultivo is None:
            raise ValueError("Ese lote no tiene cultivo sembrado.")
        temperatura = leer_numero("Temperatura (°C): ")
        guardar_y_mostrar(conn, pb.diagnosticar_riego(q.siguiente_id(conn, "diagnosticos"), lote, cultivo, temperatura))

def diagnostico_plagas(conn):
    lote = elegir("lotes", cargar(conn).lotes)
    if lote is not None:
        disponibles = pb.sintomas_conocidos()
        for numero, sintoma in enumerate(disponibles, 1):
            print(f"{numero}. {sintoma.replace('_', ' ')}")
        numeros = [t.strip() for t in input("Números separados por coma: ").split(",")]
        if not all(n.isdigit() and 1 <= int(n) <= len(disponibles) for n in numeros):
            raise ValueError("Escribe números de la lista, separados por coma.")
        sintomas = [disponibles[int(n) - 1] for n in numeros]
        guardar_y_mostrar(conn, pb.diagnosticar_plagas(q.siguiente_id(conn, "diagnosticos"), lote, sintomas))

# --- reporte (funcional) y menú ---
def reporte(conn):
    print("\n" + rg.reporte_completo(cargar(conn)))

MENU = """
=== AgroControl ===
1. Registrar lote            6. Registrar aplicación
2. Listar lotes              7. Diagnóstico: ¿puedo sembrar?
3. Actualizar humedad        8. Diagnóstico: riego
4. Sembrar cultivo           9. Diagnóstico: plagas
5. Registrar insumo         10. Reporte completo
                            11. Ver bodega / insumos
0. Salir"""

ACCIONES = {"1": registrar_lote, "2": listar_lotes, "3": actualizar_humedad,
            "4": sembrar_cultivo, "5": registrar_insumo, "6": registrar_aplicacion,
            "7": diagnostico_siembra, "8": diagnostico_riego, "9": diagnostico_plagas,
            "10": reporte, "11": ver_bodega}

def menu_principal(conn):
    opcion = ""
    while opcion != "0":
        print(MENU)
        opcion = input("Opción: ").strip()
        if opcion in ACCIONES:
            ejecutar(ACCIONES[opcion], conn)
        elif opcion != "0":
            print("Opción inválida.")
    print("Hasta luego.")

def iniciar(ruta=DB_PATH):
    conn = obtener_conexion(ruta)
    try:
        crear_tablas(conn)
        menu_principal(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    iniciar()
"""Enlace entre Python y SWI-Prolog (llama a swipl con subprocess)."""
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PROLOG_FILE
from models.lote import Lote
from models.cultivo import Cultivo
from models.diagnostico import Diagnostico


# ------------------------------------------------ preparar datos para Prolog
def _atomo(texto):
    """Convierte un texto en un átomo Prolog seguro: sin tildes, en minúsculas,
    con guiones bajos. Nunca se pega texto crudo dentro de una consulta."""
    limpio = unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode()
    limpio = limpio.lower().strip().replace(" ", "_")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", limpio):
        raise ValueError(f"Valor no válido para Prolog: {texto!r}")
    return limpio


def _numero(valor):
    return f"{float(valor):.4f}"


# --------------------------------------------------------- ejecutar consultas
def _ejecutar(objetivo):
    """Carga sistema_experto.pl, ejecuta el objetivo y devuelve lo que imprime."""
    ruta = PROLOG_FILE.as_posix().replace("'", "\\'")
    comando = ["swipl", "-q", "-g", f"consult('{ruta}'), {objetivo}, halt", "-t", "halt"]
    try:
        resultado = subprocess.run(comando, capture_output=True, text=True, timeout=10)
    except FileNotFoundError:
        raise RuntimeError("No se encontró swipl. Revisa que SWI-Prolog esté en el PATH.")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Prolog tardó demasiado en responder.")
    if resultado.returncode != 0:
        raise RuntimeError(f"Error de Prolog: {resultado.stderr.strip()}")
    return resultado.stdout.strip()


# ------------------------------------------------------ aprobación de siembra
def puede_sembrar(cultivo, ph, suelo):
    objetivo = (f"(puede_sembrar({_atomo(cultivo)}, {_numero(ph)}, {_atomo(suelo)})"
                " -> write(si) ; write(no))")
    return _ejecutar(objetivo) == "si"


def motivo_rechazo(cultivo, ph, suelo):
    """None si se puede sembrar; si no, 'cultivo_desconocido',
    'ph_fuera_de_rango' o 'suelo_no_apto'."""
    objetivo = (f"(motivo_rechazo({_atomo(cultivo)}, {_numero(ph)}, {_atomo(suelo)}, M)"
                " -> write(M) ; write(ninguno))")
    salida = _ejecutar(objetivo)
    return None if salida == "ninguno" else salida


def cultivos_aptos(ph, suelo):
    objetivo = (f"findall(C, puede_sembrar(C, {_numero(ph)}, {_atomo(suelo)}), L), "
                "atomic_list_concat(L, ',', R), write(R)")
    salida = _ejecutar(objetivo)
    return salida.split(",") if salida else []


MOTIVOS = {
    "cultivo_desconocido": ("el cultivo no está en la base de conocimientos",
                            "Revisa el nombre o agrégalo en sistema_experto.pl."),
    "ph_fuera_de_rango": ("el pH del lote está fuera del rango del cultivo",
                          "Ajusta el pH del lote o elige otro cultivo."),
    "suelo_no_apto": ("el tipo de suelo no es apto para el cultivo",
                      "Elige otro cultivo o mejora el suelo."),
}


def diagnosticar_siembra(id, lote, cultivo):
    """Consulta a Prolog y devuelve un objeto Diagnostico de tipo 'siembra'."""
    if not isinstance(lote, Lote):
        raise TypeError("lote debe ser un objeto Lote.")
    motivo = motivo_rechazo(cultivo, lote.ph, lote.tipo_suelo)
    if motivo is None:
        respuesta = {"conclusion": f"{lote.nombre} es apto para sembrar {cultivo}",
                     "recomendacion": "Puede proceder con la siembra.",
                     "severidad": "baja"}
    else:
        explicacion, recomendacion = MOTIVOS[motivo]
        respuesta = {"conclusion": f"{lote.nombre} no es apto para {cultivo}: {explicacion}",
                     "recomendacion": recomendacion,
                     "severidad": "media"}
    return Diagnostico.desde_respuesta(id, lote, "siembra", respuesta)


# ------------------------------------------------------ riego y fertirriego
def diagnostico_riego(etapa, humedad, temperatura):
    """Devuelve {'accion', 'nutriente', 'severidad'} o None si Prolog no puede
    diagnosticar (por ejemplo, una etapa que no conoce)."""
    objetivo = (f"(diagnostico_riego({_atomo(etapa)}, {_numero(humedad)}, "
                f"{_numero(temperatura)}, A, N, S)"
                " -> format('~w,~w,~w', [A, N, S]) ; write(sin_diagnostico))")
    salida = _ejecutar(objetivo)
    if salida == "sin_diagnostico":
        return None
    accion, nutriente, severidad = salida.split(",")
    return {"accion": accion, "nutriente": nutriente, "severidad": severidad}


ACCIONES = {
    "riego_inmediato_abundante": "Humedad baja con clima cálido: regar de inmediato y en abundancia",
    "riego_inmediato": "Humedad baja: regar de inmediato",
    "riego_ligero": "Humedad baja con clima frío: aplicar riego ligero",
    "mantener_riego_y_vigilar_evaporacion":
        "Humedad adecuada, pero el calor acelera la evaporación: mantener el riego y vigilar",
    "mantener_riego_actual": "Humedad adecuada: mantener el riego actual",
    "suspender_riego_y_revisar_drenaje": "Humedad alta: suspender el riego y revisar el drenaje",
}

NUTRIENTES = {
    "nitrogeno": "nitrógeno",
    "fosforo": "fósforo",
    "potasio": "potasio",
    "fosforo_potasio": "fósforo y potasio",
    "ninguno": None,
}


def diagnosticar_riego(id, lote, cultivo, temperatura):
    """Usa la humedad del lote, la etapa del cultivo y la temperatura que
    ingresa el usuario. Devuelve un Diagnostico de tipo 'riego'."""
    if not isinstance(lote, Lote):
        raise TypeError("lote debe ser un objeto Lote.")
    if not isinstance(cultivo, Cultivo):
        raise TypeError("cultivo debe ser un objeto Cultivo.")
    resultado = diagnostico_riego(cultivo.etapa_fenologica, lote.humedad_actual, temperatura)
    if resultado is None:
        raise ValueError("Prolog no pudo evaluar el riego con esos datos.")
    nutriente = NUTRIENTES[resultado["nutriente"]]
    if nutriente:
        recomendacion = f"Fertilización sugerida en esta etapa: {nutriente}."
    else:
        recomendacion = "No se recomienda fertilizar en esta etapa."
    respuesta = {"conclusion": ACCIONES[resultado["accion"]],
                 "recomendacion": recomendacion,
                 "severidad": resultado["severidad"]}
    return Diagnostico.desde_respuesta(id, lote, "riego", respuesta)


# ------------------------------------------- plagas, enfermedades y deficiencias
def sintomas_conocidos():
    """Lista de síntomas que Prolog entiende (útil para mostrarlos en el menú
    o en la interfaz sin repetirlos en Python)."""
    salida = _ejecutar("findall(S, sintoma(S), L), atomic_list_concat(L, ',', R), write(R)")
    return salida.split(",") if salida else []


def causas_probables(sintomas):
    """Devuelve las causas compatibles con los síntomas, de la más específica a
    la menos específica. Cada causa es un diccionario con las claves
    'causa', 'tipo', 'accion', 'especificidad' y 'severidad'."""
    atomos = [_atomo(s) for s in sintomas]
    if not atomos:
        return []
    desconocidos = [a for a in atomos if a not in sintomas_conocidos()]
    if desconocidos:
        raise ValueError(f"Síntomas desconocidos: {', '.join(desconocidos)}")
    lista = "[" + ", ".join(atomos) + "]"
    objetivo = (f"findall(T, (causa_probable({lista}, C, Tipo, A, E, S), "
                "format(atom(T), '~w,~w,~w,~w,~w', [C, Tipo, A, E, S])), L), "
                "atomic_list_concat(L, ';', R), write(R)")
    salida = _ejecutar(objetivo)
    causas = []
    for bloque in (salida.split(";") if salida else []):
        causa, tipo, accion, especificidad, severidad = bloque.split(",")
        causas.append({"causa": causa, "tipo": tipo, "accion": accion,
                       "especificidad": int(especificidad), "severidad": severidad})
    return sorted(causas, key=lambda c: c["especificidad"], reverse=True)


NOMBRES_CAUSAS = {
    "deficiencia_nitrogeno": "deficiencia de nitrógeno",
    "deficiencia_fosforo": "deficiencia de fósforo",
    "deficiencia_potasio": "deficiencia de potasio",
    "deficiencia_hierro": "deficiencia de hierro",
    "pulgones": "pulgones",
    "mosca_blanca": "mosca blanca",
    "gusano_cogollero": "gusano cogollero",
    "arana_roja": "araña roja",
    "tizon": "tizón",
    "oidio": "oídio",
}

TRATAMIENTOS = {
    "aplicar_fertilizante_nitrogenado": "Aplicar fertilizante nitrogenado.",
    "aplicar_fertilizante_fosforado": "Aplicar fertilizante fosforado.",
    "aplicar_fertilizante_potasico": "Aplicar fertilizante potásico.",
    "aplicar_hierro_y_revisar_ph": "Aplicar hierro (quelato) y revisar el pH del suelo.",
    "controlar_plaga": ("Aplicar un control autorizado (mejor si es biológico) y respetar "
                        "el periodo de carencia antes de cosechar."),
    "controlar_hongos": ("Mejorar la ventilación, evitar el exceso de humedad y aplicar "
                         "un fungicida autorizado."),
}


def diagnosticar_plagas(id, lote, sintomas):
    """Devuelve un Diagnostico de tipo 'plaga_deficiencia' a partir de los
    síntomas observados."""
    if not isinstance(lote, Lote):
        raise TypeError("lote debe ser un objeto Lote.")
    causas = causas_probables(sintomas)
    if not causas:
        respuesta = {"conclusion": "No se pudo determinar una causa con los síntomas indicados",
                     "recomendacion": "Observa más síntomas o consulta a un técnico agrónomo.",
                     "severidad": "baja"}
    else:
        principal = causas[0]
        recomendacion = TRATAMIENTOS[principal["accion"]]
        otras = [NOMBRES_CAUSAS[c["causa"]] for c in causas[1:]]
        if otras:
            recomendacion += f" Otras causas posibles: {', '.join(otras)}."
        respuesta = {"conclusion": (f"Causa probable: {NOMBRES_CAUSAS[principal['causa']]} "
                                    f"({principal['tipo']})"),
                     "recomendacion": recomendacion,
                     "severidad": principal["severidad"]}
    return Diagnostico.desde_respuesta(id, lote, "plaga_deficiencia", respuesta)


if __name__ == "__main__":
    print("--- Siembra ---")
    print("¿Maíz con pH 6.5 en suelo franco?", puede_sembrar("maíz", 6.5, "franco"))
    print("Motivo con pH 5.0:", motivo_rechazo("maíz", 5.0, "franco"))
    print("Cultivos aptos (pH 6.2, franco):", cultivos_aptos(6.2, "franco"))
    print(diagnosticar_siembra(1, Lote(1, "Lote Norte", 2, "franco", 6.5, 40), "Maíz"))
    print(diagnosticar_siembra(2, Lote(2, "Lote Ácido", 1, "arenoso", 4.8, 40), "tomate"))

    print("--- Riego ---")
    maiz = Cultivo("Maíz", "criollo", "vegetativa", 30)
    frijol = Cultivo("Frijol", "rojo", "floracion", 40)
    print(diagnosticar_riego(3, Lote(1, "Lote Norte", 2, "franco", 6.5, 25), maiz, 32))
    print(diagnosticar_riego(4, Lote(1, "Lote Norte", 2, "franco", 6.5, 60), maiz, 22))
    print(diagnosticar_riego(5, Lote(1, "Lote Norte", 2, "franco", 6.5, 85), frijol, 20))

    print("--- Plagas y deficiencias ---")
    lote = Lote(1, "Lote Norte", 2, "franco", 6.5, 40)
    print("Síntomas que conoce Prolog:", len(sintomas_conocidos()))
    print(diagnosticar_plagas(6, lote, ["hojas amarillas", "hojas viejas primero", "crecimiento lento"]))
    print(diagnosticar_plagas(7, lote, ["hojas amarillas", "melaza pegajosa", "insectos blancos",
                                        "hojas enrolladas"]))
    print(diagnosticar_plagas(8, lote, ["puntos amarillos", "telarana fina"]))
    print(diagnosticar_plagas(9, lote, ["hojas amarillas"]))
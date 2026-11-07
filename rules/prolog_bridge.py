"""Enlace entre Python y SWI-Prolog (llama a swipl con subprocess)."""
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PROLOG_FILE
from models.lote import Lote
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
    """None si se puede sembrar; si no, cultivo_desconocido,
    ph_fuera_de_rango o suelo_no_apto."""
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
    """Consulta a Prolog y devuelve un objeto Diagnostico de tipo siembra."""
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


if __name__ == "__main__":
    print("¿Maíz con pH 6.5 en suelo franco?", puede_sembrar("maíz", 6.5, "franco"))
    print("Motivo con pH 5.0:", motivo_rechazo("maíz", 5.0, "franco"))
    print("Cultivos aptos (pH 6.2, franco):", cultivos_aptos(6.2, "franco"))
    print(diagnosticar_siembra(1, Lote(1, "Lote Norte", 2, "franco", 6.5, 40), "Maíz"))
    print(diagnosticar_siembra(2, Lote(2, "Lote Ácido", 1, "arenoso", 4.8, 40), "tomate"))
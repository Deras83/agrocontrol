"""Enlace entre Python y SWI-Prolog.

Primero intenta con pyswip; si falla, usa subprocess con swipl.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import PROLOG_FILE


def consultar_subprocess(goal: str) -> str:
    """Ejecuta un objetivo Prolog con swipl y devuelve la salida."""
    resultado = subprocess.run(
        ["swipl", "-q", "-g", f"consult('{PROLOG_FILE.as_posix()}'), {goal}, halt", "-t", "halt"],
        capture_output=True,
        text=True,
    )
    return (resultado.stdout + resultado.stderr).strip()


if __name__ == "__main__":
    # Prueba: debe imprimir hola_agrocontrol
    print(consultar_subprocess("saludo(X), write(X), nl"))

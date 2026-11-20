"""Parámetros generales y rutas del proyecto."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get("AGROCONTROL_DB_PATH") or BASE_DIR / "database" / "agrocontrol.db")
PROLOG_FILE = BASE_DIR / "rules" / "sistema_experto.pl"

"""Parámetros generales y rutas del proyecto."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "agrocontrol.db"
PROLOG_FILE = BASE_DIR / "rules" / "sistema_experto.pl"

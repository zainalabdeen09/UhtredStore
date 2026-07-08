import os
import sys
from pathlib import Path

# Mobile app shares database with the desktop app
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent / "data"  # Share with main UhtredStore
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'uhtred.db'}"
LOW_STOCK_THRESHOLD = 5

APP_NAME = "Uhtred Store"
APP_VERSION = "1.0.0"

DEFAULT_PRINTER = None

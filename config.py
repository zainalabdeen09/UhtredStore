import os
import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
    APP_DIR = Path(os.path.dirname(sys.executable))
else:
    BASE_DIR = Path(__file__).resolve().parent
    APP_DIR = BASE_DIR

DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATA_DIR / 'uhtred.db'}"
LOW_STOCK_THRESHOLD = 5

APP_NAME = "Uhtred Store"
APP_VERSION = "1.0.0"

DEFAULT_PRINTER = None

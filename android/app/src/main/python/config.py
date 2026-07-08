import os

DATA_DIR = os.environ.get("UHTRED_DATA_DIR",
                          os.path.join(os.path.dirname(os.path.abspath(__file__)), "data"))
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = "sqlite:///" + os.path.join(DATA_DIR, "uhtred.db")
LOW_STOCK_THRESHOLD = 5

APP_NAME = "Uhtred Store"
APP_VERSION = "1.0.0"

DEFAULT_PRINTER = None

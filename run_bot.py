import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE = Path(sys._MEIPASS)
else:
    BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from database import init_db
init_db()

from bot.main import run_bot
run_bot()

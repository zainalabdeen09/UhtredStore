import sys
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE = Path(sys._MEIPASS)
else:
    BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QIcon
from database import init_db, SessionLocal
from config import APP_NAME

init_db()

app = QApplication(sys.argv)
app.setApplicationName(APP_NAME)

icon_path = BASE / "resources" / "icon.png"
if icon_path.exists():
    app.setWindowIcon(QIcon(str(icon_path)))

font = QFont("Tahoma", 10)
app.setFont(font)

from ui.login_dialog import LoginDialog
login = LoginDialog()
if login.exec() != LoginDialog.Accepted:
    sys.exit(0)

from ui.main_window import MainWindow
db = SessionLocal()
window = MainWindow(db)
window.show()

exit_code = app.exec()
db.close()
sys.exit(exit_code)

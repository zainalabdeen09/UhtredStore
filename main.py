import sys
import threading
import socket
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE = Path(sys._MEIPASS)
else:
    BASE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont, QIcon
from database import init_db, SessionLocal
from config import APP_NAME, BASE_DIR, APP_DIR

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

# ---- Start Flask server in background ----
def start_flask_server():
    try:
        mobile_dir = BASE / "mobile"
        if mobile_dir.exists():
            sys.path.insert(0, str(mobile_dir))
        from mobile.app import app as flask_app
        flask_app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Flask server error: {e}")

thread = threading.Thread(target=start_flask_server, daemon=True)
thread.start()

# Get IP address
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    SERVER_IP = s.getsockname()[0]
    s.close()
except Exception:
    SERVER_IP = '127.0.0.1'

from ui.main_window import MainWindow
db = SessionLocal()
window = MainWindow(db, server_ip=SERVER_IP)
window.show()

exit_code = app.exec()
db.close()
sys.exit(exit_code)

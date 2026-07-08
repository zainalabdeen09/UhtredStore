from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Uhtred Store - تسجيل الدخول")
        self.setFixedSize(400, 320)
        self.setStyleSheet("""
            QDialog { background: #0f172a; }
            QLabel { color: #f1f5f9; }
            QLineEdit {
                background: #1e293b; color: #f1f5f9;
                border: 1.5px solid #475569; border-radius: 8px;
                padding: 12px 16px; font-size: 15px; min-height: 44px;
            }
            QLineEdit:focus { border: 2px solid #0ea5e9; }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0ea5e9, stop:1 #0284c7);
                color: #fff; border: none; border-radius: 8px;
                padding: 12px; font-size: 15px; font-weight: bold; min-height: 44px;
            }
            QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #38bdf8, stop:1 #0ea5e9); }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(14)

        title = QLabel("Uhtred Store")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #ffffff;")
        layout.addWidget(title)

        subtitle = QLabel("نظام إدارة المبيعات")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #64748b; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        login_btn = QPushButton("تسجيل الدخول")
        login_btn.clicked.connect(self.check_login)
        self.password_input.returnPressed.connect(login_btn.click)
        layout.addWidget(login_btn)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet("color: #ef4444; font-size: 12px;")
        layout.addWidget(self.error_label)

        layout.addStretch()

    def check_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if username == "za_c10" and password == "1942":
            self.accept()
        else:
            self.error_label.setText("اسم المستخدم أو كلمة المرور غير صحيحة")
            self.password_input.clear()

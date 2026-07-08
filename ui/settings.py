from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, QGroupBox, QMessageBox, QTextEdit, QDoubleSpinBox
from models import Setting, Category
from utils.helpers import get_setting, save_setting


class SettingsPage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("⚙️ الإعدادات")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        # Store Info
        store_group = QGroupBox("معلومات المتجر")
        store_form = QFormLayout()

        self.store_name = QLineEdit()
        store_form.addRow("اسم المتجر:", self.store_name)
        self.store_phone = QLineEdit()
        store_form.addRow("رقم الهاتف:", self.store_phone)
        self.store_address = QLineEdit()
        store_form.addRow("العنوان:", self.store_address)
        self.store_note = QLineEdit()
        store_form.addRow("ملاحظة الفاتورة:", self.store_note)
        self.tax_rate = QDoubleSpinBox()
        self.tax_rate.setMaximum(100)
        self.tax_rate.setSuffix("%")
        store_form.addRow("نسبة الضريبة:", self.tax_rate)

        save_store_btn = QPushButton("💾 حفظ معلومات المتجر")
        save_store_btn.setObjectName("btnSuccess")
        save_store_btn.clicked.connect(self.save_store_settings)
        store_form.addRow(save_store_btn)
        store_group.setLayout(store_form)
        layout.addWidget(store_group)

        # Categories
        cat_group = QGroupBox("إدارة الأصناف")
        cat_layout = QVBoxLayout()

        cat_input_layout = QHBoxLayout()
        self.cat_input = QLineEdit()
        self.cat_input.setPlaceholderText("اسم الصنف الجديد")
        cat_input_layout.addWidget(self.cat_input)

        add_cat_btn = QPushButton("➕ إضافة")
        add_cat_btn.setObjectName("btnSuccess")
        add_cat_btn.clicked.connect(self.add_category)
        cat_input_layout.addWidget(add_cat_btn)
        cat_layout.addLayout(cat_input_layout)

        self.cat_list = QLabel()
        self.cat_list.setWordWrap(True)
        cat_layout.addWidget(self.cat_list)
        cat_group.setLayout(cat_layout)
        layout.addWidget(cat_group)

        layout.addStretch()

    def on_show(self):
        self.load_settings()

    def load_settings(self):
        self.store_name.setText(get_setting(self.db, "store_name", "Uhtred Store"))
        self.store_phone.setText(get_setting(self.db, "store_phone", ""))
        self.store_address.setText(get_setting(self.db, "store_address", ""))
        self.store_note.setText(get_setting(self.db, "store_note", ""))
        self.tax_rate.setValue(float(get_setting(self.db, "tax_rate", "0")))
        self.load_categories()

    def load_categories(self):
        cats = self.db.query(Category).all()
        if cats:
            text = "  |  ".join([f"• {c.name}" for c in cats])
        else:
            text = "لا توجد أصناف بعد"
        self.cat_list.setText(text)

    def save_store_settings(self):
        save_setting(self.db, "store_name", self.store_name.text())
        save_setting(self.db, "store_phone", self.store_phone.text())
        save_setting(self.db, "store_address", self.store_address.text())
        save_setting(self.db, "store_note", self.store_note.text())
        save_setting(self.db, "tax_rate", str(self.tax_rate.value()))
        QMessageBox.information(self, "تم", "تم حفظ الإعدادات")

    def add_category(self):
        name = self.cat_input.text().strip()
        if not name:
            return
        existing = self.db.query(Category).filter(Category.name == name).first()
        if existing:
            QMessageBox.warning(self, "تنبيه", "الصنف موجود مسبقاً")
            return
        self.db.add(Category(name=name))
        self.db.commit()
        self.cat_input.clear()
        self.load_categories()

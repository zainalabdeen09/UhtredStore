from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QFormLayout, QTextEdit, QMessageBox
from models import Customer


class CustomersPage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("👤 العملاء")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث...")
        self.search_input.textChanged.connect(self.load_customers)
        toolbar.addWidget(self.search_input)

        add_btn = QPushButton("➕ إضافة عميل")
        add_btn.setObjectName("btnSuccess")
        add_btn.clicked.connect(self.add_customer)
        toolbar.addWidget(add_btn)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["#", "الاسم", "الهاتف", "العنوان", "خيارات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def on_show(self):
        self.load_customers()

    def load_customers(self):
        query = self.db.query(Customer)
        search = self.search_input.text().strip()
        if search:
            query = query.filter(Customer.name.contains(search) | Customer.phone.contains(search))
        customers = query.all()

        self.table.setRowCount(len(customers))
        for i, c in enumerate(customers):
            self.table.setItem(i, 0, QTableWidgetItem(str(c.id)))
            self.table.setItem(i, 1, QTableWidgetItem(c.name))
            self.table.setItem(i, 2, QTableWidgetItem(c.phone or "-"))
            self.table.setItem(i, 3, QTableWidgetItem(c.address or "-"))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedWidth(35)
            edit_btn.clicked.connect(lambda checked, cid=c.id: self.edit_customer(cid))
            del_btn = QPushButton("🗑️")
            del_btn.setFixedWidth(35)
            del_btn.setObjectName("btnDanger")
            del_btn.clicked.connect(lambda checked, cid=c.id: self.delete_customer(cid))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(del_btn)
            self.table.setCellWidget(i, 4, btn_widget)

    def add_customer(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("إضافة عميل")
        dialog.setMinimumWidth(400)
        form = QFormLayout(dialog)

        name_input = QLineEdit()
        form.addRow("الاسم:", name_input)
        phone_input = QLineEdit()
        form.addRow("رقم الهاتف:", phone_input)
        address_input = QTextEdit()
        address_input.setMaximumHeight(80)
        form.addRow("العنوان:", address_input)
        notes_input = QTextEdit()
        notes_input.setMaximumHeight(80)
        form.addRow("ملاحظات:", notes_input)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(dialog.reject)
        save_btn = QPushButton("💾 حفظ")
        save_btn.setObjectName("btnSuccess")

        def save():
            c = Customer(
                name=name_input.text(),
                phone=phone_input.text(),
                address=address_input.toPlainText(),
                notes=notes_input.toPlainText(),
            )
            self.db.add(c)
            self.db.commit()
            dialog.accept()
            self.load_customers()

        save_btn.clicked.connect(save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        form.addRow(btn_layout)
        dialog.exec()

    def edit_customer(self, cid):
        c = self.db.query(Customer).filter(Customer.id == cid).first()
        if not c:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"تعديل: {c.name}")
        dialog.setMinimumWidth(400)
        form = QFormLayout(dialog)

        name_input = QLineEdit(c.name)
        form.addRow("الاسم:", name_input)
        phone_input = QLineEdit(c.phone or "")
        form.addRow("رقم الهاتف:", phone_input)
        address_input = QTextEdit(c.address or "")
        address_input.setMaximumHeight(80)
        form.addRow("العنوان:", address_input)
        notes_input = QTextEdit(c.notes or "")
        notes_input.setMaximumHeight(80)
        form.addRow("ملاحظات:", notes_input)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(dialog.reject)
        save_btn = QPushButton("💾 حفظ")

        def save():
            c.name = name_input.text()
            c.phone = phone_input.text()
            c.address = address_input.toPlainText()
            c.notes = notes_input.toPlainText()
            self.db.commit()
            dialog.accept()
            self.load_customers()

        save_btn.clicked.connect(save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        form.addRow(btn_layout)
        dialog.exec()

    def delete_customer(self, cid):
        reply = QMessageBox.question(self, "تأكيد", "هل أنت متأكد من حذف هذا العميل؟")
        if reply == QMessageBox.Yes:
            c = self.db.query(Customer).filter(Customer.id == cid).first()
            if c:
                self.db.delete(c)
                self.db.commit()
                self.load_customers()

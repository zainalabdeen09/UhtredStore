from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QSpinBox, QDialog, QFormLayout, QMessageBox, QTextEdit
from models import Product, StockMovement


class StockAddPage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("📥 إضافة مخزون (مشتريات)")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث عن منتج...")
        self.search_input.textChanged.connect(self.load_products)
        toolbar.addWidget(self.search_input)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["#", "المنتج", "المخزون الحالي", "الحد الأدنى", "خيارات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def on_show(self):
        self.load_products()

    def load_products(self):
        query = self.db.query(Product)
        search = self.search_input.text().strip()
        if search:
            query = query.filter(Product.name.contains(search))
        products = query.all()

        self.table.setRowCount(len(products))
        for i, p in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(i, 1, QTableWidgetItem(p.name))
            self.table.setItem(i, 2, QTableWidgetItem(str(p.current_stock)))
            self.table.setItem(i, 3, QTableWidgetItem(str(p.min_stock)))

            btn = QPushButton("📥 إضافة")
            btn.setObjectName("btnSuccess")
            btn.clicked.connect(lambda checked, pid=p.id: self.add_stock(pid))
            self.table.setCellWidget(i, 4, btn)

    def add_stock(self, pid):
        p = self.db.query(Product).filter(Product.id == pid).first()
        if not p:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"إضافة مخزون: {p.name}")
        dialog.setMinimumWidth(350)
        form = QFormLayout(dialog)

        label = QLabel(f"المخزون الحالي: {p.current_stock}")
        label.setStyleSheet("font-weight: bold; font-size: 16px;")
        form.addRow(label)

        qty_input = QSpinBox()
        qty_input.setMinimum(1)
        qty_input.setMaximum(99999)
        qty_input.setValue(1)
        form.addRow("الكمية المضافة:", qty_input)

        ref_input = QLineEdit()
        ref_input.setPlaceholderText("رقم فاتورة الشراء")
        form.addRow("مرجع الشراء:", ref_input)

        notes_input = QTextEdit()
        notes_input.setMaximumHeight(80)
        form.addRow("ملاحظات:", notes_input)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(dialog.reject)
        save_btn = QPushButton("💾 إضافة")
        save_btn.setObjectName("btnSuccess")

        def save():
            qty = qty_input.value()
            p.current_stock += qty
            self.db.add(StockMovement(
                product_id=p.id,
                type="in",
                quantity=qty,
                reference=ref_input.text() or "",
                notes=notes_input.toPlainText(),
            ))
            self.db.commit()
            dialog.accept()
            self.load_products()

        save_btn.clicked.connect(save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        form.addRow(btn_layout)
        dialog.exec()

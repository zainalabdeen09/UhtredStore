from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QDateEdit
from PySide6.QtCore import Qt, QDate
from models import Invoice
from utils.invoice_printer import preview_invoice
from utils.helpers import get_setting


class InvoicesPage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("📄 الفواتير")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث برقم الفاتورة أو اسم العميل...")
        self.search_input.textChanged.connect(self.load_invoices)
        toolbar.addWidget(self.search_input)

        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.clicked.connect(self.load_invoices)
        toolbar.addWidget(refresh_btn)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["رقم الفاتورة", "العميل", "الإجمالي", "التاريخ", "الوقت", "خيارات"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def on_show(self):
        self.load_invoices()

    def load_invoices(self):
        query = self.db.query(Invoice).order_by(Invoice.created_at.desc())
        search = self.search_input.text().strip()
        if search:
            query = query.filter(
                Invoice.invoice_number.contains(search) |
                Invoice.customer_name.contains(search)
            )
        invoices = query.all()

        self.table.setRowCount(len(invoices))
        for i, inv in enumerate(invoices):
            self.table.setItem(i, 0, QTableWidgetItem(inv.invoice_number))
            self.table.setItem(i, 1, QTableWidgetItem(inv.customer_name or "-"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{inv.grand_total:,.0f} د.ع"))
            self.table.setItem(i, 3, QTableWidgetItem(inv.invoice_date.isoformat() if inv.invoice_date else ""))
            self.table.setItem(i, 4, QTableWidgetItem(inv.created_at.strftime("%H:%M") if inv.created_at else ""))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            print_btn = QPushButton("🖨️")
            print_btn.setFixedWidth(40)
            print_btn.clicked.connect(lambda checked, iid=inv.id: self.print_invoice(iid))
            btn_layout.addWidget(print_btn)
            self.table.setCellWidget(i, 5, btn_widget)

    def print_invoice(self, invoice_id):
        inv = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            return

        items = []
        for item in inv.items:
            items.append({
                "product_name": item.product_name,
                "quantity": item.quantity,
                "price": item.price,
                "total": item.total,
                "size": item.size,
                "color": item.color,
                "print_location": item.print_location,
            })

        inv_dict = {
            "customer_name": inv.customer_name or "",
            "customer_phone": inv.customer_phone or "",
            "customer_address": inv.customer_address or "",
            "invoice_number": inv.invoice_number,
            "invoice_date": inv.invoice_date.isoformat() if inv.invoice_date else "",
            "grand_total": inv.grand_total,
            "notes": inv.notes or "",
            "items": items,
        }
        store_dict = {
            "store_name": get_setting(self.db, "store_name", "Uhtred Store"),
            "store_phone": get_setting(self.db, "store_phone", ""),
            "store_address": get_setting(self.db, "store_address", ""),
        }
        preview_invoice(inv_dict, store_dict, self)

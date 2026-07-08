from datetime import date, timedelta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QDateEdit, QGroupBox, QGridLayout, QFrame
from PySide6.QtCore import Qt, QDate
from sqlalchemy import func
from models import Invoice, InvoiceItem, Product, Customer


class ReportsPage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)

        title = QLabel("📊 التقارير")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)

        self.stats_widgets = {}
        stats_info = [
            ("total_sales", "إجمالي المبيعات", "💰"),
            ("total_invoices", "عدد الفواتير", "📄"),
            ("total_products", "المنتجات", "📦"),
            ("total_customers", "العملاء", "👤"),
        ]
        for i, (key, label, icon) in enumerate(stats_info):
            card = QFrame()
            card.setObjectName("statCard")
            card.setMinimumHeight(100)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(18, 14, 18, 14)
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 26px; border: none; background: transparent;")
            card_layout.addWidget(icon_lbl)
            num_lbl = QLabel("0")
            num_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #0f172a; border: none; background: transparent;")
            card_layout.addWidget(num_lbl)
            name_lbl = QLabel(label)
            name_lbl.setStyleSheet("color: #64748b; font-size: 13px; border: none; background: transparent;")
            card_layout.addWidget(name_lbl)
            self.stats_widgets[key] = num_lbl
            stats_layout.addWidget(card, 0, i)

        layout.addLayout(stats_layout)

        products_group = QGroupBox("أفضل المنتجات مبيعاً")
        products_layout = QVBoxLayout()
        self.top_table = QTableWidget()
        self.top_table.setColumnCount(4)
        self.top_table.setHorizontalHeaderLabels(["المنتج", "الكمية المباعة", "الإيراد", "نسبة"])
        self.top_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.top_table.setEditTriggers(QTableWidget.NoEditTriggers)
        products_layout.addWidget(self.top_table)
        products_group.setLayout(products_layout)
        layout.addWidget(products_group)

    def on_show(self):
        self.load_stats()
        self.load_top_products()

    def load_stats(self):
        today = date.today()
        month_start = today.replace(day=1)

        total_sales = self.db.query(func.coalesce(func.sum(Invoice.grand_total), 0)).filter(
            Invoice.invoice_date >= month_start).scalar()
        total_invoices = self.db.query(func.count(Invoice.id)).filter(
            Invoice.invoice_date >= month_start).scalar()
        total_products = self.db.query(func.count(Product.id)).scalar()
        total_customers = self.db.query(func.count(Customer.id)).scalar()

        self.stats_widgets["total_sales"].setText(f"{total_sales:,.0f} د.ع")
        self.stats_widgets["total_invoices"].setText(str(total_invoices))
        self.stats_widgets["total_products"].setText(str(total_products))
        self.stats_widgets["total_customers"].setText(str(total_customers))

    def load_top_products(self):
        from sqlalchemy import desc
        results = self.db.query(
            InvoiceItem.product_name,
            func.sum(InvoiceItem.quantity).label("qty"),
            func.sum(InvoiceItem.total).label("rev"),
        ).group_by(InvoiceItem.product_name).order_by(desc("qty")).limit(15).all()

        if not results:
            grand_total = 0
        else:
            grand_total = sum(r.rev or 0 for r in results)

        self.top_table.setRowCount(len(results))
        for i, r in enumerate(results):
            self.top_table.setItem(i, 0, QTableWidgetItem(r.product_name))
            self.top_table.setItem(i, 1, QTableWidgetItem(str(int(r.qty))))
            self.top_table.setItem(i, 2, QTableWidgetItem(f"{r.rev:,.0f}"))
            pct = (r.rev / grand_total * 100) if grand_total > 0 else 0
            self.top_table.setItem(i, 3, QTableWidgetItem(f"{pct:.1f}%"))

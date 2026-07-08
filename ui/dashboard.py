from datetime import datetime, date, timedelta
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PySide6.QtCore import Qt
from sqlalchemy import func
from models import Invoice, InvoiceItem, Product, Customer


class StatCard(QFrame):
    def __init__(self, title, icon, color=""):
        super().__init__()
        self.setObjectName("statCard")
        self.setMinimumHeight(110)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)

        top = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px; border: none; background: transparent;")
        top.addWidget(icon_label)
        top.addStretch()

        self.number_label = QLabel("0")
        self.number_label.setStyleSheet(
            "font-size: 24px; font-weight: bold; color: #0f172a; border: none; background: transparent;")
        top.addWidget(self.number_label)

        layout.addLayout(top)
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #64748b; font-size: 13px; border: none; background: transparent;")
        layout.addWidget(self.title_label)


class DashboardPage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)

        title = QLabel("🏠 الرئيسية")
        title.setObjectName("pageTitle")
        layout.addWidget(title)
        subtitle = QLabel("ملخص مبيعات وأداء المتجر")
        subtitle.setStyleSheet("color: #64748b; font-size: 14px; margin: 0 0 12px 0;")
        layout.addWidget(subtitle)

        self.cards_layout = QGridLayout()
        self.cards_layout.setSpacing(16)
        layout.addLayout(self.cards_layout)

        self.stat_cards = {}
        stats = [
            ("today_sales", "مبيعات اليوم", "💰"),
            ("today_orders", "طلبات اليوم", "📋"),
            ("total_products", "إجمالي المنتجات", "📦"),
            ("low_stock", "منتجات منخفضة", "⚠️"),
            ("total_customers", "العملاء", "👤"),
            ("month_sales", "مبيعات الشهر", "📊"),
        ]
        for i, (key, label, icon) in enumerate(stats):
            card = StatCard(label, icon)
            self.stat_cards[key] = card
            self.cards_layout.addWidget(card, i // 3, i % 3)

        layout.addSpacing(16)
        recent_title = QLabel("آخر الفواتير")
        recent_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #0f172a; margin-top: 6px;")
        layout.addWidget(recent_title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["رقم الفاتورة", "العميل", "الإجمالي", "التاريخ", "الوقت"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def on_show(self):
        self.load_stats()
        self.load_recent_invoices()

    def load_stats(self):
        today = date.today()
        month_start = today.replace(day=1)

        today_total = self.db.query(func.coalesce(func.sum(Invoice.grand_total), 0)).filter(
            func.date(Invoice.created_at) == today).scalar()
        month_total = self.db.query(func.coalesce(func.sum(Invoice.grand_total), 0)).filter(
            Invoice.invoice_date >= month_start).scalar()
        today_count = self.db.query(func.count(Invoice.id)).filter(
            func.date(Invoice.created_at) == today).scalar()
        total_products = self.db.query(func.count(Product.id)).scalar()
        low_stock = self.db.query(func.count(Product.id)).filter(
            Product.current_stock <= Product.min_stock).scalar()
        total_customers = self.db.query(func.count(Customer.id)).scalar()

        self.stat_cards["today_sales"].number_label.setText(f"{today_total:,.0f} د.ع")
        self.stat_cards["today_orders"].number_label.setText(str(today_count))
        self.stat_cards["total_products"].number_label.setText(str(total_products))
        self.stat_cards["low_stock"].number_label.setText(str(low_stock))
        self.stat_cards["total_customers"].number_label.setText(str(total_customers))
        self.stat_cards["month_sales"].number_label.setText(f"{month_total:,.0f} د.ع")

    def load_recent_invoices(self):
        invoices = self.db.query(Invoice).order_by(Invoice.created_at.desc()).limit(20).all()
        self.table.setRowCount(len(invoices))
        for i, inv in enumerate(invoices):
            self.table.setItem(i, 0, QTableWidgetItem(inv.invoice_number))
            self.table.setItem(i, 1, QTableWidgetItem(inv.customer_name or "-"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{inv.grand_total:,.0f}"))
            self.table.setItem(i, 3, QTableWidgetItem(inv.invoice_date.isoformat() if inv.invoice_date else ""))
            self.table.setItem(i, 4, QTableWidgetItem(inv.created_at.strftime("%H:%M") if inv.created_at else ""))

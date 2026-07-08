import sys
from pathlib import Path
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QFrame, QScrollArea
from PySide6.QtCore import Qt

from ui.dashboard import DashboardPage
from ui.pos import POSPage
from ui.products import ProductsPage
from ui.invoices import InvoicesPage
from ui.customers import CustomersPage
from ui.reports import ReportsPage
from ui.inventory import InventoryPage
from ui.stock_add import StockAddPage
from ui.settings import SettingsPage


NAV_ITEMS = [
    ("🏠", "الرئيسية", "dashboard"),
    ("🛒", "نقطة البيع", "pos"),
    ("📦", "المنتجات", "products"),
    ("📋", "المخزون الكامل", "inventory"),
    ("📥", "إضافة مخزون", "stock_add"),
    ("📄", "الفواتير", "invoices"),
    ("👤", "العملاء", "customers"),
    ("📊", "التقارير", "reports"),
    ("⚙️", "الإعدادات", "settings"),
]


class MainWindow(QMainWindow):
    def __init__(self, db, server_ip="127.0.0.1"):
        super().__init__()
        self.db = db
        self.setWindowTitle(f"Uhtred Store - {server_ip}:5000 - نظام إدارة المبيعات")
        self.setMinimumSize(1024, 600)
        self.resize(1200, 700)
        self.setStyleSheet(self._load_qss())

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(190)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        title = QLabel("Uhtred Store")
        title.setObjectName("appTitle")
        subtitle = QLabel("نظام إدارة المبيعات")
        subtitle.setObjectName("appSubtitle")

        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(subtitle)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(0)

        self.nav_buttons = {}
        for icon, label, name in NAV_ITEMS:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, n=name: self.switch_page(n))
            self.nav_buttons[name] = btn
            scroll_layout.addWidget(btn)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        sidebar_layout.addWidget(scroll)
        main_layout.addWidget(sidebar)

        content = QFrame()
        content.setObjectName("content")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked = QStackedWidget()

        self.pages = {}
        page_classes = {
            "dashboard": DashboardPage,
            "pos": POSPage,
            "products": ProductsPage,
            "invoices": InvoicesPage,
            "customers": CustomersPage,
            "reports": ReportsPage,
            "inventory": InventoryPage,
            "stock_add": StockAddPage,
            "settings": SettingsPage,
        }
        for key, cls in page_classes.items():
            widget = cls(self.db, self)
            self.pages[key] = widget
            self.stacked.addWidget(widget)

        content_layout.addWidget(self.stacked)
        main_layout.addWidget(content, 1)

        self.switch_page("dashboard")

    def switch_page(self, name):
        for n, btn in self.nav_buttons.items():
            btn.setChecked(n == name)
        self.stacked.setCurrentWidget(self.pages[name])
        if hasattr(self.pages[name], "on_show"):
            self.pages[name].on_show()

    def _load_qss(self):
        if getattr(sys, 'frozen', False):
            style_path = Path(sys._MEIPASS) / "resources" / "style.qss"
        else:
            style_path = Path(__file__).resolve().parent.parent / "resources" / "style.qss"
        if style_path.exists():
            return open(str(style_path), encoding="utf-8").read()
        return ""

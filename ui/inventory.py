from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QMessageBox
from PySide6.QtCore import Qt
from models import Product, StockMovement

from utils.invoice_printer import build_invoice_html
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextBrowser
from PySide6.QtCore import Qt


class InventoryPage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("📋 المخزون الكامل")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث...")
        self.search_input.textChanged.connect(self.load_inventory)
        toolbar.addWidget(self.search_input)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("🔵 كل المنتجات", "all")
        self.filter_combo.addItem("🟡 منخفضة المخزون", "low")
        self.filter_combo.addItem("🔴 مصفرة (0)", "zero")
        self.filter_combo.currentIndexChanged.connect(self.load_inventory)
        toolbar.addWidget(self.filter_combo)

        print_btn = QPushButton("🖨️ طباعة الجرد")
        print_btn.setObjectName("btnPrimary")
        print_btn.clicked.connect(self.print_inventory)
        toolbar.addWidget(print_btn)

        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["#", "المنتج", "الصنف", "سعر البيع", "سعر الشراء", "المخزون", "الحد الأدنى"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

    def on_show(self):
        self.load_inventory()

    def load_inventory(self):
        query = self.db.query(Product)
        search = self.search_input.text().strip()
        if search:
            query = query.filter(Product.name.contains(search))

        filt = self.filter_combo.currentData()
        if filt == "low":
            query = query.filter(Product.current_stock <= Product.min_stock, Product.current_stock > 0)
        elif filt == "zero":
            query = query.filter(Product.current_stock == 0)

        products = query.all()

        self.table.setRowCount(len(products))
        total_value = 0
        for i, p in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id)))
            self.table.setItem(i, 1, QTableWidgetItem(p.name))
            cat_name = p.category.name if p.category else "-"
            self.table.setItem(i, 2, QTableWidgetItem(cat_name))
            self.table.setItem(i, 3, QTableWidgetItem(f"{p.sell_price:,.0f}"))
            self.table.setItem(i, 4, QTableWidgetItem(f"{p.buy_price:,.0f}"))
            stock_item = QTableWidgetItem(str(p.current_stock))
            if p.current_stock == 0:
                stock_item.setBackground(Qt.red)
                stock_item.setForeground(Qt.white)
            elif p.current_stock <= p.min_stock:
                stock_item.setBackground(Qt.yellow)
            self.table.setItem(i, 5, stock_item)
            self.table.setItem(i, 6, QTableWidgetItem(str(p.min_stock)))
            total_value += p.current_stock * p.buy_price

    def print_inventory(self):
        products = self.db.query(Product).order_by(Product.name).all()
        rows = ""
        total_value = 0
        zero_count = 0
        low_count = 0
        for i, p in enumerate(products, 1):
            row_class = ""
            if p.current_stock == 0:
                row_class = ' class="zero"'
            elif p.current_stock <= p.min_stock:
                row_class = ' class="low"'
            rows += f"""
            <tr{row_class}>
                <td>{i}</td>
                <td>{p.name}</td>
                <td>{p.category.name if p.category else '-'}</td>
                <td>{p.current_stock}</td>
                <td>{p.min_stock}</td>
                <td>{p.buy_price:,.0f}</td>
                <td>{p.sell_price:,.0f}</td>
                <td>{(p.current_stock * p.buy_price):,.0f}</td>
            </tr>"""
            total_value += p.current_stock * p.buy_price
            if p.current_stock == 0:
                zero_count += 1
            elif p.current_stock <= p.min_stock:
                low_count += 1

        today = __import__('datetime').date.today().isoformat()
        year = __import__('datetime').date.today().year

        html = f"""<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="UTF-8">
<title>جرد المخزون - {today}</title>
<style>
    @page {{ size: A4 landscape; margin: 10mm; }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: 'Traditional Arabic', 'Tahoma', 'Arial', sans-serif;
        direction: rtl;
        color: #000;
        padding: 0;
    }}
    .header {{
        text-align: center;
        border-bottom: 3px solid #000;
        padding-bottom: 12px;
        margin-bottom: 14px;
    }}
    .header h1 {{ font-size: 22px; font-weight: bold; color: #000; margin: 0; }}
    .header h3 {{ font-size: 14px; font-weight: normal; color: #000; margin: 4px 0 0 0; }}
    .summary {{
        text-align: center;
        margin: 10px 0 14px 0;
        padding: 8px;
        border: 2px solid #000;
        font-size: 14px;
        font-weight: bold;
    }}
    .summary span {{ margin: 0 10px; }}
    table {{
        width: 100%;
        border-collapse: collapse;
        font-size: 15px;
    }}
    th {{
        background: #000;
        color: #fff;
        padding: 10px 6px;
        font-size: 15px;
        font-weight: bold;
        text-align: center;
        border: 1px solid #000;
    }}
    td {{
        padding: 8px 6px;
        text-align: center;
        border: 1px solid #000;
        font-size: 15px;
        color: #000;
    }}
    tr:nth-child(even) td {{ background: #f5f5f5; }}
    tr.zero td {{ background: #ffe0e0; font-weight: bold; }}
    tr.low td {{ background: #fff8e0; }}
    .footer {{
        margin-top: 14px;
        text-align: center;
        border-top: 2px solid #000;
        padding-top: 8px;
        font-size: 11px;
    }}
    @media print {{
        body {{ margin: 0; padding: 0; }}
        .no-print {{ display: none; }}
    }}
</style>
</head>
<body>
<div class="header">
    <h1>Uhtred Store - جرد المخزون</h1>
    <h3>تاريخ الجرد: {today}</h3>
</div>
<div class="summary">
    <span>إجمالي المنتجات: {len(products)}</span>
    <span>|</span>
    <span>قيمة المخزون: {total_value:,.0f} د.ع</span>
    <span>|</span>
    <span style="color:#c00;">مصفرة: {zero_count}</span>
    <span>|</span>
    <span style="color:#b8860b;">منخفضة: {low_count}</span>
</div>
<table>
<thead>
<tr>
    <th style="width:30px;">#</th>
    <th>المنتج</th>
    <th style="width:60px;">الصنف</th>
    <th style="width:50px;">المخزون</th>
    <th style="width:55px;">الحد</th>
    <th style="width:65px;">سعر الشراء</th>
    <th style="width:65px;">سعر البيع</th>
    <th style="width:75px;">القيمة</th>
</tr>
</thead>
<tbody>{rows}</tbody>
</table>
<div class="footer">
    <strong>Uhtred Store</strong> &copy; {year}
</div>
</body>
</html>"""

        import tempfile, webbrowser
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8")
        tmp.write(html)
        tmp_path = tmp.name
        tmp.close()
        webbrowser.open(f"file:///{tmp_path.replace(chr(92), '/')}")
        QMessageBox.information(self, "طباعة الجرد", "تم فتح الجرد في المتصفح.\nاضغط Ctrl+P للطباعة بحجم A4.")

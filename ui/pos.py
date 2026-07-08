import json
from datetime import date
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QComboBox, QSpinBox, QFrame, QMessageBox, QGroupBox, QGridLayout, QScrollArea
from PySide6.QtCore import Qt
from models import Product, Customer, Invoice, InvoiceItem, StockMovement
from utils.helpers import generate_invoice_number
from utils.invoice_printer import preview_invoice, print_invoice


class POSPage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        self.cart = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)

        title = QLabel("🛒 نقطة البيع")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        content = QHBoxLayout()

        # Left panel - Products
        left = QVBoxLayout()
        left_group = QGroupBox("المنتجات")
        left_group_layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث عن منتج...")
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(self.search_input)

        self.category_filter = QComboBox()
        self.category_filter.addItem("كل الأصناف", "all")
        self.category_filter.currentIndexChanged.connect(self.search_products)
        search_layout.addWidget(self.category_filter)
        left_group_layout.addLayout(search_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.products_container = QWidget()
        self.products_grid = QGridLayout(self.products_container)
        self.products_grid.setSpacing(10)
        scroll.setWidget(self.products_container)

        left_group_layout.addWidget(scroll)
        left_group.setLayout(left_group_layout)
        left.addWidget(left_group)
        content.addLayout(left, 3)

        # Right panel - Cart
        right = QVBoxLayout()
        right_group = QGroupBox("الفاتورة الحالية")
        right_layout = QVBoxLayout()

        self.customer_name = QLineEdit()
        self.customer_name.setPlaceholderText("اسم العميل")
        right_layout.addWidget(self.customer_name)

        self.customer_phone = QLineEdit()
        self.customer_phone.setPlaceholderText("رقم الهاتف")
        right_layout.addWidget(self.customer_phone)

        self.customer_address = QLineEdit()
        self.customer_address.setPlaceholderText("عنوان الزبون")
        right_layout.addWidget(self.customer_address)

        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(7)
        self.cart_table.setHorizontalHeaderLabels(["المنتج", "المقاس", "اللون", "مكان الطباعة", "الكمية", "السعر", "الإجمالي"])
        self.cart_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.cart_table.setAlternatingRowColors(True)
        right_layout.addWidget(self.cart_table)

        total_layout = QHBoxLayout()
        total_layout.addWidget(QLabel("الإجمالي:"))
        self.total_label = QLabel("0.00 د.ع")
        self.total_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #0284c7;")
        total_layout.addWidget(self.total_label)
        total_layout.addStretch()
        right_layout.addLayout(total_layout)

        btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton("🧹 تفريغ")
        self.clear_btn.setObjectName("btnDanger")
        self.clear_btn.clicked.connect(self.clear_cart)
        btn_layout.addWidget(self.clear_btn)

        self.sell_btn = QPushButton("💾 حفظ الفاتورة")
        self.sell_btn.setObjectName("btnSuccess")
        self.sell_btn.clicked.connect(self.save_invoice)
        btn_layout.addWidget(self.sell_btn)

        self.print_btn = QPushButton("🖨️ حفظ وطباعة")
        self.print_btn.setObjectName("btnPrimary")
        self.print_btn.clicked.connect(self.save_and_print)
        btn_layout.addWidget(self.print_btn)

        right_layout.addLayout(btn_layout)
        right_group.setLayout(right_layout)
        right.addWidget(right_group)
        content.addLayout(right, 2)

        layout.addLayout(content)

    def on_show(self):
        self.load_categories()
        self.load_products()

    def load_categories(self):
        from models import Category
        self.category_filter.clear()
        self.category_filter.addItem("كل الأصناف", "all")
        cats = self.db.query(Category).all()
        for c in cats:
            self.category_filter.addItem(c.name, c.id)

    def load_products(self):
        query = self.db.query(Product).filter(Product.current_stock > 0)
        cat_id = self.category_filter.currentData()
        if cat_id != "all":
            query = query.filter(Product.category_id == cat_id)
        search = self.search_input.text().strip()
        if search:
            query = query.filter(Product.name.contains(search))
        products = query.all()

        self.clear_grid()
        for i, p in enumerate(products):
            self.add_product_card(p, i)

    def search_products(self):
        self.load_products()

    def clear_grid(self):
        while self.products_grid.count():
            item = self.products_grid.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

    def add_product_card(self, product, idx):
        card = QFrame()
        card.setObjectName("productCard")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        card.setStyleSheet("""
            QFrame#productCard {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 12px;
            }
            QFrame#productCard:hover {
                border: 1.5px solid #0ea5e9;
                background: #fafcff;
            }
        """)
        clayout = QVBoxLayout(card)
        clayout.setContentsMargins(10, 8, 10, 8)
        clayout.setSpacing(4)

        name_label = QLabel(product.name)
        name_label.setStyleSheet(
            "font-weight: bold; font-size: 13px; color: #0f172a; border: none; background: transparent;")
        name_label.setWordWrap(True)
        clayout.addWidget(name_label)

        price_label = QLabel(f"{product.sell_price:,.0f} د.ع")
        price_label.setStyleSheet(
            "color: #059669; font-weight: bold; font-size: 15px; border: none; background: transparent;")
        clayout.addWidget(price_label)

        stock_label = QLabel(f"المخزون: {product.current_stock}")
        stock_label.setStyleSheet("color: #64748b; font-size: 11px; border: none; background: transparent;")
        clayout.addWidget(stock_label)

        card.mousePressEvent = lambda e, p=product: self.add_to_cart(p)

        cols = 3
        row = idx // cols
        col = idx % cols
        self.products_grid.addWidget(card, row, col)

    def add_to_cart(self, product):
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox

        dialog = QDialog(self)
        dialog.setWindowTitle(f"إضافة: {product.name}")
        dialog.setMinimumWidth(420)
        dialog.setStyleSheet("QDialog { background: #ffffff; }")
        layout = QVBoxLayout(dialog)
        layout.setSpacing(12)

        layout.addWidget(QLabel(f"<b>المنتج:</b> {product.name}"))
        layout.addWidget(QLabel(f"<b>السعر:</b> {product.sell_price:,.0f} د.ع"))
        layout.addWidget(QLabel(f"<b>المخزون:</b> {product.current_stock}"))

        size_cb = QComboBox()
        sizes = json.loads(product.sizes) if product.sizes else ["واحد"]
        for s in sizes:
            size_cb.addItem(s)
        layout.addWidget(QLabel("المقاس:"))
        layout.addWidget(size_cb)

        color_cb = QComboBox()
        colors = json.loads(product.colors) if product.colors else ["عادي"]
        for c in colors:
            color_cb.addItem(c)
        layout.addWidget(QLabel("اللون:"))
        layout.addWidget(color_cb)

        print_cb = QComboBox()
        prints = json.loads(product.print_locations) if product.print_locations else ["بدون"]
        for p in prints:
            print_cb.addItem(p)
        layout.addWidget(QLabel("مكان الطباعة:"))
        layout.addWidget(print_cb)

        qty_input = QSpinBox()
        qty_input.setMinimum(1)
        qty_input.setMaximum(product.current_stock)
        qty_input.setValue(1)
        layout.addWidget(QLabel("الكمية:"))
        layout.addWidget(qty_input)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(dialog.reject)
        add_btn = QPushButton("➕ إضافة للفاتورة")
        add_btn.setObjectName("btnSuccess")

        def confirm():
            self.cart.append({
                "product_id": product.id,
                "product_name": product.name,
                "size": size_cb.currentText(),
                "color": color_cb.currentText(),
                "print_location": print_cb.currentText(),
                "quantity": qty_input.value(),
                "price": product.sell_price,
                "total": product.sell_price * qty_input.value(),
            })
            self.refresh_cart_table()
            dialog.accept()

        add_btn.clicked.connect(confirm)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

        dialog.exec()

    def refresh_cart_table(self):
        self.cart_table.setRowCount(len(self.cart))
        total = 0
        for i, item in enumerate(self.cart):
            self.cart_table.setItem(i, 0, QTableWidgetItem(item["product_name"]))
            self.cart_table.setItem(i, 1, QTableWidgetItem(item["size"]))
            self.cart_table.setItem(i, 2, QTableWidgetItem(item["color"]))
            self.cart_table.setItem(i, 3, QTableWidgetItem(item["print_location"]))
            self.cart_table.setItem(i, 4, QTableWidgetItem(str(item["quantity"])))
            self.cart_table.setItem(i, 5, QTableWidgetItem(f"{item['price']:,.0f}"))
            self.cart_table.setItem(i, 6, QTableWidgetItem(f"{item['total']:,.0f}"))
            total += item["total"]
        self.total_label.setText(f"{total:,.0f} د.ع")

    def clear_cart(self):
        self.cart = []
        self.refresh_cart_table()

    def _do_save(self, should_print=False):
        if not self.cart:
            QMessageBox.warning(self, "تنبيه", "الفاتورة فارغة!")
            return

        total = sum(item["total"] for item in self.cart)

        from utils.helpers import get_setting
        tax_rate = float(get_setting(self.db, "tax_rate", "0"))
        tax = total * (tax_rate / 100)
        grand_total = total + tax

        customer_name = self.customer_name.text().strip() or "نقدي"
        customer_phone = self.customer_phone.text().strip() or ""
        customer_address = self.customer_address.text().strip() or ""

        store_name = get_setting(self.db, "store_name", "Uhtred Store")

        invoice = Invoice(
            invoice_number=generate_invoice_number(self.db),
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            total=total,
            discount=0,
            tax=tax,
            grand_total=grand_total,
            invoice_date=date.today(),
        )
        self.db.add(invoice)
        self.db.flush()

        for item in self.cart:
            ii = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item["product_id"],
                product_name=item["product_name"],
                quantity=item["quantity"],
                price=item["price"],
                total=item["total"],
                size=item.get("size", ""),
                color=item.get("color", ""),
                print_location=item.get("print_location", ""),
            )
            self.db.add(ii)

            product = self.db.query(Product).filter(Product.id == item["product_id"]).first()
            if product:
                product.current_stock -= item["quantity"]
                self.db.add(StockMovement(
                    product_id=product.id,
                    type="out",
                    quantity=-item["quantity"],
                    reference=invoice.invoice_number,
                ))

        self.db.commit()

        if should_print:
            inv_dict = {
                "customer_name": customer_name,
                "customer_phone": customer_phone,
                "customer_address": customer_address,
                "invoice_number": invoice.invoice_number,
                "invoice_date": invoice.invoice_date.isoformat(),
                "grand_total": grand_total,
                "notes": "",
                "items": [
                    {
                        "product_name": item["product_name"],
                        "quantity": item["quantity"],
                        "price": item["price"],
                        "total": item["total"],
                        "size": item.get("size", ""),
                        "color": item.get("color", ""),
                        "print_location": item.get("print_location", ""),
                    }
                    for item in self.cart
                ],
            }
            store_dict = {
                "store_name": get_setting(self.db, "store_name", "Uhtred Store"),
                "store_phone": get_setting(self.db, "store_phone", ""),
                "store_address": get_setting(self.db, "store_address", ""),
            }
            preview_invoice(inv_dict, store_dict, self)

        QMessageBox.information(self, "تم", f"تم حفظ الفاتورة رقم {invoice.invoice_number}")
        self.clear_cart()
        self.customer_name.clear()
        self.customer_phone.clear()
        self.customer_address.clear()
        self.load_products()

    def save_invoice(self):
        self._do_save(should_print=False)

    def save_and_print(self):
        self._do_save(should_print=True)

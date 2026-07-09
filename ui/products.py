import json
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QDialog, QFormLayout, QDoubleSpinBox, QSpinBox, QMessageBox, QTextEdit, QFileDialog
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from models import Product, Category, StockMovement
from config import PRODUCT_IMAGES_DIR


class ProductsPage(QWidget):
    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main = main_window
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)

        title = QLabel("📦 المنتجات")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        toolbar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 بحث...")
        self.search_input.textChanged.connect(self.load_products)
        toolbar.addWidget(self.search_input)

        add_btn = QPushButton("➕ إضافة منتج")
        add_btn.setObjectName("btnSuccess")
        add_btn.clicked.connect(self.add_product)
        toolbar.addWidget(add_btn)
        layout.addLayout(toolbar)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels(["#", "الصورة", "الاسم", "الصنف", "سعر الشراء", "سعر البيع", "المخزون", "الحد الأدنى", "خيارات"])
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
        self.table.setRowHeight(60)
        for i, p in enumerate(products):
            self.table.setItem(i, 0, QTableWidgetItem(str(p.id)))

            img_label = QLabel()
            img_label.setFixedSize(50, 50)
            img_label.setAlignment(Qt.AlignCenter)
            if p.image:
                img_path = PRODUCT_IMAGES_DIR / p.image
                if img_path.exists():
                    pix = QPixmap(str(img_path)).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    img_label.setPixmap(pix)
            else:
                img_label.setText("📷")
            self.table.setCellWidget(i, 1, img_label)

            self.table.setItem(i, 2, QTableWidgetItem(p.name))
            cat_name = p.category.name if p.category else "-"
            self.table.setItem(i, 3, QTableWidgetItem(cat_name))
            self.table.setItem(i, 4, QTableWidgetItem(f"{p.buy_price:,.0f}"))
            self.table.setItem(i, 5, QTableWidgetItem(f"{p.sell_price:,.0f}"))
            stock_item = QTableWidgetItem(str(p.current_stock))
            if p.current_stock <= p.min_stock:
                stock_item.setForeground(Qt.red)
            self.table.setItem(i, 6, stock_item)
            self.table.setItem(i, 7, QTableWidgetItem(str(p.min_stock)))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(2, 2, 2, 2)
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedWidth(35)
            edit_btn.clicked.connect(lambda checked, pid=p.id: self.edit_product(pid))
            del_btn = QPushButton("🗑️")
            del_btn.setFixedWidth(35)
            del_btn.setObjectName("btnDanger")
            del_btn.clicked.connect(lambda checked, pid=p.id: self.delete_product(pid))
            btn_layout.addWidget(edit_btn)
            btn_layout.addWidget(del_btn)
            self.table.setCellWidget(i, 8, btn_widget)

    def add_product(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("إضافة منتج جديد")
        dialog.setMinimumWidth(450)
        form = QFormLayout(dialog)

        name_input = QLineEdit()
        form.addRow("الاسم:", name_input)

        from models import Category
        cat_combo = __import__("PySide6.QtWidgets", fromlist=["QComboBox"]).QComboBox()
        cats = self.db.query(Category).all()
        for c in cats:
            cat_combo.addItem(c.name, c.id)
        form.addRow("الصنف:", cat_combo)

        buy_input = QDoubleSpinBox()
        buy_input.setMaximum(999999)
        form.addRow("سعر الشراء:", buy_input)

        sell_input = QDoubleSpinBox()
        sell_input.setMaximum(999999)
        form.addRow("سعر البيع:", sell_input)

        stock_input = QSpinBox()
        stock_input.setMaximum(99999)
        form.addRow("المخزون الحالي:", stock_input)

        min_input = QSpinBox()
        min_input.setMaximum(99999)
        min_input.setValue(5)
        form.addRow("الحد الأدنى:", min_input)

        sizes_input = QLineEdit()
        sizes_input.setPlaceholderText("S, M, L, XL")
        form.addRow("المقاسات (مفصولة بفاصلة):", sizes_input)

        colors_input = QLineEdit()
        colors_input.setPlaceholderText("أحمر, أزرق, أسود")
        form.addRow("الألوان (مفصولة بفاصلة):", colors_input)

        prints_input = QLineEdit()
        prints_input.setPlaceholderText("أمامي, خلفي, كم")
        form.addRow("أماكن الطباعة (مفصولة بفاصلة):", prints_input)

        notes_input = QTextEdit()
        notes_input.setMaximumHeight(80)
        form.addRow("ملاحظات:", notes_input)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(dialog.reject)
        save_btn = QPushButton("💾 حفظ")
        save_btn.setObjectName("btnSuccess")

        def save():
            sizes = [s.strip() for s in sizes_input.text().split(",") if s.strip()]
            colors = [c.strip() for c in colors_input.text().split(",") if c.strip()]
            prints = [p.strip() for p in prints_input.text().split(",") if p.strip()]

            p = Product(
                name=name_input.text(),
                category_id=cat_combo.currentData() if cat_combo.currentData() != -1 else None,
                buy_price=buy_input.value(),
                sell_price=sell_input.value(),
                current_stock=stock_input.value(),
                min_stock=min_input.value(),
                sizes=json.dumps(sizes),
                colors=json.dumps(colors),
                print_locations=json.dumps(prints),
                notes=notes_input.toPlainText(),
            )
            self.db.add(p)
            if stock_input.value() > 0:
                self.db.add(StockMovement(
                    product=p, type="in", quantity=stock_input.value(),
                    reference="initial", notes="الافتتاحية"
                ))
            self.db.commit()
            dialog.accept()
            self.load_products()

        save_btn.clicked.connect(save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        form.addRow(btn_layout)
        dialog.exec()

    def edit_product(self, pid):
        p = self.db.query(Product).filter(Product.id == pid).first()
        if not p:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"تعديل: {p.name}")
        dialog.setMinimumWidth(450)
        form = QFormLayout(dialog)

        name_input = QLineEdit(p.name)
        form.addRow("الاسم:", name_input)

        from models import Category
        cat_combo = __import__("PySide6.QtWidgets", fromlist=["QComboBox"]).QComboBox()
        cats = self.db.query(Category).all()
        for c in cats:
            cat_combo.addItem(c.name, c.id)
        if p.category_id:
            idx = cat_combo.findData(p.category_id)
            if idx >= 0:
                cat_combo.setCurrentIndex(idx)
        form.addRow("الصنف:", cat_combo)

        sell_input = QDoubleSpinBox()
        sell_input.setMaximum(999999)
        sell_input.setValue(p.sell_price)
        form.addRow("سعر البيع:", sell_input)

        buy_input = QDoubleSpinBox()
        buy_input.setMaximum(999999)
        buy_input.setValue(p.buy_price)
        form.addRow("سعر الشراء:", buy_input)

        min_input = QSpinBox()
        min_input.setMaximum(99999)
        min_input.setValue(p.min_stock)
        form.addRow("الحد الأدنى:", min_input)

        sizes_input = QLineEdit(", ".join(json.loads(p.sizes)) if p.sizes else "")
        form.addRow("المقاسات:", sizes_input)

        colors_input = QLineEdit(", ".join(json.loads(p.colors)) if p.colors else "")
        form.addRow("الألوان:", colors_input)

        prints_input = QLineEdit(", ".join(json.loads(p.print_locations)) if p.print_locations else "")
        form.addRow("الطباعة:", prints_input)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(dialog.reject)
        save_btn = QPushButton("💾 حفظ")

        def save():
            p.name = name_input.text()
            p.category_id = cat_combo.currentData() if cat_combo.currentData() != -1 else None
            p.sell_price = sell_input.value()
            p.buy_price = buy_input.value()
            p.min_stock = min_input.value()
            p.sizes = json.dumps([s.strip() for s in sizes_input.text().split(",") if s.strip()])
            p.colors = json.dumps([c.strip() for c in colors_input.text().split(",") if c.strip()])
            p.print_locations = json.dumps([x.strip() for x in prints_input.text().split(",") if x.strip()])
            self.db.commit()
            dialog.accept()
            self.load_products()

        save_btn.clicked.connect(save)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        form.addRow(btn_layout)
        dialog.exec()

    def delete_product(self, pid):
        reply = QMessageBox.question(self, "تأكيد", "هل أنت متأكد من حذف هذا المنتج؟")
        if reply == QMessageBox.Yes:
            p = self.db.query(Product).filter(Product.id == pid).first()
            if p:
                self.db.delete(p)
                self.db.commit()
                self.load_products()

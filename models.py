from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Date, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from database import Base


class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, default="")
    type = Column(String(20), default="text")


class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(50), default="")
    address = Column(Text, default="")
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(300), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    buy_price = Column(Float, default=0.0)
    sell_price = Column(Float, default=0.0)
    current_stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=5)
    sizes = Column(Text, default="")       # JSON: ["S","M","L","XL"]
    colors = Column(Text, default="")      # JSON: ["أحمر","أزرق","أسود"]
    print_locations = Column(Text, default="")  # JSON: ["أمامي","خلفي","كم"]
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    category = relationship("Category")


class StockMovement(Base):
    __tablename__ = "stock_movements"
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    type = Column(String(20), nullable=False)  # "in" (purchase) or "out" (sale) or "adjust"
    quantity = Column(Integer, nullable=False)
    reference = Column(String(200), default="")  # invoice number or purchase ref
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")


class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    customer_name = Column(String(200), default="")
    customer_phone = Column(String(50), default="")
    customer_address = Column(Text, default="")
    total = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    invoice_date = Column(Date, default=date.today)

    customer = relationship("Customer")
    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceItem(Base):
    __tablename__ = "invoice_items"
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(300), nullable=False)
    quantity = Column(Integer, default=1)
    price = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    size = Column(String(50), default="")
    color = Column(String(50), default="")
    print_location = Column(String(100), default="")

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("Product")

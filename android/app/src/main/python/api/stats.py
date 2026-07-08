from flask import Blueprint, jsonify
from database import SessionLocal
from models import Product, Customer, Invoice
from datetime import datetime, date

stats_bp = Blueprint('stats', __name__, url_prefix='/api/stats')

@stats_bp.route('/dashboard', methods=['GET'])
def dashboard():
    db = SessionLocal()
    try:
        today = date.today()
        today_start = datetime(today.year, today.month, today.day)

        today_invoices = db.query(Invoice).filter(Invoice.created_at >= today_start).all()
        today_sales = sum(inv.grand_total for inv in today_invoices)
        today_orders = len(today_invoices)

        total_products = db.query(Product).count()
        low_stock = db.query(Product).filter(Product.current_stock < Product.min_stock).count()
        total_customers = db.query(Customer).count()

        month_start = datetime(today.year, today.month, 1)
        month_invoices = db.query(Invoice).filter(Invoice.created_at >= month_start).all()
        month_sales = sum(inv.grand_total for inv in month_invoices)

        return jsonify({
            'today_sales': today_sales,
            'today_orders': today_orders,
            'total_products': total_products,
            'low_stock': low_stock,
            'total_customers': total_customers,
            'month_sales': month_sales
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

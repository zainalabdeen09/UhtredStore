from flask import Blueprint, jsonify
from database import SessionLocal
from models import InvoiceItem
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@reports_bp.route('/top-products', methods=['GET'])
def top_products():
    db = SessionLocal()
    try:
        results = db.query(
            InvoiceItem.product_id,
            InvoiceItem.product_name,
            func.sum(InvoiceItem.quantity).label('total_qty'),
            func.sum(InvoiceItem.total).label('total_sales')
        ).group_by(
            InvoiceItem.product_id, InvoiceItem.product_name
        ).order_by(
            func.sum(InvoiceItem.total).desc()
        ).limit(20).all()

        data = []
        for r in results:
            data.append({
                'product_id': r.product_id,
                'product_name': r.product_name,
                'total_quantity': int(r.total_qty),
                'total_sales': float(r.total_sales)
            })
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

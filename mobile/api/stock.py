from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Product, StockMovement

stock_bp = Blueprint('stock', __name__, url_prefix='/api/stock')

@stock_bp.route('/add', methods=['POST'])
def add_stock():
    db = SessionLocal()
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        product_id = data.get('product_id')
        quantity = data.get('quantity', 0)
        notes = data.get('notes', '')

        if not product_id:
            return jsonify({'error': 'product_id is required'}), 400
        if quantity <= 0:
            return jsonify({'error': 'quantity must be positive'}), 400

        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404

        product.current_stock += quantity

        movement = StockMovement(
            product_id=product_id,
            type='in',
            quantity=quantity,
            reference='Manual add',
            notes=notes
        )
        db.add(movement)
        db.commit()

        return jsonify({
            'message': 'Stock added',
            'product_id': product.id,
            'current_stock': product.current_stock
        })
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

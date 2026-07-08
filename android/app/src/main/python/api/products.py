from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Product

products_bp = Blueprint('products', __name__, url_prefix='/api/products')

@products_bp.route('', methods=['GET'])
def list_products():
    db = SessionLocal()
    try:
        query = db.query(Product)
        search = request.args.get('search', '')
        category_id = request.args.get('category_id', type=int)

        if search:
            query = query.filter(Product.name.ilike(f'%{search}%'))
        if category_id:
            query = query.filter(Product.category_id == category_id)

        products = query.order_by(Product.id.desc()).all()
        result = []
        for p in products:
            result.append({
                'id': p.id,
                'name': p.name,
                'category_id': p.category_id,
                'category_name': p.category.name if p.category else None,
                'buy_price': p.buy_price,
                'sell_price': p.sell_price,
                'current_stock': p.current_stock,
                'min_stock': p.min_stock,
                'sizes': p.sizes,
                'colors': p.colors,
                'print_locations': p.print_locations,
                'notes': p.notes,
                'created_at': p.created_at.isoformat() if p.created_at else None
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    db = SessionLocal()
    try:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            return jsonify({'error': 'Product not found'}), 404
        return jsonify({
            'id': p.id,
            'name': p.name,
            'category_id': p.category_id,
            'category_name': p.category.name if p.category else None,
            'buy_price': p.buy_price,
            'sell_price': p.sell_price,
            'current_stock': p.current_stock,
            'min_stock': p.min_stock,
            'sizes': p.sizes,
            'colors': p.colors,
            'print_locations': p.print_locations,
            'notes': p.notes,
            'created_at': p.created_at.isoformat() if p.created_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('', methods=['POST'])
def create_product():
    db = SessionLocal()
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        product = Product(
            name=data.get('name', ''),
            category_id=data.get('category_id'),
            buy_price=data.get('buy_price', 0.0),
            sell_price=data.get('sell_price', 0.0),
            current_stock=data.get('current_stock', 0),
            min_stock=data.get('min_stock', 5),
            sizes=data.get('sizes', ''),
            colors=data.get('colors', ''),
            print_locations=data.get('print_locations', ''),
            notes=data.get('notes', '')
        )
        db.add(product)
        db.commit()
        return jsonify({'id': product.id, 'message': 'Product created'}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        product.name = data.get('name', product.name)
        product.category_id = data.get('category_id', product.category_id)
        product.buy_price = data.get('buy_price', product.buy_price)
        product.sell_price = data.get('sell_price', product.sell_price)
        product.current_stock = data.get('current_stock', product.current_stock)
        product.min_stock = data.get('min_stock', product.min_stock)
        product.sizes = data.get('sizes', product.sizes)
        product.colors = data.get('colors', product.colors)
        product.print_locations = data.get('print_locations', product.print_locations)
        product.notes = data.get('notes', product.notes)
        db.commit()
        return jsonify({'message': 'Product updated'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@products_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        db.delete(product)
        db.commit()
        return jsonify({'message': 'Product deleted'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

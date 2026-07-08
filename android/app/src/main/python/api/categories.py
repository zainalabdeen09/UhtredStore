from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Category

categories_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

@categories_bp.route('', methods=['GET'])
def list_categories():
    db = SessionLocal()
    try:
        categories = db.query(Category).all()
        return jsonify([{'id': c.id, 'name': c.name} for c in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@categories_bp.route('', methods=['POST'])
def create_category():
    db = SessionLocal()
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Category name is required'}), 400
        category = Category(name=data['name'])
        db.add(category)
        db.commit()
        return jsonify({'id': category.id, 'name': category.name, 'message': 'Category created'}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@categories_bp.route('/<int:category_id>', methods=['DELETE'])
def delete_category(category_id):
    db = SessionLocal()
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        db.delete(category)
        db.commit()
        return jsonify({'message': 'Category deleted'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

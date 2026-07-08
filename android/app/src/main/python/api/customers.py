from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Customer

customers_bp = Blueprint('customers', __name__, url_prefix='/api/customers')

@customers_bp.route('', methods=['GET'])
def list_customers():
    db = SessionLocal()
    try:
        query = db.query(Customer)
        search = request.args.get('search', '')
        if search:
            query = query.filter(
                Customer.name.ilike(f'%{search}%') |
                Customer.phone.ilike(f'%{search}%')
            )
        customers = query.order_by(Customer.id.desc()).all()
        result = []
        for c in customers:
            result.append({
                'id': c.id,
                'name': c.name,
                'phone': c.phone,
                'address': c.address,
                'notes': c.notes,
                'created_at': c.created_at.isoformat() if c.created_at else None
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@customers_bp.route('', methods=['POST'])
def create_customer():
    db = SessionLocal()
    try:
        data = request.get_json()
        if not data or not data.get('name'):
            return jsonify({'error': 'Customer name is required'}), 400
        customer = Customer(
            name=data['name'],
            phone=data.get('phone', ''),
            address=data.get('address', ''),
            notes=data.get('notes', '')
        )
        db.add(customer)
        db.commit()
        return jsonify({
            'id': customer.id,
            'name': customer.name,
            'phone': customer.phone,
            'address': customer.address,
            'notes': customer.notes,
            'message': 'Customer created'
        }), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        customer.name = data.get('name', customer.name)
        customer.phone = data.get('phone', customer.phone)
        customer.address = data.get('address', customer.address)
        customer.notes = data.get('notes', customer.notes)
        db.commit()
        return jsonify({'message': 'Customer updated'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    db = SessionLocal()
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        db.delete(customer)
        db.commit()
        return jsonify({'message': 'Customer deleted'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

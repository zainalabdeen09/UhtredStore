from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Invoice, InvoiceItem, Product, StockMovement, Customer
from datetime import date
from utils.helpers import generate_invoice_number, get_setting
from utils.invoice_printer import build_invoice_html

invoices_bp = Blueprint('invoices', __name__, url_prefix='/api/invoices')

@invoices_bp.route('', methods=['GET'])
def list_invoices():
    db = SessionLocal()
    try:
        query = db.query(Invoice)
        search = request.args.get('search', '')
        if search:
            query = query.filter(
                Invoice.invoice_number.ilike(f'%{search}%') |
                Invoice.customer_name.ilike(f'%{search}%') |
                Invoice.customer_phone.ilike(f'%{search}%')
            )
        invoices = query.order_by(Invoice.id.desc()).all()
        result = []
        for inv in invoices:
            result.append({
                'id': inv.id,
                'invoice_number': inv.invoice_number,
                'customer_name': inv.customer_name,
                'customer_phone': inv.customer_phone,
                'total': inv.total,
                'discount': inv.discount,
                'tax': inv.tax,
                'grand_total': inv.grand_total,
                'notes': inv.notes,
                'created_at': inv.created_at.isoformat() if inv.created_at else None,
                'invoice_date': inv.invoice_date.isoformat() if inv.invoice_date else None
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@invoices_bp.route('/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    db = SessionLocal()
    try:
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            return jsonify({'error': 'Invoice not found'}), 404
        items = []
        for item in inv.items:
            items.append({
                'id': item.id,
                'product_id': item.product_id,
                'product_name': item.product_name,
                'quantity': item.quantity,
                'price': item.price,
                'total': item.total,
                'size': item.size,
                'color': item.color,
                'print_location': item.print_location
            })
        return jsonify({
            'id': inv.id,
            'invoice_number': inv.invoice_number,
            'customer_id': inv.customer_id,
            'customer_name': inv.customer_name,
            'customer_phone': inv.customer_phone,
            'customer_address': inv.customer_address,
            'total': inv.total,
            'discount': inv.discount,
            'tax': inv.tax,
            'grand_total': inv.grand_total,
            'notes': inv.notes,
            'created_at': inv.created_at.isoformat() if inv.created_at else None,
            'invoice_date': inv.invoice_date.isoformat() if inv.invoice_date else None,
            'items': items
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@invoices_bp.route('', methods=['POST'])
def create_invoice():
    db = SessionLocal()
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        cart = data.get('items', [])
        if not cart:
            return jsonify({'error': 'Cart is empty'}), 400

        invoice_number = generate_invoice_number(db)

        subtotal = 0.0
        for item in cart:
            qty = item.get('quantity', 1)
            price = item.get('price', 0)
            subtotal += qty * price

        discount = data.get('discount', 0.0)
        tax_rate = float(get_setting(db, 'tax_rate', '0'))
        tax = subtotal * (tax_rate / 100.0)
        grand_total = subtotal - discount + tax

        customer_id = data.get('customer_id')
        customer_name = data.get('customer_name', '')
        customer_phone = data.get('customer_phone', '')
        customer_address = data.get('customer_address', '')

        if customer_id:
            customer = db.query(Customer).filter(Customer.id == customer_id).first()
            if customer:
                customer_name = customer.name
                customer_phone = customer.phone
                customer_address = customer.address

        invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=customer_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_address=customer_address,
            total=subtotal,
            discount=discount,
            tax=tax,
            grand_total=grand_total,
            notes=data.get('notes', ''),
            invoice_date=date.today()
        )
        db.add(invoice)
        db.flush()

        for item in cart:
            product_id = item.get('product_id')
            qty = item.get('quantity', 1)
            price = item.get('price', 0)
            item_total = qty * price
            product_name = item.get('product_name', '')

            if product_id:
                product = db.query(Product).filter(Product.id == product_id).first()
                if product:
                    product_name = product.name
                    product.current_stock -= qty

                    movement = StockMovement(
                        product_id=product_id,
                        type='out',
                        quantity=qty,
                        reference=invoice_number,
                        notes='Sale'
                    )
                    db.add(movement)

            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=product_id,
                product_name=product_name,
                quantity=qty,
                price=price,
                total=item_total,
                size=item.get('size', ''),
                color=item.get('color', ''),
                print_location=item.get('print_location', '')
            )
            db.add(invoice_item)

        db.commit()
        return jsonify({'id': invoice.id, 'invoice_number': invoice_number, 'message': 'Invoice created'}), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@invoices_bp.route('/<int:invoice_id>', methods=['DELETE'])
def delete_invoice(invoice_id):
    db = SessionLocal()
    try:
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            return jsonify({'error': 'الفاتورة غير موجودة'}), 404

        # Restore stock for each item
        for item in inv.items:
            if item.product_id:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    product.current_stock += item.quantity
                    movement = StockMovement(
                        product_id=item.product_id,
                        type='in',
                        quantity=item.quantity,
                        reference=f"DELETE-{inv.invoice_number}",
                        notes='إلغاء فاتورة'
                    )
                    db.add(movement)

        db.delete(inv)
        db.commit()
        return jsonify({'message': 'تم حذف الفاتورة وإرجاع المخزون'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@invoices_bp.route('/<int:invoice_id>/print', methods=['GET'])
def print_invoice(invoice_id):
    db = SessionLocal()
    try:
        inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not inv:
            return jsonify({'error': 'Invoice not found'}), 404

        items = []
        for item in inv.items:
            items.append({
                'product_name': item.product_name,
                'quantity': item.quantity,
                'price': item.price,
                'total': item.total,
                'size': item.size,
                'color': item.color,
                'print_location': item.print_location
            })

        invoice_dict = {
            'invoice_number': inv.invoice_number,
            'customer_name': inv.customer_name,
            'customer_phone': inv.customer_phone,
            'customer_address': inv.customer_address,
            'invoice_date': inv.invoice_date.isoformat() if inv.invoice_date else '',
            'grand_total': inv.grand_total,
            'notes': inv.notes,
            'items': items
        }

        store = {
            'store_name': get_setting(db, 'store_name', 'Uhtred Store'),
            'store_phone': get_setting(db, 'store_phone', ''),
            'store_address': get_setting(db, 'store_address', '')
        }

        html = build_invoice_html(invoice_dict, store)
        return html, 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

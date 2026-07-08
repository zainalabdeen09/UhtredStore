from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Setting

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

@settings_bp.route('', methods=['GET'])
def get_settings():
    db = SessionLocal()
    try:
        settings = db.query(Setting).all()
        result = {}
        for s in settings:
            result[s.key] = s.value
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@settings_bp.route('', methods=['POST'])
def save_settings():
    db = SessionLocal()
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        for key, value in data.items():
            setting = db.query(Setting).filter(Setting.key == key).first()
            if setting:
                setting.value = str(value)
            else:
                db.add(Setting(key=key, value=str(value), type='text'))
        db.commit()
        return jsonify({'message': 'Settings saved'})
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

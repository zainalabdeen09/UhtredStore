from flask import Blueprint, request, jsonify

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

VALID_USERNAME = 'za_c10'
VALID_PASSWORD = '1942'

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        username = data.get('username', '')
        password = data.get('password', '')
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            return jsonify({'success': True})
        return jsonify({'success': False}), 401
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

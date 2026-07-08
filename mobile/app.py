import sys
sys.path.insert(0, '..')

from flask import Flask, send_from_directory, render_template
from flask_cors import CORS
from database import init_db
from api.auth import auth_bp
from api.stats import stats_bp
from api.products import products_bp
from api.categories import categories_bp
from api.customers import customers_bp
from api.invoices import invoices_bp
from api.stock import stock_bp
from api.settings import settings_bp
from api.reports import reports_bp

app = Flask(__name__, static_folder='static')
CORS(app)

init_db()

app.register_blueprint(auth_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(products_bp)
app.register_blueprint(categories_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(invoices_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(reports_bp)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    print('=' * 50)
    print('  Uhtred Store - Server Running!')
    print('=' * 50)
    print(f'  Computer: http://localhost:5000')
    print(f'  Phone:    http://{ip}:5000')
    print('=' * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

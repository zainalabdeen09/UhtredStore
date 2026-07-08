import os
import sys

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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(__name__,
                static_folder=os.path.join(BASE_DIR, "static"),
                template_folder=os.path.join(BASE_DIR, "templates"))
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

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/<path:path>")
    def static_files(path):
        return send_from_directory("static", path)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=False)

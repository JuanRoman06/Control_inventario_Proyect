from flask import Flask
from config import Config
from database.db import db
from flask_cors import CORS
from models.producto import Producto
from models.venta import Venta

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

db.init_app(app)

from routes.productos import productos_bp
from routes.ventas import ventas_bp

app.register_blueprint(productos_bp, url_prefix='/productos')
app.register_blueprint(ventas_bp, url_prefix='/ventas')

@app.route('/')
def home():
    return "API de dulceria funcionando"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
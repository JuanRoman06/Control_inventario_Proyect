from pathlib import Path
import os
from flask import Flask
from sqlalchemy import inspect, text
from config import Config
from database.db import db
from flask_cors import CORS
from models.producto import Producto
from models.venta import Venta
from models.movimiento import Movimiento
from models.compra import Compra
from models.categoria import Categoria
from models.usuario import Usuario


FRONTEND_DIR = Path(__file__).resolve().parent.parent / 'frontend'

app = Flask(
    __name__,
    static_folder=str(FRONTEND_DIR),
    static_url_path=''
)
app.config.from_object(Config)

CORS(app, supports_credentials=True, origins=Config.CORS_ORIGINS)

db.init_app(app)

from routes.productos import productos_bp
from routes.ventas import ventas_bp
from routes.dashboard import dashboard_bp
from routes.movimientos import movimientos_bp
from routes.compras import compras_bp
from routes.exportaciones import exportaciones_bp
from routes.categorias import categorias_bp
from routes.auth import auth_bp

app.register_blueprint(productos_bp, url_prefix='/productos')
app.register_blueprint(ventas_bp, url_prefix='/ventas')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(movimientos_bp, url_prefix='/movimientos')
app.register_blueprint(compras_bp, url_prefix='/compras')
app.register_blueprint(exportaciones_bp, url_prefix='/exportaciones')
app.register_blueprint(categorias_bp, url_prefix='/categorias')
app.register_blueprint(auth_bp, url_prefix='/auth')


@app.route('/')
def home():
    return app.send_static_file('index.html')


@app.route('/api/health')
def health():
    return {"mensaje": "API de dulceria funcionando"}


def ensure_schema():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()

    if 'productos' in table_names:
        producto_columns = {column['name'] for column in inspector.get_columns('productos')}

        producto_migrations = {
            'categoria_id': 'ALTER TABLE productos ADD COLUMN categoria_id INTEGER',
            'costo': 'ALTER TABLE productos ADD COLUMN costo INTEGER DEFAULT 0 NOT NULL',
            'stock_minimo': 'ALTER TABLE productos ADD COLUMN stock_minimo INTEGER DEFAULT 5 NOT NULL',
            'proveedor': 'ALTER TABLE productos ADD COLUMN proveedor VARCHAR(120)',
            'sku': 'ALTER TABLE productos ADD COLUMN sku VARCHAR(80)'
        }

        for column_name, statement in producto_migrations.items():
            if column_name not in producto_columns:
                db.session.execute(text(statement))

        db.session.execute(text('UPDATE productos SET costo = 0 WHERE costo IS NULL'))
        db.session.execute(text('UPDATE productos SET stock_minimo = 5 WHERE stock_minimo IS NULL'))

    if 'ventas' in table_names:
        venta_columns = {column['name'] for column in inspector.get_columns('ventas')}

        venta_migrations = {
            'precio_unitario': 'ALTER TABLE ventas ADD COLUMN precio_unitario INTEGER DEFAULT 0 NOT NULL',
            'costo_unitario': 'ALTER TABLE ventas ADD COLUMN costo_unitario INTEGER DEFAULT 0 NOT NULL'
        }

        for column_name, statement in venta_migrations.items():
            if column_name not in venta_columns:
                db.session.execute(text(statement))

        db.session.execute(text("""
            UPDATE ventas
            SET precio_unitario = COALESCE(
                (SELECT productos.precio FROM productos WHERE productos.id = ventas.producto_id),
                0
            )
            WHERE precio_unitario IS NULL OR precio_unitario = 0
        """))
        db.session.execute(text("""
            UPDATE ventas
            SET costo_unitario = COALESCE(
                (SELECT productos.costo FROM productos WHERE productos.id = ventas.producto_id),
                0
            )
            WHERE costo_unitario IS NULL
        """))

    if 'productos' in table_names or 'ventas' in table_names:
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_schema()
    app.run(debug=True, use_reloader=False, port=int(os.getenv('PORT', 5001)))

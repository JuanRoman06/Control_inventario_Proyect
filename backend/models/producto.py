from database.db import db

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    costo = db.Column(db.Integer, default=0, nullable=False)
    stock = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=5, nullable=False)
    proveedor = db.Column(db.String(120), nullable=True)
    sku = db.Column(db.String(80), nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=True)

    ventas = db.relationship('Venta', back_populates='producto', lazy=True)
    movimientos = db.relationship('Movimiento', back_populates='producto', lazy=True)
    categoria = db.relationship('Categoria', back_populates='productos')

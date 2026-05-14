from database.db import db

class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    stock = db.Column(db.Integer, default=0)

    ventas = db.relationship('Venta', back_populates='producto', lazy=True)
    movimientos = db.relationship('Movimiento', backref='producto_rel', lazy=True)
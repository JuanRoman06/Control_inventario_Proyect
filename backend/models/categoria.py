from database.db import db


class Categoria(db.Model):
    __tablename__ = 'categorias'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)

    productos = db.relationship('Producto', back_populates='categoria', lazy=True)
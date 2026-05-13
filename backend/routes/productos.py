from flask import Blueprint, jsonify, request
from models.producto import Producto
from database.db import db

productos_bp = Blueprint('productos', __name__)


@productos_bp.route('/', methods=['POST'])
def crear_producto():
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

    nombre = data.get('nombre')
    precio = data.get('precio')
    stock = data.get('stock', 0)

    if not nombre:
        return jsonify({"mensaje": "El nombre es obligatorio"}), 400

    if precio is None:
        return jsonify({"mensaje": "El precio es obligatorio"}), 400

    if not isinstance(precio, int) or precio < 0:
        return jsonify({"mensaje": "El precio debe ser un número entero mayor o igual a 0"}), 400

    if not isinstance(stock, int) or stock < 0:
        return jsonify({"mensaje": "El stock debe ser un número entero mayor o igual a 0"}), 400

    nuevo_producto = Producto(
        nombre=nombre,
        precio=precio,
        stock=stock
    )

    db.session.add(nuevo_producto)
    db.session.commit()

    return jsonify({"mensaje": "Producto creado"}), 201


@productos_bp.route('/', methods=['GET'])
def listar_productos():
    productos = Producto.query.all()

    resultado = []
    for p in productos:
        resultado.append({
            "id": p.id,
            "nombre": p.nombre,
            "precio": p.precio,
            "stock": p.stock
        })

    return jsonify(resultado)


@productos_bp.route('/<int:id>', methods=['PUT', 'DELETE'])
def manejar_producto(id):
    producto = Producto.query.get_or_404(id)

    if request.method == 'PUT':
        data = request.get_json()

        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        nombre = data.get('nombre', producto.nombre)
        precio = data.get('precio', producto.precio)
        stock = data.get('stock', producto.stock)

        if not nombre:
            return jsonify({"mensaje": "El nombre no puede estar vacío"}), 400

        if not isinstance(precio, int) or precio < 0:
            return jsonify({"mensaje": "El precio debe ser un número entero mayor o igual a 0"}), 400

        if not isinstance(stock, int) or stock < 0:
            return jsonify({"mensaje": "El stock debe ser un número entero mayor o igual a 0"}), 400

        producto.nombre = nombre
        producto.precio = precio
        producto.stock = stock

        db.session.commit()

        return jsonify({"mensaje": "Producto actualizado"})

    elif request.method == 'DELETE':
        db.session.delete(producto)
        db.session.commit()

        return jsonify({"mensaje": "Producto eliminado"})


@productos_bp.route('/<int:id>/vender', methods=['PUT'])
def vender_producto(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json() or {}
    cantidad = data.get("cantidad", 1)

    if not isinstance(cantidad, int) or cantidad <= 0:
        return jsonify({"mensaje": "La cantidad debe ser un número entero mayor a 0"}), 400

    if producto.stock >= cantidad:
        producto.stock -= cantidad
        db.session.commit()
        return jsonify({"mensaje": "Venta realizada", "cantidad": cantidad})
    else:
        return jsonify({"mensaje": "Sin stock disponible"}), 400
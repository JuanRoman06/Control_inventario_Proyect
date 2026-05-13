from flask import Blueprint, jsonify, request
from models.producto import Producto
from database.db import db
from models.venta import Venta

productos_bp = Blueprint('productos', __name__)


@productos_bp.route('/', methods=['POST'])
def crear_producto():
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "Debes enviar un JSON válido"}), 400

    nombre = data.get('nombre')
    precio = data.get('precio')
    stock = data.get('stock', 0)

    if not nombre or not isinstance(nombre, str) or not nombre.strip():
        return jsonify({"mensaje": "El nombre es obligatorio"}), 400

    if precio is None or not isinstance(precio, int) or precio < 0:
        return jsonify({"mensaje": "El precio debe ser un número entero mayor o igual a 0"}), 400

    if not isinstance(stock, int) or stock < 0:
        return jsonify({"mensaje": "El stock debe ser un número entero mayor o igual a 0"}), 400

    nuevo_producto = Producto(
        nombre=nombre.strip(),
        precio=precio,
        stock=stock
    )

    db.session.add(nuevo_producto)
    db.session.commit()

    return jsonify({
        "mensaje": "Producto creado",
        "producto": {
            "id": nuevo_producto.id,
            "nombre": nuevo_producto.nombre,
            "precio": nuevo_producto.precio,
            "stock": nuevo_producto.stock
        }
    }), 201

@productos_bp.route('/', methods=['GET'])
def listar_productos():
    nombre = request.args.get('nombre')
    stock_bajo = request.args.get('stock_bajo', type=int)
    orden = request.args.get('orden')
    direccion = request.args.get('direccion', 'asc')

    query = Producto.query

    if nombre:
        query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))

    if stock_bajo is not None:
        query = query.filter(Producto.stock <= stock_bajo)

    if orden in ['nombre', 'precio', 'stock']:
        columna = getattr(Producto, orden)

        if direccion == 'desc':
            query = query.order_by(columna.desc())
        else:
            query = query.order_by(columna.asc())

    productos = query.all()

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

        if not isinstance(nombre, str) or not nombre.strip():
            return jsonify({"mensaje": "El nombre no puede estar vacío"}), 400

        if not isinstance(precio, int) or precio < 0:
            return jsonify({"mensaje": "El precio debe ser un número entero mayor o igual a 0"}), 400

        if not isinstance(stock, int) or stock < 0:
            return jsonify({"mensaje": "El stock debe ser un número entero mayor o igual a 0"}), 400

        producto.nombre = nombre.strip()
        producto.precio = precio
        producto.stock = stock

        db.session.commit()

        return jsonify({
            "mensaje": "Producto actualizado",
            "producto": {
                "id": producto.id,
                "nombre": producto.nombre,
                "precio": producto.precio,
                "stock": producto.stock
            }
        })

    elif request.method == 'DELETE':
        db.session.delete(producto)
        db.session.commit()

        return jsonify({"mensaje": "Producto eliminado"})


@productos_bp.route('/<int:id>/vender', methods=['PUT'])
def vender_producto(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json() or {}
    cantidad = data.get("cantidad")

    if cantidad is None:
        return jsonify({"mensaje": "Debes enviar la cantidad"}), 400

    if not isinstance(cantidad, int) or cantidad <= 0:
        return jsonify({"mensaje": "La cantidad debe ser un número entero mayor a 0"}), 400

    if producto.stock >= cantidad:
        producto.stock -= cantidad

        nueva_venta = Venta(
            producto_id=producto.id,
            cantidad=cantidad
        )

        db.session.add(nueva_venta)
        db.session.commit()

        return jsonify({
            "mensaje": "Venta realizada",
            "venta": {
                "id": nueva_venta.id,
                "producto_id": nueva_venta.producto_id,
                "cantidad": nueva_venta.cantidad,
                "fecha": nueva_venta.fecha
            },
            "producto": {
                "id": producto.id,
                "nombre": producto.nombre,
                "precio": producto.precio,
                "stock": producto.stock
            }
        })
    else:
        return jsonify({"mensaje": "Sin stock disponible"}), 400

@productos_bp.route('/<int:id>', methods=['GET'])
def obtener_producto(id):
    producto = Producto.query.get_or_404(id)

    return jsonify({
        "id": producto.id,
        "nombre": producto.nombre,
        "precio": producto.precio,
        "stock": producto.stock
    })

@productos_bp.route('/<int:id>/stock', methods=['PUT'])
def agregar_stock(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json() or {}
    cantidad = data.get("cantidad")

    if cantidad is None:
        return jsonify({"mensaje": "Debes enviar la cantidad"}), 400

    if not isinstance(cantidad, int) or cantidad <= 0:
        return jsonify({"mensaje": "La cantidad debe ser un número entero mayor a 0"}), 400

    producto.stock += cantidad
    db.session.commit()

    return jsonify({
        "mensaje": "Stock actualizado",
        "producto": {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "stock": producto.stock
        }
    })

@productos_bp.route('/<int:id>/ventas', methods=['GET'])
def obtener_ventas_producto(id):
    producto = Producto.query.get_or_404(id)

    resultado = []
    for venta in producto.ventas:
        resultado.append({
            "id": venta.id,
            "cantidad": venta.cantidad,
            "fecha": venta.fecha
        })

    return jsonify({
        "producto": {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": producto.precio,
            "stock": producto.stock
        },
        "ventas": resultado
    })
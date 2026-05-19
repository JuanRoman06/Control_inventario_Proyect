from flask import Blueprint, jsonify, request
from models.producto import Producto
from models.categoria import Categoria
from database.db import db
from models.venta import Venta
from models.movimiento import Movimiento
from utils.auth import login_requerido

productos_bp = Blueprint('productos', __name__)


def _texto_opcional(valor):
    if valor is None:
        return None

    if not isinstance(valor, str):
        return None

    valor = valor.strip()
    return valor or None


def producto_a_json(producto):
    precio_venta = producto.precio or 0
    costo = producto.costo or 0

    return {
        "id": producto.id,
        "nombre": producto.nombre,
        "precio": precio_venta,
        "precio_venta": precio_venta,
        "costo": costo,
        "stock": producto.stock,
        "stock_minimo": producto.stock_minimo,
        "proveedor": producto.proveedor,
        "sku": producto.sku,
        "utilidad_unitaria": precio_venta - costo,
        "valor_inventario": precio_venta * producto.stock,
        "costo_inventario": costo * producto.stock,
        "categoria_id": producto.categoria_id,
        "categoria": {
            "id": producto.categoria.id,
            "nombre": producto.categoria.nombre
        } if producto.categoria else None
    }


def venta_a_json(venta):
    precio_unitario = venta.precio_unitario or 0
    costo_unitario = venta.costo_unitario or 0

    return {
        "id": venta.id,
        "producto_id": venta.producto_id,
        "cantidad": venta.cantidad,
        "precio_unitario": precio_unitario,
        "costo_unitario": costo_unitario,
        "total": precio_unitario * venta.cantidad,
        "utilidad": (precio_unitario - costo_unitario) * venta.cantidad,
        "fecha": venta.fecha
    }


@productos_bp.route('/', methods=['POST'])
@login_requerido
def crear_producto():
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "Debes enviar un JSON válido"}), 400

    nombre = data.get('nombre')
    precio = data.get('precio_venta', data.get('precio'))
    costo = data.get('costo', 0)
    stock = data.get('stock', 0)
    stock_minimo = data.get('stock_minimo', 5)
    proveedor = _texto_opcional(data.get('proveedor'))
    sku = _texto_opcional(data.get('sku'))
    categoria_id = data.get('categoria_id')

    if not nombre or not isinstance(nombre, str) or not nombre.strip():
        return jsonify({"mensaje": "El nombre es obligatorio"}), 400

    if precio is None or not isinstance(precio, int) or precio < 0:
        return jsonify({"mensaje": "El precio de venta debe ser un número entero mayor o igual a 0"}), 400

    if costo is None:
        costo = 0

    if not isinstance(costo, int) or costo < 0:
        return jsonify({"mensaje": "El costo debe ser un número entero mayor o igual a 0"}), 400

    if not isinstance(stock, int) or stock < 0:
        return jsonify({"mensaje": "El stock debe ser un número entero mayor o igual a 0"}), 400

    if stock_minimo is None:
        stock_minimo = 5

    if not isinstance(stock_minimo, int) or stock_minimo < 0:
        return jsonify({"mensaje": "El stock mínimo debe ser un número entero mayor o igual a 0"}), 400

    if sku and Producto.query.filter_by(sku=sku).first():
        return jsonify({"mensaje": "Ya existe un producto con ese SKU o código"}), 400

    categoria = None
    if categoria_id is not None and categoria_id != "":
        categoria = Categoria.query.get(categoria_id)
        if not categoria:
            return jsonify({"mensaje": "La categoría no existe"}), 400

    nuevo_producto = Producto(
        nombre=nombre.strip(),
        precio=precio,
        costo=costo,
        stock=stock,
        stock_minimo=stock_minimo,
        proveedor=proveedor,
        sku=sku,
        categoria_id=categoria.id if categoria else None
    )

    db.session.add(nuevo_producto)
    db.session.commit()

    if stock > 0:
        movimiento_inicial = Movimiento(
            producto_id=nuevo_producto.id,
            tipo="entrada",
            cantidad=stock,
            motivo="Stock inicial"
        )
        db.session.add(movimiento_inicial)
        db.session.commit()

    return jsonify({
        "mensaje": "Producto creado",
        "producto": producto_a_json(nuevo_producto)
    }), 201

@productos_bp.route('/', methods=['GET'])
@login_requerido
def listar_productos():
    nombre = request.args.get('nombre')
    stock_bajo = request.args.get('stock_bajo', type=int)
    orden = request.args.get('orden')
    direccion = request.args.get('direccion', 'asc')
    categoria_id = request.args.get('categoria_id', type=int)
    proveedor = request.args.get('proveedor')
    sku = request.args.get('sku')

    query = Producto.query

    if nombre:
        query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))

    if stock_bajo is not None:
        query = query.filter(Producto.stock <= stock_bajo)

    if categoria_id is not None:
        query = query.filter(Producto.categoria_id == categoria_id)

    if proveedor:
        query = query.filter(Producto.proveedor.ilike(f"%{proveedor}%"))

    if sku:
        query = query.filter(Producto.sku.ilike(f"%{sku}%"))

    ordenes = {
        'nombre': Producto.nombre,
        'precio': Producto.precio,
        'precio_venta': Producto.precio,
        'costo': Producto.costo,
        'stock': Producto.stock,
        'stock_minimo': Producto.stock_minimo
    }

    if orden in ordenes:
        columna = ordenes[orden]

        if direccion == 'desc':
            query = query.order_by(columna.desc())
        else:
            query = query.order_by(columna.asc())

    productos = query.all()

    return jsonify([producto_a_json(p) for p in productos])


@productos_bp.route('/<int:id>', methods=['PUT', 'DELETE'])
@login_requerido
def manejar_producto(id):
    producto = Producto.query.get_or_404(id)

    if request.method == 'PUT':
        data = request.get_json()

        if not data:
            return jsonify({"mensaje": "No se enviaron datos JSON"}), 400

        nombre = data.get('nombre', producto.nombre)
        precio = data.get('precio_venta', data.get('precio', producto.precio))
        costo = data.get('costo', producto.costo)
        stock = data.get('stock', producto.stock)
        stock_minimo = data.get('stock_minimo', producto.stock_minimo)
        proveedor = _texto_opcional(data.get('proveedor', producto.proveedor))
        sku = _texto_opcional(data.get('sku', producto.sku))
        categoria_id = data.get('categoria_id', producto.categoria_id)

        if not isinstance(nombre, str) or not nombre.strip():
            return jsonify({"mensaje": "El nombre no puede estar vacío"}), 400

        if not isinstance(precio, int) or precio < 0:
            return jsonify({"mensaje": "El precio de venta debe ser un número entero mayor o igual a 0"}), 400

        if not isinstance(costo, int) or costo < 0:
            return jsonify({"mensaje": "El costo debe ser un número entero mayor o igual a 0"}), 400

        if not isinstance(stock, int) or stock < 0:
            return jsonify({"mensaje": "El stock debe ser un número entero mayor o igual a 0"}), 400

        if not isinstance(stock_minimo, int) or stock_minimo < 0:
            return jsonify({"mensaje": "El stock mínimo debe ser un número entero mayor o igual a 0"}), 400

        if sku and Producto.query.filter(Producto.sku == sku, Producto.id != id).first():
            return jsonify({"mensaje": "Ya existe otro producto con ese SKU o código"}), 400

        categoria = None
        if categoria_id is not None and categoria_id != "":
            categoria = Categoria.query.get(categoria_id)
            if not categoria:
                return jsonify({"mensaje": "La categoría no existe"}), 400

        stock_anterior = producto.stock
        diferencia = stock - stock_anterior

        producto.nombre = nombre.strip()
        producto.precio = precio
        producto.costo = costo
        producto.stock = stock
        producto.stock_minimo = stock_minimo
        producto.proveedor = proveedor
        producto.sku = sku
        producto.categoria_id = categoria.id if categoria else None

        db.session.commit()

        if diferencia != 0:
            tipo = "entrada" if diferencia > 0 else "salida"
            movimiento = Movimiento(
                producto_id=producto.id,
                tipo=tipo,
                cantidad=abs(diferencia),
                motivo="Edición manual de producto"
            )
            db.session.add(movimiento)
            db.session.commit()

        return jsonify({
            "mensaje": "Producto actualizado",
            "producto": producto_a_json(producto)
        })

    elif request.method == 'DELETE':
        db.session.delete(producto)
        db.session.commit()

        return jsonify({"mensaje": "Producto eliminado"})


@productos_bp.route('/<int:id>/vender', methods=['PUT'])
@login_requerido
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
            cantidad=cantidad,
            precio_unitario=producto.precio,
            costo_unitario=producto.costo
        )

        nuevo_movimiento = Movimiento(
            producto_id=producto.id,
            tipo="salida",
            cantidad=cantidad,
            motivo="Venta de producto"
        )

        db.session.add(nueva_venta)
        db.session.add(nuevo_movimiento)
        db.session.commit()

        return jsonify({
            "mensaje": "Venta realizada",
            "venta": venta_a_json(nueva_venta),
            "producto": producto_a_json(producto)
        })
    else:
        return jsonify({"mensaje": "Sin stock disponible"}), 400

@productos_bp.route('/<int:id>', methods=['GET'])
@login_requerido
def obtener_producto(id):
    producto = Producto.query.get_or_404(id)

    return jsonify(producto_a_json(producto))

@productos_bp.route('/<int:id>/stock', methods=['PUT'])
@login_requerido
def agregar_stock(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json() or {}
    cantidad = data.get("cantidad")

    if cantidad is None:
        return jsonify({"mensaje": "Debes enviar la cantidad"}), 400

    if not isinstance(cantidad, int) or cantidad <= 0:
        return jsonify({"mensaje": "La cantidad debe ser un número entero mayor a 0"}), 400

    producto.stock += cantidad

    movimiento = Movimiento(
        producto_id=producto.id,
        tipo="entrada",
        cantidad=cantidad,
        motivo="Ingreso manual de stock"
    )

    db.session.add(movimiento)
    db.session.commit()

    return jsonify({
        "mensaje": "Stock actualizado",
        "producto": producto_a_json(producto)
    })

@productos_bp.route('/<int:id>/ajustar-stock', methods=['PUT'])
@login_requerido
def ajustar_stock(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json() or {}

    nuevo_stock = data.get("nuevo_stock")
    motivo = data.get("motivo", "Ajuste manual")

    if nuevo_stock is None:
        return jsonify({"mensaje": "Debes enviar el nuevo stock"}), 400

    if not isinstance(nuevo_stock, int) or nuevo_stock < 0:
        return jsonify({"mensaje": "El nuevo stock debe ser un número entero mayor o igual a 0"}), 400

    stock_anterior = producto.stock
    diferencia = nuevo_stock - stock_anterior

    producto.stock = nuevo_stock

    if diferencia != 0:
        movimiento = Movimiento(
            producto_id=producto.id,
            tipo="ajuste",
            cantidad=abs(diferencia),
            motivo=motivo
        )
        db.session.add(movimiento)

    db.session.commit()

    return jsonify({
        "mensaje": "Stock ajustado correctamente",
        "producto": producto_a_json(producto)
    })

@productos_bp.route('/<int:id>/ventas', methods=['GET'])
@login_requerido
def obtener_ventas_producto(id):
    producto = Producto.query.get_or_404(id)

    resultado = []
    for venta in producto.ventas:
        resultado.append(venta_a_json(venta))

    return jsonify({
        "producto": producto_a_json(producto),
        "ventas": resultado
    })

@productos_bp.route('/<int:id>/movimientos', methods=['GET'])
@login_requerido
def obtener_movimientos_producto(id):
    producto = Producto.query.get_or_404(id)

    resultado = []
    for movimiento in sorted(producto.movimientos, key=lambda m: m.fecha, reverse=True):
        resultado.append({
            "id": movimiento.id,
            "tipo": movimiento.tipo,
            "cantidad": movimiento.cantidad,
            "motivo": movimiento.motivo,
            "fecha": movimiento.fecha
        })

    return jsonify({
        "producto": {
            "id": producto.id,
            "nombre": producto.nombre
        },
        "movimientos": resultado
    })

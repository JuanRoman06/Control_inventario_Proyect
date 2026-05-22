from datetime import datetime

from flask import Blueprint, jsonify, request

from database.db import db
from models.compra import Compra
from models.movimiento import Movimiento
from models.producto import Producto
from utils.auth import login_requerido

compras_bp = Blueprint('compras', __name__)


def _texto_opcional(valor):
    if valor is None or not isinstance(valor, str):
        return None

    valor = valor.strip()
    return valor or None


def _parse_fecha(valor):
    if not valor:
        return datetime.utcnow()

    return datetime.strptime(valor, "%Y-%m-%d")


def compra_a_json(compra):
    total = compra.cantidad * (compra.costo_unitario or 0)

    return {
        "id": compra.id,
        "producto_id": compra.producto_id,
        "cantidad": compra.cantidad,
        "costo_unitario": compra.costo_unitario,
        "total": total,
        "proveedor": compra.proveedor,
        "nota": compra.nota,
        "fecha": compra.fecha,
        "producto": {
            "id": compra.producto.id,
            "nombre": compra.producto.nombre,
            "stock": compra.producto.stock,
            "costo": compra.producto.costo,
            "precio_venta": compra.producto.precio,
            "sku": compra.producto.sku
        }
    }


@compras_bp.route('/', methods=['GET'])
@login_requerido
def listar_compras():
    producto_id = request.args.get('producto_id', type=int)
    limite = request.args.get('limite', default=20, type=int)
    limite = max(1, min(limite, 100))

    query = Compra.query

    if producto_id is not None:
        query = query.filter(Compra.producto_id == producto_id)

    compras = query.order_by(Compra.fecha.desc(), Compra.id.desc()).limit(limite).all()

    return jsonify([compra_a_json(compra) for compra in compras])


@compras_bp.route('/', methods=['POST'])
@login_requerido
def registrar_compra():
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "Debes enviar un JSON válido"}), 400

    producto_id = data.get("producto_id")
    cantidad = data.get("cantidad")
    costo_unitario = data.get("costo_unitario")
    proveedor = _texto_opcional(data.get("proveedor"))
    nota = _texto_opcional(data.get("nota"))
    actualizar_costo = data.get("actualizar_costo", True)

    if not isinstance(producto_id, int):
        return jsonify({"mensaje": "Debes seleccionar un producto válido"}), 400

    if not isinstance(cantidad, int) or cantidad <= 0:
        return jsonify({"mensaje": "La cantidad debe ser un número entero mayor a 0"}), 400

    if not isinstance(costo_unitario, int) or costo_unitario < 0:
        return jsonify({"mensaje": "El costo unitario debe ser un número entero mayor o igual a 0"}), 400

    try:
        fecha = _parse_fecha(data.get("fecha"))
    except ValueError:
        return jsonify({"mensaje": "La fecha debe tener formato YYYY-MM-DD"}), 400

    producto = Producto.query.get(producto_id)
    if not producto:
        return jsonify({"mensaje": "El producto seleccionado no existe"}), 404

    proveedor_final = proveedor or producto.proveedor

    compra = Compra(
        producto_id=producto.id,
        cantidad=cantidad,
        costo_unitario=costo_unitario,
        proveedor=proveedor_final,
        nota=nota,
        fecha=fecha
    )

    producto.stock += cantidad
    if actualizar_costo:
        producto.costo = costo_unitario
    if proveedor:
        producto.proveedor = proveedor

    movimiento = Movimiento(
        producto_id=producto.id,
        tipo="entrada",
        cantidad=cantidad,
        motivo=f"Compra a {proveedor_final}" if proveedor_final else "Compra registrada"
    )

    db.session.add(compra)
    db.session.add(movimiento)
    db.session.commit()

    return jsonify({
        "mensaje": "Compra registrada y stock actualizado",
        "compra": compra_a_json(compra)
    }), 201

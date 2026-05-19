from flask import Blueprint, jsonify, request
from models.venta import Venta
from utils.auth import login_requerido

ventas_bp = Blueprint('ventas', __name__)


def venta_a_json(venta):
    precio_unitario = venta.precio_unitario or 0
    costo_unitario = venta.costo_unitario or 0
    total = precio_unitario * venta.cantidad
    utilidad = (precio_unitario - costo_unitario) * venta.cantidad

    return {
        "id": venta.id,
        "cantidad": venta.cantidad,
        "fecha": venta.fecha,
        "precio_unitario": precio_unitario,
        "costo_unitario": costo_unitario,
        "total": total,
        "utilidad": utilidad,
        "producto": {
            "id": venta.producto.id,
            "nombre": venta.producto.nombre,
            "precio": venta.producto.precio,
            "precio_venta": venta.producto.precio,
            "costo": venta.producto.costo
        }
    }


@ventas_bp.route('/', methods=['GET'])
@login_requerido
def listar_ventas():
    producto_id = request.args.get('producto_id', type=int)

    query = Venta.query

    if producto_id is not None:
        query = query.filter(Venta.producto_id == producto_id)

    ventas = query.all()

    return jsonify([venta_a_json(v) for v in ventas])


@ventas_bp.route('/<int:id>', methods=['GET'])
@login_requerido
def obtener_venta(id):
    venta = Venta.query.get_or_404(id)

    return jsonify(venta_a_json(venta))

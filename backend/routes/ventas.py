from flask import Blueprint, jsonify
from models.venta import Venta

ventas_bp = Blueprint('ventas', __name__)


@ventas_bp.route('/', methods=['GET'])
def listar_ventas():
    producto_id = request.args.get('producto_id', type=int)

    query = Venta.query

    if producto_id is not None:
        query = query.filter(Venta.producto_id == producto_id)

    ventas = query.all()

    resultado = []
    for v in ventas:
        resultado.append({
            "id": v.id,
            "cantidad": v.cantidad,
            "fecha": v.fecha,
            "producto": {
                "id": v.producto.id,
                "nombre": v.producto.nombre,
                "precio": v.producto.precio
            }
        })

    return jsonify(resultado)


@ventas_bp.route('/<int:id>', methods=['GET'])
def obtener_venta(id):
    venta = Venta.query.get_or_404(id)

    return jsonify({
        "id": venta.id,
        "cantidad": venta.cantidad,
        "fecha": venta.fecha,
        "producto": {
            "id": venta.producto.id,
            "nombre": venta.producto.nombre,
            "precio": venta.producto.precio
        }
    })
from flask import Blueprint, jsonify, request
from models.movimiento import Movimiento


movimientos_bp = Blueprint('movimientos', __name__)


@movimientos_bp.route('/', methods=['GET'])
def listar_movimientos():
    producto_id = request.args.get('producto_id', type=int)
    tipo = request.args.get('tipo')

    query = Movimiento.query

    if producto_id is not None:
        query = query.filter(Movimiento.producto_id == producto_id)

    if tipo:
        query = query.filter(Movimiento.tipo == tipo)

    movimientos = query.order_by(Movimiento.fecha.desc()).all()

    resultado = []
    for m in movimientos:
        resultado.append({
            "id": m.id,
            "tipo": m.tipo,
            "cantidad": m.cantidad,
            "motivo": m.motivo,
            "fecha": m.fecha,
            "producto": {
                "id": m.producto.id,
                "nombre": m.producto.nombre,
                "precio": m.producto.precio
            }
        })

    return jsonify(resultado)
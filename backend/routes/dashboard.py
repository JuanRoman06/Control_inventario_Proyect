from flask import Blueprint, jsonify
from sqlalchemy import func
from models.producto import Producto
from models.venta import Venta
from models.movimiento import Movimiento
from database.db import db


dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/resumen', methods=['GET'])
def resumen_dashboard():
    productos = Producto.query.all()
    ventas = Venta.query.all()

    total_productos = len(productos)
    total_stock = sum(p.stock for p in productos)
    stock_bajo = len([p for p in productos if p.stock <= 5])
    valor_inventario = sum(p.precio * p.stock for p in productos)
    total_ventas = len(ventas)
    unidades_vendidas = sum(v.cantidad for v in ventas)

    return jsonify({
        "total_productos": total_productos,
        "total_stock": total_stock,
        "stock_bajo": stock_bajo,
        "valor_inventario": valor_inventario,
        "total_ventas": total_ventas,
        "unidades_vendidas": unidades_vendidas
    })


@dashboard_bp.route('/mas-vendidos', methods=['GET'])
def productos_mas_vendidos():
    resultados = (
        db.session.query(
            Producto.id,
            Producto.nombre,
            Producto.precio,
            func.coalesce(func.sum(Venta.cantidad), 0).label('total_vendido')
        )
        .outerjoin(Venta, Producto.id == Venta.producto_id)
        .group_by(Producto.id, Producto.nombre, Producto.precio)
        .order_by(func.coalesce(func.sum(Venta.cantidad), 0).desc())
        .all()
    )

    data = []
    for r in resultados:
        data.append({
            "id": r.id,
            "nombre": r.nombre,
            "precio": r.precio,
            "total_vendido": r.total_vendido
        })

    return jsonify(data[:10])


@dashboard_bp.route('/movimientos-recientes', methods=['GET'])
def movimientos_recientes():
    movimientos = Movimiento.query.order_by(Movimiento.fecha.desc()).limit(10).all()

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
                "nombre": m.producto.nombre
            }
        })

    return jsonify(resultado)
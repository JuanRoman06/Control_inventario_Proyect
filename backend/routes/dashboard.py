from flask import Blueprint, jsonify
from sqlalchemy import func
from models.producto import Producto
from models.venta import Venta
from models.movimiento import Movimiento
from database.db import db
from utils.auth import login_requerido

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/resumen', methods=['GET'])
@login_requerido
def resumen_dashboard():
    productos = Producto.query.all()
    ventas = Venta.query.all()

    total_productos = len(productos)
    total_stock = sum(p.stock for p in productos)
    stock_bajo = len([p for p in productos if p.stock <= p.stock_minimo])
    valor_inventario = sum(p.precio * p.stock for p in productos)
    costo_inventario = sum(p.costo * p.stock for p in productos)
    utilidad_potencial = valor_inventario - costo_inventario
    total_ventas = len(ventas)
    unidades_vendidas = sum(v.cantidad for v in ventas)
    ingresos_ventas = sum((v.precio_unitario or 0) * v.cantidad for v in ventas)
    costo_ventas = sum((v.costo_unitario or 0) * v.cantidad for v in ventas)
    utilidad_ventas = ingresos_ventas - costo_ventas

    return jsonify({
        "total_productos": total_productos,
        "total_stock": total_stock,
        "stock_bajo": stock_bajo,
        "valor_inventario": valor_inventario,
        "costo_inventario": costo_inventario,
        "utilidad_potencial": utilidad_potencial,
        "total_ventas": total_ventas,
        "unidades_vendidas": unidades_vendidas,
        "ingresos_ventas": ingresos_ventas,
        "costo_ventas": costo_ventas,
        "utilidad_ventas": utilidad_ventas
    })


@dashboard_bp.route('/mas-vendidos', methods=['GET'])
@login_requerido
def productos_mas_vendidos():
    resultados = (
        db.session.query(
            Producto.id,
            Producto.nombre,
            Producto.precio,
            Producto.costo,
            func.coalesce(func.sum(Venta.cantidad), 0).label('total_vendido'),
            func.coalesce(func.sum(Venta.precio_unitario * Venta.cantidad), 0).label('ingresos'),
            func.coalesce(func.sum((Venta.precio_unitario - Venta.costo_unitario) * Venta.cantidad), 0).label('utilidad')
        )
        .outerjoin(Venta, Producto.id == Venta.producto_id)
        .group_by(Producto.id, Producto.nombre, Producto.precio, Producto.costo)
        .order_by(func.coalesce(func.sum(Venta.cantidad), 0).desc())
        .all()
    )

    data = []
    for r in resultados:
        data.append({
            "id": r.id,
            "nombre": r.nombre,
            "precio": r.precio,
            "precio_venta": r.precio,
            "costo": r.costo,
            "total_vendido": r.total_vendido,
            "ingresos": r.ingresos,
            "utilidad": r.utilidad
        })

    return jsonify(data[:10])


@dashboard_bp.route('/movimientos-recientes', methods=['GET'])
@login_requerido
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

from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from models.producto import Producto
from models.venta import Venta
from models.movimiento import Movimiento
from database.db import db
from utils.auth import login_requerido

dashboard_bp = Blueprint('dashboard', __name__)


def _parse_fecha(valor):
    if not valor:
        return None

    return datetime.strptime(valor, "%Y-%m-%d")


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


@dashboard_bp.route('/reporte-ventas', methods=['GET'])
@login_requerido
def reporte_ventas():
    try:
        desde = _parse_fecha(request.args.get('desde'))
        hasta = _parse_fecha(request.args.get('hasta'))
    except ValueError:
        return jsonify({"mensaje": "Las fechas deben tener formato YYYY-MM-DD"}), 400

    if desde is None and hasta is None:
        hasta = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        desde = hasta - timedelta(days=6)
    elif desde is None:
        desde = hasta - timedelta(days=6)
    elif hasta is None:
        hasta = desde + timedelta(days=6)

    if desde > hasta:
        return jsonify({"mensaje": "La fecha inicial no puede ser mayor que la fecha final"}), 400

    if (hasta - desde).days > 370:
        return jsonify({"mensaje": "El reporte permite consultar máximo 370 días"}), 400

    hasta_exclusivo = hasta + timedelta(days=1)
    ventas = (
        Venta.query
        .join(Producto)
        .filter(Venta.fecha >= desde)
        .filter(Venta.fecha < hasta_exclusivo)
        .order_by(Venta.fecha.asc())
        .all()
    )

    resumen = {
        "total_ventas": len(ventas),
        "unidades": 0,
        "ingresos": 0,
        "costo": 0,
        "utilidad": 0,
        "ticket_promedio": 0
    }
    por_dia = defaultdict(lambda: {
        "ventas": 0,
        "unidades": 0,
        "ingresos": 0,
        "utilidad": 0
    })
    por_producto = {}

    for venta in ventas:
        precio_unitario = venta.precio_unitario or venta.producto.precio or 0
        costo_unitario = venta.costo_unitario or venta.producto.costo or 0
        ingresos = precio_unitario * venta.cantidad
        costo = costo_unitario * venta.cantidad
        utilidad = ingresos - costo
        fecha_key = venta.fecha.date().isoformat()

        resumen["unidades"] += venta.cantidad
        resumen["ingresos"] += ingresos
        resumen["costo"] += costo
        resumen["utilidad"] += utilidad

        por_dia[fecha_key]["ventas"] += 1
        por_dia[fecha_key]["unidades"] += venta.cantidad
        por_dia[fecha_key]["ingresos"] += ingresos
        por_dia[fecha_key]["utilidad"] += utilidad

        producto_key = venta.producto_id
        if producto_key not in por_producto:
            por_producto[producto_key] = {
                "id": venta.producto.id,
                "nombre": venta.producto.nombre,
                "cantidad": 0,
                "ventas": 0,
                "ingresos": 0,
                "utilidad": 0
            }

        por_producto[producto_key]["cantidad"] += venta.cantidad
        por_producto[producto_key]["ventas"] += 1
        por_producto[producto_key]["ingresos"] += ingresos
        por_producto[producto_key]["utilidad"] += utilidad

    if resumen["total_ventas"]:
        resumen["ticket_promedio"] = round(resumen["ingresos"] / resumen["total_ventas"])

    dias = []
    dia_actual = desde
    while dia_actual <= hasta:
        fecha_key = dia_actual.date().isoformat()
        dias.append({
            "fecha": fecha_key,
            **por_dia[fecha_key]
        })
        dia_actual += timedelta(days=1)

    productos = sorted(
        por_producto.values(),
        key=lambda producto: (producto["ingresos"], producto["cantidad"]),
        reverse=True
    )

    return jsonify({
        "desde": desde.date().isoformat(),
        "hasta": hasta.date().isoformat(),
        "resumen": resumen,
        "por_dia": dias,
        "productos": productos[:10]
    })


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

import csv
from io import StringIO

from flask import Blueprint, Response

from models.compra import Compra
from models.producto import Producto
from models.venta import Venta
from utils.auth import login_requerido

exportaciones_bp = Blueprint('exportaciones', __name__)


def _csv_response(nombre_archivo, encabezados, filas):
    salida = StringIO()
    salida.write('\ufeff')
    writer = csv.writer(salida, delimiter=';')
    writer.writerow(encabezados)
    writer.writerows(filas)

    return Response(
        salida.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={
            "Content-Disposition": f"attachment; filename={nombre_archivo}"
        }
    )


@exportaciones_bp.route('/inventario.csv', methods=['GET'])
@login_requerido
def exportar_inventario():
    productos = Producto.query.order_by(Producto.nombre.asc()).all()
    filas = []

    for producto in productos:
        precio = producto.precio or 0
        costo = producto.costo or 0
        stock = producto.stock or 0
        filas.append([
            producto.id,
            producto.sku or "",
            producto.nombre,
            producto.categoria.nombre if producto.categoria else "",
            stock,
            producto.stock_minimo or 0,
            precio,
            costo,
            precio * stock,
            costo * stock,
            (precio - costo) * stock,
            producto.proveedor or ""
        ])

    return _csv_response(
        'inventario_dulceria.csv',
        [
            'ID',
            'SKU',
            'Producto',
            'Categoria',
            'Stock',
            'Stock minimo',
            'Precio venta',
            'Costo unitario',
            'Valor inventario venta',
            'Costo inventario',
            'Utilidad potencial',
            'Proveedor'
        ],
        filas
    )


@exportaciones_bp.route('/ventas.csv', methods=['GET'])
@login_requerido
def exportar_ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc(), Venta.id.desc()).all()
    filas = []

    for venta in ventas:
        precio = venta.precio_unitario or 0
        costo = venta.costo_unitario or 0
        total = precio * venta.cantidad
        utilidad = (precio - costo) * venta.cantidad
        filas.append([
            venta.id,
            venta.fecha.isoformat(sep=' ', timespec='seconds') if venta.fecha else "",
            venta.producto.nombre,
            venta.cantidad,
            precio,
            costo,
            total,
            utilidad
        ])

    return _csv_response(
        'ventas_dulceria.csv',
        [
            'ID',
            'Fecha',
            'Producto',
            'Cantidad',
            'Precio unitario',
            'Costo unitario',
            'Total venta',
            'Utilidad'
        ],
        filas
    )


@exportaciones_bp.route('/compras.csv', methods=['GET'])
@login_requerido
def exportar_compras():
    compras = Compra.query.order_by(Compra.fecha.desc(), Compra.id.desc()).all()
    filas = []

    for compra in compras:
        costo = compra.costo_unitario or 0
        filas.append([
            compra.id,
            compra.fecha.isoformat(sep=' ', timespec='seconds') if compra.fecha else "",
            compra.producto.nombre,
            compra.cantidad,
            costo,
            costo * compra.cantidad,
            compra.proveedor or "",
            compra.nota or ""
        ])

    return _csv_response(
        'compras_dulceria.csv',
        [
            'ID',
            'Fecha',
            'Producto',
            'Cantidad',
            'Costo unitario',
            'Total compra',
            'Proveedor',
            'Nota'
        ],
        filas
    )

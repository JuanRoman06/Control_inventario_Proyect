from flask import Blueprint, jsonify, request
from models.categoria import Categoria
from database.db import db
from utils.auth import login_requerido

categorias_bp = Blueprint('categorias', __name__)


@categorias_bp.route('/', methods=['GET'])
@login_requerido
def listar_categorias():
    categorias = Categoria.query.order_by(Categoria.nombre.asc()).all()

    resultado = []
    for c in categorias:
        resultado.append({
            "id": c.id,
            "nombre": c.nombre
        })

    return jsonify(resultado)


@categorias_bp.route('/', methods=['POST'])
@login_requerido
def crear_categoria():
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "Debes enviar un JSON válido"}), 400

    nombre = data.get("nombre")

    if not nombre or not isinstance(nombre, str) or not nombre.strip():
        return jsonify({"mensaje": "El nombre de la categoría es obligatorio"}), 400

    nombre = nombre.strip()

    existe = Categoria.query.filter(Categoria.nombre.ilike(nombre)).first()
    if existe:
        return jsonify({"mensaje": "La categoría ya existe"}), 400

    nueva_categoria = Categoria(nombre=nombre)
    db.session.add(nueva_categoria)
    db.session.commit()

    return jsonify({
        "mensaje": "Categoría creada",
        "categoria": {
            "id": nueva_categoria.id,
            "nombre": nueva_categoria.nombre
        }
    }), 201


@categorias_bp.route('/<int:id>', methods=['PUT'])
@login_requerido
def editar_categoria(id):
    categoria = Categoria.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "Debes enviar un JSON válido"}), 400

    nombre = data.get("nombre")

    if not nombre or not isinstance(nombre, str) or not nombre.strip():
        return jsonify({"mensaje": "El nombre de la categoría es obligatorio"}), 400

    nombre = nombre.strip()

    existe = Categoria.query.filter(Categoria.nombre.ilike(nombre), Categoria.id != id).first()
    if existe:
        return jsonify({"mensaje": "Ya existe otra categoría con ese nombre"}), 400

    categoria.nombre = nombre
    db.session.commit()

    return jsonify({
        "mensaje": "Categoría actualizada",
        "categoria": {
            "id": categoria.id,
            "nombre": categoria.nombre
        }
    })


@categorias_bp.route('/<int:id>', methods=['DELETE'])
@login_requerido
def eliminar_categoria(id):
    categoria = Categoria.query.get_or_404(id)

    if categoria.productos:
        return jsonify({"mensaje": "No puedes eliminar una categoría que tiene productos asociados"}), 400

    db.session.delete(categoria)
    db.session.commit()

    return jsonify({"mensaje": "Categoría eliminada"})
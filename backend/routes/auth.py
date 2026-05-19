from flask import Blueprint, jsonify, request, session
from models.usuario import Usuario
from database.db import db


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "Debes enviar un JSON válido"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not username.strip():
        return jsonify({"mensaje": "El usuario es obligatorio"}), 400

    if not password or len(password) < 4:
        return jsonify({"mensaje": "La contraseña debe tener al menos 4 caracteres"}), 400

    usuarios_existentes = Usuario.query.count()
    if usuarios_existentes and not session.get("usuario_id"):
        return jsonify({
            "mensaje": "El registro inicial ya fue creado. Inicia sesión para crear más usuarios."
        }), 403

    existe = Usuario.query.filter_by(username=username.strip()).first()
    if existe:
        return jsonify({"mensaje": "Ese usuario ya existe"}), 400

    nuevo_usuario = Usuario(username=username.strip())
    nuevo_usuario.set_password(password)

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        "mensaje": "Usuario creado correctamente",
        "usuario": {
            "id": nuevo_usuario.id,
            "username": nuevo_usuario.username
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "Debes enviar un JSON válido"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"mensaje": "Usuario y contraseña son obligatorios"}), 400

    usuario = Usuario.query.filter_by(username=username.strip()).first()

    if not usuario or not usuario.check_password(password):
        return jsonify({"mensaje": "Credenciales inválidas"}), 401

    session["usuario_id"] = usuario.id
    session["username"] = usuario.username

    return jsonify({
        "mensaje": "Login exitoso",
        "usuario": {
            "id": usuario.id,
            "username": usuario.username
        }
    })


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"mensaje": "Sesión cerrada correctamente"})


@auth_bp.route('/me', methods=['GET'])
def me():
    if not session.get("usuario_id"):
        return jsonify({"autenticado": False}), 200

    return jsonify({
        "autenticado": True,
        "usuario": {
            "id": session.get("usuario_id"),
            "username": session.get("username")
        }
    })

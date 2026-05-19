from functools import wraps
from flask import session, jsonify


def login_requerido(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            return jsonify({"mensaje": "No autorizado"}), 401
        return func(*args, **kwargs)
    return wrapper
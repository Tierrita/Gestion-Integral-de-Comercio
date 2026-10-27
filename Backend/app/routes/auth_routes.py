"""
Rutas de autenticación.

Define los endpoints relacionados con el acceso
de los usuarios al sistema.
"""

from flask import Blueprint

from app.controllers.auth_controller import (
    login,
    obtener_perfil_actual,
)

from core.auth import login_requerido

auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


@auth_bp.route("/login", methods=["POST"])
def login_route():
    """
    POST /auth/login
    """
    return login()

@auth_bp.route("/me", methods=["GET"])
@login_requerido
def me_route():
    """
    GET /auth/me
    """
    return obtener_perfil_actual()
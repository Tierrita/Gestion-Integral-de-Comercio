"""
Controlador de productos.

Este módulo recibe las solicitudes HTTP relacionadas
con productos y delega la lógica de negocio al Service.

El comercio nunca se recibe desde el frontend.
Se obtiene del usuario autenticado mediante g.id_comercio.

Route → Controller → Service → Model → Supabase
"""

from flask import jsonify, request, g
from postgrest.exceptions import APIError

from core.auth import usuario_tiene_permiso

from app.services.producto_service import (
    listar_productos,
    buscar_producto_por_id,
    crear_producto,
    modificar_producto,
)


def _ocultar_costos_si_corresponde(producto):
    """
    Elimina el precio de costo cuando el usuario
    no posee el permiso productos.ver_costos.

    El propietario posee acceso automático a todos
    los permisos mediante usuario_tiene_permiso().
    """

    if usuario_tiene_permiso("productos.ver_costos"):
        return producto

    producto_seguro = producto.copy()
    producto_seguro.pop("precio_costo", None)

    return producto_seguro


def obtener_productos_controller():
    """
    Obtiene los productos pertenecientes
    al comercio autenticado.

    El precio de costo solamente se muestra
    a usuarios autorizados.
    """

    try:
        productos = listar_productos(
            g.id_comercio
        )

        productos_seguros = [
            _ocultar_costos_si_corresponde(producto)
            for producto in productos
        ]

        return jsonify(productos_seguros), 200

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


def obtener_producto_controller(id_producto):
    """
    Obtiene un producto específico verificando
    que pertenezca al comercio autenticado.

    El precio de costo solamente se muestra
    a usuarios autorizados.
    """

    try:
        producto = buscar_producto_por_id(
            id_producto,
            g.id_comercio
        )

        producto_seguro = _ocultar_costos_si_corresponde(
            producto
        )

        return jsonify(producto_seguro), 200

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 404

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


def crear_producto_controller():
    """
    Crea un producto dentro del comercio autenticado.

    El id_comercio nunca se obtiene del body.
    Siempre se utiliza el comercio del usuario autenticado.
    """

    try:
        datos = request.get_json() or {}

        if not datos:
            return jsonify({
                "error": "No se enviaron datos del producto"
            }), 400

        producto = crear_producto(
            datos,
            g.id_comercio
        )

        producto_seguro = _ocultar_costos_si_corresponde(
            producto
        )

        return jsonify({
            "message": "Producto creado correctamente",
            "producto": producto_seguro
        }), 201

    except ValueError as error:
        return jsonify({
            "error": str(error)
        }), 400

    except APIError as error:

        if error.code == "23503":
            return jsonify({
                "error": "La categoría o el proveedor indicado no existe"
            }), 400

        # Temporal durante desarrollo.
        return jsonify({
            "error": "Error al crear el producto",
            "codigo": error.code,
            "detalle": str(error)
        }), 500

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


def modificar_producto_controller(id_producto):
    """
    Modifica los datos comerciales de un producto
    perteneciente al comercio autenticado.

    El Service controla qué campos pueden modificarse.

    Para modificar precio_costo, además del permiso
    productos.modificar, el usuario debe poseer
    productos.ver_costos.
    """

    try:
        datos = request.get_json() or {}

        if not datos:
            return jsonify({
                "error": "No se enviaron datos para modificar"
            }), 400

        puede_modificar_costo = usuario_tiene_permiso(
            "productos.ver_costos"
        )

        producto = modificar_producto(
            id_producto=id_producto,
            datos=datos,
            id_comercio=g.id_comercio,
            puede_modificar_costo=puede_modificar_costo
        )

        producto_seguro = _ocultar_costos_si_corresponde(
            producto
        )

        return jsonify({
            "message": "Producto modificado correctamente",
            "producto": producto_seguro
        }), 200

    except PermissionError as error:
        return jsonify({
            "error": str(error)
        }), 403

    except ValueError as error:
        mensaje = str(error)

        if mensaje == "Producto no encontrado":
            return jsonify({
                "error": mensaje
            }), 404

        return jsonify({
            "error": mensaje
        }), 400

    except APIError as error:

        if error.code == "23503":
            return jsonify({
                "error": "La categoría o el proveedor indicado no existe"
            }), 400

        return jsonify({
            "error": "Error al modificar el producto",
            "codigo": error.code,
            "detalle": str(error)
        }), 500

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500
"""
Este paquete representa la capa principal de la aplicación Flask.

Su responsabilidad es agrupar la lógica del backend y organizar
los distintos módulos que conforman la arquitectura del proyecto.

Aquí se conectarán, de forma ordenada, las rutas, los controladores,
los modelos y los servicios del E-Commerce Kiosco.

Es el punto de entrada de la estructura del backend y sirve para
mantener una separación clara entre la API, la lógica de negocio y
los datos.
"""

from flask import Flask
from config import init_app as init_config


def create_app():
    """
    Crea y configura la aplicación Flask.

    Carga la configuración del proyecto, inicializa el cliente
    de Supabase y registra los Blueprints de la aplicación.
    """

    # Crear instancia de Flask
    app = Flask(__name__)

    # Cargar configuración y variables de entorno
    init_config(app)

    # Inicializar cliente de Supabase
    from core.supabase_client import init_supabase

    supabase_url = app.config.get("SUPABASE_URL")
    supabase_key = app.config.get("SUPABASE_KEY")

    # Inicializar Supabase solamente si existen las credenciales
    if supabase_url and supabase_key:
        init_supabase(app)






    # Importar Blueprints
    from .routes import main_bp
    from .routes.producto_routes import producto_bp
    from .routes.stock_routes import stock_bp
    from .routes.compra_routes import compra_bp
    from .routes.venta_routes import venta_bp
    from .routes.categoria_routes import categoria_bp
    from .routes.proveedor_routes import proveedor_bp
    from .routes.cuenta_routes import cuenta_bp
    from .routes.cobro_routes import cobro_bp
    from .routes.pago_proveedor_routes import pago_proveedor_bp
    from .routes.cliente_routes import cliente_bp





    # Registrar Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(producto_bp)
    app.register_blueprint(stock_bp)
    app.register_blueprint(compra_bp)
    app.register_blueprint(venta_bp)
    app.register_blueprint(categoria_bp)
    app.register_blueprint(proveedor_bp)
    app.register_blueprint(cuenta_bp)
    app.register_blueprint(cobro_bp)
    app.register_blueprint(pago_proveedor_bp)
    app.register_blueprint(cliente_bp)



    # Devolver aplicación configurada
    return app
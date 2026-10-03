#EN ESTE MODULO, CREAMOS LA APP, Y PRENDEMOS EN EL SERVIDOR 5001

from app import create_app


if __name__ == "__main__":
    # Obtener la aplicación desde la Application Factory
    app = create_app()
    # Ejecutar el servidor de desarrollo en el puerto esperado
    app.run(host="0.0.0.0", port=5001, debug=True)

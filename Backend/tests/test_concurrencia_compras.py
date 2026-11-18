
import os
import threading
from getpass import getpass

import psycopg

HOST = "aws-0-us-west-2.pooler.supabase.com"
PORT = 5432
DATABASE = "postgres"
USER = "postgres.qyshurxdkyucbydsttbw"

ID_COMERCIO = 1
ID_USUARIO = 1
ID_PROVEEDOR = 1
ID_PRODUCTO = 6

password = getpass("Contraseña de Supabase: ")

resultados = {}
inicio = threading.Barrier(2)


def conectar():
    return psycopg.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=password,
        sslmode="require",
        connect_timeout=10,
        autocommit=False,
    )


def probar_compra(nombre, cantidad):
    try:
        with conectar() as conexion:
            with conexion.cursor() as cursor:
                # Evita que la prueba quede esperando indefinidamente.
                cursor.execute("SET LOCAL lock_timeout = '15s'")

                inicio.wait(timeout=20)

                cursor.execute(
                    """
                    SELECT public.registrar_compra_transaccional(
                        %s, %s, %s, %s::jsonb, %s
                    )
                    """,
                    (
                        ID_COMERCIO,
                        ID_USUARIO,
                        ID_PROVEEDOR,
                        psycopg.types.json.Jsonb([
                            {
                                "id_producto": ID_PRODUCTO,
                                "cantidad": cantidad,
                                "precio_unitario": 1000,
                            }
                        ]),
                        f"PRUEBA CONCURRENCIA {nombre}",
                    ),
                )

                resultado = cursor.fetchone()[0]

                resultados[nombre] = {
                    "numero_compra": resultado["compra"]["numero_compra"],
                    "stock_resultante": resultado[
                        "productos_actualizados"
                    ][0]["stock_actual"],
                }

                # No confirmar cambios en la base de datos.
                conexion.rollback()

    except Exception as error:
        resultados[nombre] = {"error": str(error)}


hilos = [
    threading.Thread(target=probar_compra, args=("A", 2)),
    threading.Thread(target=probar_compra, args=("B", 3)),
]

for hilo in hilos:
    hilo.start()

for hilo in hilos:
    hilo.join()

print("\nRESULTADOS DE CONCURRENCIA")

for nombre, resultado in sorted(resultados.items()):
    print(f"Compra {nombre}: {resultado}")

print("\nAmbas transacciones finalizaron.")

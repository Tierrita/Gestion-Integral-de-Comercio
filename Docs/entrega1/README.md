# Entrega 1 – Configuración inicial del backend

**Fecha:** 31 de agosto de 2026  
**Proyecto:** E-Commerce Kiosco

## Objetivo

Preparar la base del backend y comprobar que una aplicación Flask pudiera ejecutarse y responder a una petición. Esta entrega se centró en la configuración inicial, antes de incorporar las funcionalidades del comercio.

## Qué se hizo

Se verificó la instalación de **Python 3.9.6** y se creó un entorno virtual para aislar las dependencias del proyecto. Dentro de ese entorno se instaló **Flask 3.1.3** y se generó `requirements.txt`, que permite volver a instalar las dependencias necesarias.

También se creó `app.py` como punto de entrada de la aplicación y se organizó el backend en carpetas para rutas, controladores, servicios y modelos. Se prepararon además carpetas para configuración, componentes compartidos, utilidades y pruebas. Esta estructura permite incorporar funcionalidades de forma ordenada en las siguientes entregas.

Como primera comprobación, se definió la ruta `GET /`, que devuelve una respuesta simple para confirmar que el servidor está funcionando.

## Prueba realizada

Se inició el backend en el entorno local y se consultó la ruta `GET /`. La aplicación respondió correctamente, confirmando que Flask estaba instalado y que el servidor podía recibir peticiones.

## Resultado

Quedó lista la base técnica del backend del E-Commerce Kiosco: entorno virtual, dependencias registradas, estructura inicial y aplicación Flask en funcionamiento. El siguiente paso es organizar la aplicación en módulos y conectar las rutas con esa estructura.
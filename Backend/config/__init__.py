"""Configuración general del proyecto.

Este módulo centraliza la configuración del proyecto y expone las
variables de entorno que necesitaremos más adelante para conectar
servicios externos (por ejemplo Supabase). En este Paso 2 sólo
preparamos la lectura de las variables de entorno de forma segura,
sin inicializar clientes externos.

Uso:
- Importar `from config import SUPABASE_URL, SUPABASE_KEY` en módulos
	que lo requieran (sin imprimirlos).
- O llamar a `config.init_app(app)` desde la fábrica de Flask para
	cargar estas variables en `app.config`.
"""

from pathlib import Path
import os

# Cargar .env local (si existe) y exponer variables de entorno.
from dotenv import load_dotenv

# Determinar la ruta base del proyecto (carpeta `Backend`)
BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = BASE_DIR / ".env"

# Cargar variables desde .env si el archivo existe. No lanza errores
# si el archivo no está presente; las variables seguirán siendo None.
load_dotenv(DOTENV_PATH)

# Variables preparadas para usar por la aplicación
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def init_app(app):
		"""Inyecta la configuración relevante dentro de `app.config`.

		No inicializa clientes externos aquí; sólo copia las variables
		de entorno a la configuración de Flask para que otros módulos
		puedan acceder a ellas desde `current_app.config` si fuese
		necesario.
		"""
		app.config.setdefault("SUPABASE_URL", SUPABASE_URL)
		app.config.setdefault("SUPABASE_KEY", SUPABASE_KEY)


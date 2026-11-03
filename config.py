import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

# Configuracion general
SECRET_KEY = os.getenv(
    'SECRET_KEY',
    'solo-desarrollo-cambiar-antes-de-publicar'
)

# Conexion con MySQL
SQLALCHEMY_DATABASE_URI = (
    'mysql+pymysql://'
    + quote_plus(os.getenv('DB_USER', 'root')) + ':'
    + quote_plus(os.getenv('DB_PASSWORD', '')) + '@'
    + os.getenv('DB_HOST', '127.0.0.1') + ':'
    + os.getenv('DB_PORT', '3306') + '/'
    + os.getenv('DB_NAME', 'jh7_db')
    + '?charset=utf8mb4'
)

SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configuracion de Flask-AppBuilder
WTF_CSRF_ENABLED = True
APP_NAME = 'JH7 Telecom'
APP_ICON = '/static/img/logo_jh7.jpg'
AUTH_ROLE_PUBLIC = 'Public'
BABEL_DEFAULT_LOCALE = 'es'

# Configuracion del asistente de inteligencia artificial
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
GROQ_MODEL = os.getenv('GROQ_MODEL', 'openai/gpt-oss-20b')
GROQ_BASE_URL = os.getenv(
    'GROQ_BASE_URL',
    'https://api.groq.com/openai/v1'
)
import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-tu-clave-secreta')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend_config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend_config.wsgi.application'

def mysql_url_config():
    mysql_url = os.getenv('MYSQL_PUBLIC_URL') or os.getenv('MYSQL_URL')
    if not mysql_url:
        return {}

    parsed = urlparse(mysql_url)
    return {
        'NAME': parsed.path.lstrip('/') or os.getenv('MYSQLDATABASE', 'planificador_eventos'),
        'USER': parsed.username or os.getenv('MYSQLUSER', 'root'),
        'PASSWORD': parsed.password or os.getenv('MYSQLPASSWORD', ''),
        'HOST': parsed.hostname or os.getenv('MYSQLHOST', 'localhost'),
        'PORT': str(parsed.port or os.getenv('MYSQLPORT', '3306')),
    }


mysql_from_url = mysql_url_config()

# MySQL: acepta variables locales, Railway y URLs de conexion.
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.mysql',
        'NAME':     os.getenv('MYSQL_DATABASE') or mysql_from_url.get('NAME') or os.getenv('MYSQLDATABASE', 'planificador_eventos'),
        'USER':     os.getenv('MYSQL_USER')     or mysql_from_url.get('USER') or os.getenv('MYSQLUSER', 'root'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD') or mysql_from_url.get('PASSWORD') or os.getenv('MYSQLPASSWORD', ''),
        'HOST':     os.getenv('MYSQL_HOST')     or mysql_from_url.get('HOST') or os.getenv('MYSQLHOST', 'localhost'),
        'PORT':     os.getenv('MYSQL_PORT')     or mysql_from_url.get('PORT') or os.getenv('MYSQLPORT', '3306'),
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-co'
TIME_ZONE     = 'America/Bogota'
USE_I18N      = True
USE_TZ        = True
STATIC_URL    = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}

SPARQL_ENDPOINT = os.getenv('SPARQL_ENDPOINT', '')
SPARQL_USER     = os.getenv('SPARQL_USER', 'admin')
SPARQL_PASSWORD = os.getenv('SPARQL_PASSWORD', '')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}


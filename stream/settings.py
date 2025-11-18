"""
Fichier de configuration pour le projet StreamApp.
Ce fichier est organisé en sections logiques pour une meilleure clarté.
"""

import os
from pathlib import Path

# --- Chemins et Variables d'Environnement ---
from dotenv import load_dotenv

# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# --- Configuration de Base Django ---
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-default-key-for-dev")

# SECURITY WARNING: don't run with debug turned on in production!
# Rend DEBUG dynamique pour plus de flexibilité et de sécurité
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Autorise les connexions en développement, restreint en production
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(',')

# Redirige l'utilisateur après la connexion/déconnexion
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Origines de confiance pour les requêtes CSRF (utile avec ngrok)
CSRF_TRUSTED_ORIGINS = [
    "https://vicarious-cucullately-davian.ngrok-free.dev",
]


# --- Définition des Applications ---
INSTALLED_APPS = [

    # Applications tierces
    'unfold',          # Thème pour l'admin
    # Applications par défaut
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    "widget_tweaks",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    'corsheaders',     # Pour gérer les CORS
    'storages',        # Pour l'intégration avec R2/S3

    # Application locale
    'core',
]
 

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Doit être en premier pour gérer les CORS
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',  # Déplacé ici
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
] 


ROOT_URLCONF = 'stream.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Dossier global pour les templates
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

WSGI_APPLICATION = 'stream.wsgi.application'


# --- Base de Données ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --- Internationalisation ---
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- Fichiers Statiques et Médias ---
# Fichiers statiques (CSS, JS du projet)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Configuration R2/S3
cdn_domain = os.getenv("R2_CDN_DOMAIN", "").strip()
if cdn_domain.startswith("http://") or cdn_domain.startswith("https://"):
    MEDIA_URL = cdn_domain + "/"
else:
    MEDIA_URL = "https://" + cdn_domain + "/" if cdn_domain else "/media/"

if DEBUG:
    MEDIA_ROOT = BASE_DIR / 'media'
else:
    MEDIA_ROOT = BASE_DIR / 'media'

# --- Configuration S3/R2 ---
if os.getenv("USE_R2", "False").lower() == "true":
    USE_S3 = True
    AWS_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL", "").strip()
    AWS_S3_REGION_NAME = 'auto'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_S3_ADDRESSING_STYLE = 'path'
    AWS_DEFAULT_ACL = None
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    R2_CDN_DOMAIN = os.getenv("R2_CDN_DOMAIN", "").strip()

# --- Configuration des Services Tiers ---

# Configuration Email (Brevo)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

# Configuration Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


# --- Configuration de Sécurité et Performance ---

# Validation des mots de passe (CORRECTION D'UNE FAUTE DE FRAPPE)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, # CORRIGÉ
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Type de champ de clé primaire par défaut
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration pour Unfold (thème de l'admin)
UNFOLD_THEME = 'default'
UNFOLD_DEFAULT_LANGUAGE = 'fr'
UNFOLD_DEFAULT_COUNTRY = 'FR'

# Limites pour l'upload de gros fichiers (2 Go)
DATA_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 1024 * 2
FILE_UPLOAD_MAX_MEMORY_SIZE = 1024 * 1024 * 1024 * 2

# Configuration CORS
# En développement, on autorise toutes les origines pour les tests.
# En production, il faudra absolument restreindre cela.
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
else:
    CORS_ALLOWED_ORIGINS = [
        "https://vicarious-cucullately-davian.ngrok-free.dev",  # Remplacez par votre domaine en production
    ]
    CORS_ALLOW_CREDENTIALS = True


# Ces paramètres ne sont activés que lorsque DEBUG=False.
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    X_FRAME_OPTIONS = 'DENY'

# === AUTHENTIFICATION PAR EMAIL UNIQUEMENT ===
AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
)

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False            

ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"     

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# === SOCIAL LOGIN (GOOGLE) ===
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online", "prompt": "select_account"},
        "OAUTH_PKCE_ENABLED": True,
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "key": "",
        },
    }
}
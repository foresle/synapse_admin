from pathlib import Path
from environs import Env

env = Env()
env.read_env('.env')

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env('DJANGO_SECRET_KEY', default='5yhb5xv1pmi(1%_-fjon7@4ut()kt1+bhc3zneq(kf%5r@1h!6')
DEBUG = env.bool('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = []


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_bootstrap5',

    # Local apps
    'users.apps.UsersConfig',
    'dashboard.apps.DashboardConfig',
    'server_notices.apps.ServerNoticesConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'synapse_admin.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'synapse_admin.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = 'staticfiles/'
STATICFILES_DIRS = (
    BASE_DIR / 'static',
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MATRIX_ADMIN_TOKEN = env('MATRIX_ADMIN_TOKEN')
MATRIX_DOMAIN = env('MATRIX_DOMAIN')

# Redis
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_LOCATION', default='redis://redis:6379/'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

BOOTSTRAP5 = {
    "css_url": {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/css/bootstrap.min.css",
        "integrity": "sha384-gH2yIJqKdNHPEq0n4Mqa/HGKIhSkIHeL5AyhkYV8i59U5AR6csBvApHHNl/vI1Bx",
        "crossorigin": "anonymous",
    },
    "javascript_url": {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/js/bootstrap.bundle.min.js",
        "integrity": "sha384-A3rJD856KowSb7dwlZdYEkO39Gagi7vIsF0jrRAoQmDKKtQBHUuLZ9AsSv4jD4Xa",
        "crossorigin": "anonymous",
    },
    'wrapper_class': 'mb-3',
    'inline_wrapper_class': '',
    'horizontal_label_class': 'col-sm-2',
    'horizontal_field_class': 'col-sm-10',
    'horizontal_field_offset_class': 'offset-sm-2',
    'set_placeholder': True,
    'required_css_class': '',
    'error_css_class': '',
    'success_css_class': '',
    'server_side_validation': True,
    'formset_renderers':{
        'default': 'django_bootstrap5.renderers.FormsetRenderer',
    },
    'form_renderers': {
        'default': 'django_bootstrap5.renderers.FormRenderer',
    },
    'field_renderers': {
        'default': 'django_bootstrap5.renderers.FieldRenderer',
    },
}
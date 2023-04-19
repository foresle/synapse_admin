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
    'rooms.apps.RoomsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'project.urls'

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

WSGI_APPLICATION = 'project.wsgi.application'

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
STATIC_ROOT = '/staticfiles/'
STATICFILES_DIRS = (
    BASE_DIR / 'static',
)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Bootstrap forms
BOOTSTRAP5 = {
    "css_url": {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css",
        "integrity": "sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3",
        "crossorigin": "anonymous",
    },
    "javascript_url": {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js",
        "integrity": "sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p",
        "crossorigin": "anonymous",
    }
}

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

# Cached values constants
CACHED_USERS: str = 'users'
CACHED_USERS_UPDATED_AT: str = 'users_updated_at'

CACHED_ROOMS: str = 'rooms'
CACHED_ROOMS_UPDATED_AT: str = 'rooms_updated_at'

CACHED_SERVER_MAP: str = 'server_map'
CACHED_SERVER_MAP_UPDATED_AT: str = 'server_map_updated_at'

CACHED_MEDIA_STATISTICS: str = 'media_statistics'
CACHED_MEDIA_STATISTICS_UPDATED_AT: str = 'media_statistics_updated_at'

# CELERY
CELERY_BEAT_SCHEDULE = {
    'update_users_info_every_30m': {
        'task': 'users.tasks.update_users_info',
        'schedule': 60 * 30
    },
    'update_rooms_info_every_30m': {
        'task': 'rooms.tasks.update_rooms_info',
        'schedule': 60 * 30
    },
    'update_media_statistics_info_every_1h': {
        'task': 'dashboard.tasks.update_media_statistics_info',
        'schedule': 60 * 60
    },
    'update_server_map_every_12h': {
        'task': 'users.tasks.dashboard.tasks.update_server_map',
        'schedule': 60 * 60 * 12
    },
}
CELERY_BROKER_URL = env('REDIS_LOCATION', default='redis://redis:6379/')

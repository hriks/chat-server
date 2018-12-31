import os
import redis

DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://localhost:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

CELERY_BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
BROKER_URL = 'redis://localhost:6379/0'
REDIS_POOL = redis.ConnectionPool.from_url(BROKER_URL)

# Number of seconds of inactivity before a user is marked offline
USER_ONLINE_TIMEOUT = 120  # 2 minutes

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

WEBSOCKET_URL = '/ws/'

WS4REDIS_EXPIRE = 0

WS4REDIS_PREFIX = 'ws'

WSGI_APPLICATION = 'ws4redis.django_runserver.application'

STATIC_URL = '/static/'

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'ws4redis',
    'chat'
]

WS4REDIS_HEARTBEAT = '--heartbeat--'

SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS_PREFIX = 'session'


if DEBUG:
    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, "static"),
    ]
else:
    STATIC_ROOT = "static"

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'server.middleware.active_user_middleware'
]

ROOT_URLCONF = 'server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'chat/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ws4redis.context_processors.default'
            ],
        },
    },
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR + '/media'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get('CHAT_DB_NAME', 'server'),
        'USER': os.environ.get('USERNAME', 'hriks'),
        'PASSWORD': os.environ['PASSWORD'],
        'HOST': os.environ.get('HOST', 'localhost'),
        'PORT': '5432',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',   # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',   # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',   # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',   # noqa
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

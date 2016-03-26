"""
Django settings for datacollection project.

Generated by 'django-admin startproject' using Django 1.8.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import djcelery
from datetime import timedelta


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '#rc10q6ynnusxldhmy$zevz8-&!k+^xxxsq24*ojo+h^!y3*zo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


djcelery.setup_loader()


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'jquery',
    'bootstrap3',
    'twitter',
    'user_profile',
    'newsscraper',
    'overview',
    'tweepy',
    'celery',
    'djcelery',
    'sendfile',
    'djng',
    'rest_framework',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'datacollection.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
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

WSGI_APPLICATION = 'datacollection.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'django': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
            'formatter': 'verbose'
        },
        'twitter': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'twitter.log',
            'formatter': 'verbose'
        },
        'newsscraper': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'newsscraper.log',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['django'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'twitter': {
            'handlers': ['twitter'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'newsscraper': {
            'handlers': ['newsscraper'],
            'propagate': True,
            'level': 'DEBUG',
        },
        'celery': {
            'handlers': ['twitter'],
            'propagate': True,
            'level': 'DEBUG',
        },

    },
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

LOGIN_URL = '/login/'

BROKER_URL = 'amqp://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'

# expiration of task is default one or several days, must be 30 days
CELERYCAM_EXPIRE_SUCCESS = timedelta(days=30)
CELERYCAM_EXPIRE_ERROR = timedelta(days=30)
CELERYCAM_EXPIRE_PENDING = timedelta(days=30)
# always eager for debugging purposes REMOVE IN PRODUCTION => code runs in one thread
# CELERY_ALWAYS_EAGER = True

# email configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'datacoll3ction@gmail.com'
EMAIL_HOST_PASSWORD = 'nJuhUpoiuK'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# sendfile configuration
SENDFILE_BACKEND = 'sendfile.backends.development'
SENDFILE_ROOT = os.path.join(BASE_DIR, 'csv_data')
SENDFILE_URL = '/csv_data'
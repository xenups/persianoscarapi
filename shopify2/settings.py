"""
Django settings for shopify2 project.

Generated by 'django-admin startproject' using Django 2.2.3.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""
# hello sanctions
import environ

from oscar.defaults import *
import os
from oscar import OSCAR_MAIN_TEMPLATE_DIR, get_core_apps

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'a%q=9pm!%&g4(r%-^jn9w@%mdei3bdc2%5uskvg1lsu!c#hnqm'
OSCAR_SHOP_NAME = "اسم فروشگاه"

OSCAR_DEFAULT_CURRENCY = 'IRR'
# OSCAR_PROMOTION_POSITIONS = (('catalogue', 'Catalogue'),
#                              ('right', 'Right-hand sidebar'),
#                              ('left', 'Left-hand sidebar'))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = "amqp"
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESTFUL_SERIALIZER = 'json'
CELERY_AMQP_TASK_RESULT_EXPIRES = 1000

ALLOWED_HOSTS = ['192.168.1.108', '*']

PAYPAL_API_USERNAME = 'xenups-facilitator_api1.outlook.com'
PAYPAL_API_PASSWORD = '2T6697D6TBDVLUB2'
PAYPAL_API_SIGNATURE = 'A7p6fVEnuk.MdrcJwzVkpTMf2gU0AFGHF6xFDE5Vh35S-7iZ7OksA2qc'
# Application definition

INSTALLED_APPS = [
                     'django.contrib.admin',
                     'django.contrib.auth',
                     'django.contrib.sites',
                     'django.contrib.contenttypes',
                     'django.contrib.sessions',
                     'django.contrib.messages',
                     'django.contrib.staticfiles',
                     'django.contrib.sitemaps',
                     'django_extensions',

                     'django.contrib.flatpages',
                     'rest_framework',
                     'frobshop',
                     'compressor',
                     'widget_tweaks',
                     'catalogue',
                     'checkout',
                     'promotions',
                     'digital',
                     'guardian',
                     'paypal',
                     'pay_ir',

                 ] + get_core_apps()

SITE_ID = 1

from django.utils.translation import ugettext_lazy as _

PAY_IR_CONFIG = {
    "api_key": "test"
}

LOGIN_REDIRECT_URL = '/'
OSCAR_RECENTLY_VIEWED_PRODUCTS = 20
APPEND_SLASH = True
env = environ.Env()
THUMBNAIL_DEBUG = DEBUG
THUMBNAIL_KEY_PREFIX = 'oscar-sandbox'
THUMBNAIL_KVSTORE = env(
    'THUMBNAIL_KVSTORE',
    default='sorl.thumbnail.kvstores.cached_db_kvstore.KVStore')
THUMBNAIL_REDIS_URL = env('THUMBNAIL_REDIS_URL', default=None)

AUTHENTICATION_BACKENDS = (
    'oscar.apps.customer.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'whitenoise.middleware.WhiteNoiseMiddleware',

    # Allow languages to be selected
    'django.middleware.http.ConditionalGetMiddleware',

    # Ensure a valid basket is added to the request instance for every request

    'oscar.apps.basket.middleware.BasketMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

ROOT_URLCONF = 'shopify2.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/pay_ir'), os.path.join(BASE_DIR, 'templates/oscar'),
                 OSCAR_MAIN_TEMPLATE_DIR]
        ,
        'APP_DIRS': True,

        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.contrib.messages.context_processors.messages',

                'oscar.apps.search.context_processors.search_form',
                'oscar.apps.customer.notifications.context_processors.notifications',
                'oscar.apps.promotions.context_processors.promotions',
                'oscar.apps.checkout.context_processors.checkout',
                'oscar.core.context_processors.metadata',
            ],
        },
    },
]

WSGI_APPLICATION = 'shopify2.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
REST_FRAMEWORK = {
    'CHARSET': 'utf-8',
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

# if persian languages doesnt work properly just copy django.po and mo into fa-ir in local venv too
# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'fa'
LANGUAGES = (
    ('es', 'Spanish'),
    ('fa', 'fa'),
    ('en', 'English'),
)

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.simple_backend.SimpleEngine',
        'URL': 'http://127.0.0.1:8000/solr/default',
        'INCLUDE_SPELLING': True,
    },
}
env = environ.Env()
CACHES = {
    'default': env.cache(default='locmemcache://'),
}
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
OSCARAPI_BLOCK_ADMIN_API_ACCESS = True
location = lambda x: os.path.join(
    os.path.dirname(os.path.realpath(__file__)), x)
STATIC_ROOT = location('static')
MEDIA_URL = '/media/'
MEDIA_ROOT = location('media')

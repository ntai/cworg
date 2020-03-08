"""
Django settings for cworg project.

Generated by 'django-admin startproject' using Django 3.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8=!c#j8y!25*d=&g^oq6&q^t&8^q74prtouhd=@d*-lws0bkp%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'material',
    
    # rest framework
    'rest_framework',
    'crispy_forms',
    'markdown_deux',
    'pagedown',
    
    #
    'common.apps.CommonConfig',
    'dashboard.apps.DashboardConfig',
    'meets.apps.MeetsConfig',
    'teams.apps.TeamsConfig',
    'locations.apps.LocationsConfig',
    'userprofile.apps.UserProfileConfig',

    # test admin apps
    'django.contrib.flatpages',
    'django.contrib.redirects',
    'django.contrib.sites',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

SITE_ID = 1

LOGIN_URL = "/login/"
ROOT_URLCONF = 'cworg.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'cworg', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',

                'django.template.context_processors.i18n',

                # This sets the 'site_components' and 'current_site_component' for the context
                'common.sitemodule.context_processor',
            ],

            'builtins': [
                'material.templatetags.material_form',
            ],

            'debug': True,
        },
    },
]

WSGI_APPLICATION = 'cworg.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'cwinner_wednesday',
        'USER': 'cleanwinner',
        'PASSWORD': 'Roger.Federer=GOAT',
        'HOST': 'mysql.cleanwinner.com',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/


STATIC_URL = '/static/'

STATIC_ROOT = os.path.dirname(BASE_DIR) + '/public/static/'
#STATIC_ROOT = os.path.dirname(BASE_DIR) + '/static/'

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'public', 'media')
#MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'media')
MEDIA_URL = '/media/'

#
#
#
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },

    'handlers': {
        'django': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/django.log',
            'maxBytes': 2**24,
            'backupCount': 3,
            'formatter': 'verbose'
        },
        'cleanwinner': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/tmp/cw.log',
            'maxBytes': 2**24,
            'backupCount': 3,
            'formatter': 'verbose'
        },
    },

    'loggers': {
        'django': {
            'handlers': ['django'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'cw': {
            'handlers': ['cleanwinner'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

#
#
#




REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        # 'common.xml_renderer.XMLRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        #'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        #'rest_framework.authentication.BasicAuthentication',
    ), 
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        #'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    )
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Host for sending e-mail.
EMAIL_USE_TLS=True
EMAIL_HOST = 'mail.cleanwinner.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'cworg@cleanwinner.com'
EMAIL_HOST_PASSWORD = 'cleanwinner_password_is_here_1122'

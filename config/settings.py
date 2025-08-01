import os
import environ
from pathlib import Path


# Initialize environ
env = environ.Env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Reading .env file
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env(
    "SECRET_KEY", default="A$47&jg^&8@dnwdt67-g@w*ob@2#od*uvb51c+it3)8-05dmg8zgkw1"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
# DEBUG = True


ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "tcis-reports.onrender.com",
    "209.74.77.238",
    "reports.tcis.edu.gh",
]


# Application definition

INSTALLED_APPS = [
    "reports",
    "django_daisy",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Configuring Whitenoise to handle static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# if DEBUG == True :
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': BASE_DIR / 'db.sqlite3',
#         }}
# else:
# DATABASES = {
#         'default': {
#             'ENGINE': env('DB_ENGINE'),
#             'NAME': env('DB_NAME'),
#             'USER': env('DB_USER'),
#             'PASSWORD': env('DB_PASSWORD'),
#             'HOST': env('DB_HOST'),
#             'PORT': env('DB_PORT'),
#         }
#     }


DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST").strip(),
        "PORT": env("DB_PORT"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# Simplified static file serving.
# https://whitenoise.evans.io/en/stable/django.html#quickstart-for-django-apps

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# Media files config
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


LOGOUT_REDIRECT_URL = "/"
LOGIN_URL = "/"


# CSRF settings
CSRF_COOKIE_AGE = 28800  # 8 hours
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

SITE_URL = env("SITE_URL", default="reports.tcis.edu.gh")
LOGIN_URL = "/"
LOGOUT_URL = "/"


DAISY_SETTINGS = {
    "SITE_TITLE": "TCIS",  # The title of the site
    "SITE_HEADER": "Administration",  # Header text displayed in the admin panel
    "INDEX_TITLE": "Hi, welcome to your dashboard",  # The title for the index page of dashboard
    "SITE_LOGO": "/static/admin/img/tcis_logo.jpeg",  # Path to the logo image displayed in the sidebar
    "EXTRA_STYLES": [],  # List of extra stylesheets to be loaded in base.html (optional)
    "EXTRA_SCRIPTS": [],  # List of extra script URLs to be loaded in base.html (optional)
    "LOAD_FULL_STYLES": False,  # If True, loads full DaisyUI components in the admin (useful if you have custom template overrides)
    "SHOW_CHANGELIST_FILTER": False,  # If True, the filter sidebar will open by default on changelist views
    "APPS_REORDER": {
        # Custom configurations for third-party apps that can't be modified directly in their `apps.py`
        "auth": {
            "icon": "fa-solid fa-person-military-pointing",  # FontAwesome icon for the 'auth' app
            "name": "Authentication",  # Custom name for the 'auth' app
            "hide": False,  # Whether to hide the 'auth' app from the sidebar (set to True to hide)
            "app": "users",  # The actual app to display in the sidebar (e.g., rename 'auth' to 'users')
            "divider_title": "Auth",  # Divider title for the 'auth' section
        },
        "social_django": {
            "icon": "fa-solid fa-users-gear",  # Custom FontAwesome icon for the 'social_django' app
        },
    },
}

if DEBUG == False:
    X_FRAME_OPTIONS = "DENY"
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_HTTPONLY = True

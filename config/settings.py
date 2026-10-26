import os
from pathlib import Path
import dj_database_url
BASE_DIR=Path(__file__).resolve().parent.parent
SECRET_KEY=os.environ.get("DJANGO_SECRET_KEY","development-key-not-for-production")
DEBUG=os.environ.get("DJANGO_DEBUG","0")=="1"
ALLOWED_HOSTS=os.environ.get("DJANGO_ALLOWED_HOSTS","localhost,127.0.0.1").split(",")
CSRF_TRUSTED_ORIGINS=[x for x in os.environ.get("CSRF_TRUSTED_ORIGINS","").split(",") if x]
INSTALLED_APPS=["django.contrib.admin","django.contrib.auth","django.contrib.contenttypes","django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles","storages","world"]
MIDDLEWARE=["django.middleware.security.SecurityMiddleware","django.contrib.sessions.middleware.SessionMiddleware","django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware","django.contrib.auth.middleware.AuthenticationMiddleware","django.contrib.messages.middleware.MessageMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware"]
ROOT_URLCONF="config.urls"
TEMPLATES=[{"BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[BASE_DIR/"templates"],"APP_DIRS":True,"OPTIONS":{"context_processors":["django.template.context_processors.debug","django.template.context_processors.request","django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION="config.wsgi.application"
DATABASES={"default":dj_database_url.config(default="postgresql://ourworld:ourworld@db:5432/ourworld",conn_max_age=600)}
AUTH_PASSWORD_VALIDATORS=[{"NAME":"django.contrib.auth.password_validation.MinimumLengthValidator"},{"NAME":"django.contrib.auth.password_validation.CommonPasswordValidator"},{"NAME":"django.contrib.auth.password_validation.NumericPasswordValidator"}]
LANGUAGE_CODE="th"
TIME_ZONE="Asia/Bangkok"
USE_I18N=True
USE_TZ=True
STATIC_URL="/static/"
STATIC_ROOT=BASE_DIR/"staticfiles"
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"
LOGIN_URL="login"
LOGIN_REDIRECT_URL="home"
LOGOUT_REDIRECT_URL="login"
SESSION_COOKIE_HTTPONLY=True
CSRF_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE="Lax"
SESSION_COOKIE_SECURE=not DEBUG
CSRF_COOKIE_SECURE=not DEBUG
SECURE_HSTS_SECONDS=31536000 if not DEBUG else 0
SECURE_CONTENT_TYPE_NOSNIFF=True
X_FRAME_OPTIONS="DENY"
S3_BUCKET=os.environ.get("S3_BUCKET","")
if S3_BUCKET:
    STORAGES={"default":{"BACKEND":"storages.backends.s3.S3Storage"},"staticfiles":{"BACKEND":"django.contrib.staticfiles.storage.StaticFilesStorage"}}
    AWS_STORAGE_BUCKET_NAME=S3_BUCKET
    AWS_S3_REGION_NAME=os.environ.get("S3_REGION","auto")
    AWS_S3_ENDPOINT_URL=os.environ.get("S3_ENDPOINT_URL") or None
    AWS_ACCESS_KEY_ID=os.environ.get("S3_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY=os.environ.get("S3_SECRET_ACCESS_KEY")
    AWS_DEFAULT_ACL=None
    AWS_QUERYSTRING_AUTH=True
    AWS_QUERYSTRING_EXPIRE=300
    AWS_S3_FILE_OVERWRITE=False
else:
    STORAGES={"default":{"BACKEND":"django.core.files.storage.FileSystemStorage"},"staticfiles":{"BACKEND":"django.contrib.staticfiles.storage.StaticFilesStorage"}}
    MEDIA_ROOT=BASE_DIR/"media"

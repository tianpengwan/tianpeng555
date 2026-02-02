# 移除废弃的 MongoDB 字段导入（核心修改1）
# from django_mongodb_backend.fields import ObjectIdAutoField
# DEFAULT_AUTO_FIELD = 'django_mongodb_backend.fields.ObjectIdAutoField'

from pathlib import Path
import os
import json
import random
import logging
import urllib3

# 解决自定义异常导入问题（Vercel 部署时可能缺失）
try:
    import hexoweb.exceptions as exceptions
except ImportError:
    # 兜底：定义空异常类，避免部署报错
    class exceptions:
        class InitError(Exception):
            pass

urllib3.disable_warnings()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

LOGIN_REDIRECT_URL = "home"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("SECRET_KEY", 'django-insecure-mrf1flh+i8*!ao73h6)ne#%gowhtype!ld#+(j^r*!^11al2vz')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DEBUG", "False") == "True"

# 适配 Vercel 的 ALLOWED_HOSTS 配置（核心修改2）
try:
    if os.environ.get("VERCEL"):
        raise Exception("Vercel")

    import configs  # 本地部署
    ALLOWED_HOSTS = configs.DOMAINS
except:
    logging.info("获取本地配置文件失败, 使用环境变量获取配置")  # Serverless部署
    ALLOWED_HOSTS = json.loads(os.environ.get("DOMAINS", '["*"]'))  # 兜底默认值，避免报错

# Application definition
INSTALLED_APPS = [
    # 'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # 'django.contrib.staticfiles',
    'hexoweb.apps.ConsoleConfig',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {}  # 初始化数据库配置
errors = ""     # 初始化错误信息

try:
    if os.environ.get("VERCEL"):
        raise Exception("Vercel")

    import configs
    print("获取本地配置文件成功, 使用本地数据库配置")
    DATABASES = configs.DATABASES
except:
    print("开始加载环境变量中的数据库配置")
    # 修复缩进 + 逻辑（核心修改3）
    if os.environ.get("MONGODB_HOST"):  # 使用MONGODB
        print("使用环境变量中的MongoDB数据库")
        # 检查必要环境变量
        for env in ["MONGODB_HOST", "MONGODB_PORT", "MONGODB_PASS"]:
            if env not in os.environ:
                if env == "MONGODB_USER" and "MONGODB_USERNAME" in os.environ:
                    continue
                if env == "MONGODB_PASS" and "MONGODB_PASSWORD" in os.environ:
                    continue
                errors += f"\"{env}\" "
        
        # MongoDB 配置（适配 djongo）
        DATABASES = {
            'default': {
                'ENGINE': 'djongo',
                'ENFORCE_SCHEMA': False,
                'NAME': 'django',
                'CLIENT': {
                    'host': os.environ.get("MONGODB_HOST"),
                    'port': int(os.environ.get("MONGODB_PORT", 27017)),
                    'username': os.environ.get("MONGODB_USER") or os.environ.get("MONGODB_USERNAME") or "root",
                    'password': os.environ.get("MONGODB_PASS") or os.environ.get("MONGODB_PASSWORD") or "",
                    'authSource': os.environ.get("MONGODB_DB") or "admin",
                    'authMechanism': 'SCRAM-SHA-1'
                }
            }
        }
    elif os.environ.get("PG_HOST") or os.environ.get("POSTGRES_HOST"):  # 使用 PostgreSQL
        print("使用环境变量中的PostgreSQL数据库")
        for env in ["PG_HOST", "PG_PASS"]:
            if (env not in os.environ) and (env.replace("PG_", "POSTGRES_") not in os.environ):
                if env == "PG_USER" and "POSTGRES_USERNAME" in os.environ:
                    continue
                if env == "PG_PASS" and "POSTGRES_PASSWORD" in os.environ:
                    continue
                errors += f"\"{env}\" "
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get("PG_DB") or os.environ.get("POSTGRES_DB") or os.environ.get("POSTGRES_DATABASE") or "root",
                'USER': os.environ.get("PG_USER") or os.environ.get("POSTGRES_USERNAME") or os.environ.get("POSTGRES_USER") or "root",
                'PASSWORD': os.environ.get("PG_PASS") or os.environ.get("POSTGRES_PASSWORD"),
                'HOST': os.environ.get("PG_HOST") or os.environ.get("POSTGRES_HOST"),
                'PORT': os.environ.get("PG_PORT") or os.environ.get("POSTGRES_PORT") or 5432,
            }
        }
    elif os.environ.get("MYSQL_HOST"):  # 使用MYSQL
        print("使用环境变量中的MySQL数据库")
        for env in ["MYSQL_HOST", "MYSQL_PORT", "MYSQL_PASSWORD"]:
            if env not in os.environ:
                if env == "MYSQL_PASSWORD" and "MYSQL_PASS" in os.environ:
                    continue
                errors += f"\"{env}\" "
        import pymysql
        pymysql.install_as_MySQLdb()
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': os.environ.get('MYSQL_NAME') or os.environ.get('MYSQL_DB') or 'root',
                'HOST': os.environ.get('MYSQL_HOST'),
                'PORT': os.environ.get('MYSQL_PORT'),
                'USER': os.environ.get('MYSQL_USER') or os.environ.get('MYSQL_USERNAME') or 'root',
                'PASSWORD': os.environ.get('MYSQL_PASSWORD') or os.environ.get('MYSQL_PASS'),
                'OPTIONS': {'ssl': {'ca': False}}
            }
        }
        if os.environ.get("PLANETSCALE"):
            DATABASES["default"]["ENGINE"] = "hexoweb.libs.django_psdb_engine"
    else:   # 默认使用sqlite（适配Vercel，核心修改4）
        print("使用sqlite数据库（Vercel默认）")
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'qexo_data.db',  # 使用绝对路径，避免Vercel路径问题
            }
        }
    
    # 检查环境变量错误
    if errors:
        raise exceptions.InitError(f"\"{errors}\"环境变量未设置")

# 兜底：如果数据库配置为空，强制使用SQLite
if not DATABASES:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'qexo_data.db',
        }
    }

# Password validation
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
LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# STATIC_URL = '/static/'
# STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
# STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_build', 'static')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session 过期时间（保留你的配置）
SESSION_COOKIE_AGE = 86400

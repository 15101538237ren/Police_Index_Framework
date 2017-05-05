# -*- coding: utf-8 -*-
"""
Django settings for Police_Index_Framework project.

Generated by 'django-admin startproject' using Django 1.8.4.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from os.path import normpath,join
import djcelery,pickle
from celery.schedules import crontab
from datetime import timedelta
# Django settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Police_Index_Framework.settings')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

djcelery.setup_loader()

BROKER_URL = 'django://localhost:8000//'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler' # 定时任务
CELERY_RESULT_BACKEND = 'djcelery.backends.database:DatabaseBackend'
CELERY_ENABLE_UTC = False # 不是用UTC
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERY_TASK_RESULT_EXPIRES = 10 #任务结果的时效时间
CELERYD_LOG_FILE = BASE_DIR + "/data/celery_logs/celery.log" # log路径
CELERYBEAT_LOG_FILE = BASE_DIR + "/data/celery_logs/beat.log" # beat log路径
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml'] # 允许的格式

CELERYBEAT_SCHEDULE = {
    'exe-every-1-minute': {
        'task': 'process.tasks.scheduled_jobs',
        'schedule': crontab(minute='*/1'),
    },
    'exe-every-10-minute': {
    'task': 'process.tasks.get_peroidic_data',
    'schedule': crontab(minute='*/10'),
    },
}




# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hzwc@ti@_kfpvl@-jeh=8v4c7tfe30r@t&poho=a00-b)=0b6o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

STATIC_URL = '/static/'
STATIC_ROOT = normpath(join(BASE_DIR,  'static', 'root'))
STATICFILES_DIRS = (
    normpath(join(BASE_DIR, 'static')),
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'bootstrap3',
    'process',
    'djcelery',
    'kombu.transport.django',
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
    'process.middleware.IPAuthenticationMiddleware'
)

ROOT_URLCONF = 'Police_Index_Framework.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                'django.core.context_processors.static',
                'django.core.context_processors.tz',
                "django.contrib.messages.context_processors.messages",
                "django.core.context_processors.request"
            ],
        },
    },
]


WSGI_APPLICATION = 'Police_Index_Framework.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases
DEPLOY = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'police_index',
        'USER': '' if DEPLOY else 'ren',
        'PASSWORD': '' if DEPLOY else 'harry123',
        'HOST': '' if DEPLOY else 'localhost',
        'PORT': '3306',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

#LANGUAGE_CODE = 'zh-CN'
LANGUAGE_CODE = 'zh-Hans'
TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

roadset_pkl_file = open(BASE_DIR+ os.sep+ "data"+os.sep+"boundary.pkl","rb")
roadset = pickle.load(roadset_pkl_file)
roadset_pkl_file.close()

API_KEY = "a296cc76f8fb3fd96208cb21e1ed3242"
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/
#APP事故和违法对应的数据库配置
DB_APP = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mobile_bjjj',
        'USER': 'zcbl_select',
        'PASSWORD': 'zcbl_select',
        'HOST': '192.166.8.8',
        'PORT': '3306',
    }
#122事故的数据库配置
DB_122 = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '122_transfer',
        'USER': 'zcbl_select',
        'PASSWORD': 'zcbl_select',
        'HOST': '192.166.31.6',
        'PORT': '3306',
    }
#各种表的名称
TABLE_OF_VIOLATION = 'breach_traffic_rules'
TABLE_OF_APP_INCIDENCE ="ig_task_info"
TABLE_OF_122_INCIDENCE = "t_zhzs"
REAL_CROWD_URL = 'https://tp-restapi.amap.com/gate?sid=30010&reqData={%22city%22:%22110000%22,%22dateType%22:0,%22userdefined%22:%22true%22}&serviceKey=2F77255FF77D948DF3FED20E0C19B14F'


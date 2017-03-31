from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = patterns('process.views',
 url(r'^index$','index',name='index'),
 url(r'^test_region_now','test_region_now',name='test_region_now'),
)
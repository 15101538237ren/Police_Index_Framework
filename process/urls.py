from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = patterns('process.views',
 url(r'^index$','index',name='index'),
 url(r'^train','train_region',name='train_region'),
 url(r'^query_status','query_status',name='query_status'),
)
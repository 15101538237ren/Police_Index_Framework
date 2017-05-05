from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from process.views import *

urlpatterns = patterns('process.views',
 url(r'^index$','index',name='index'),
 url(r'^rindex$','realtime_index',name='realtime_index'),
 url(r'^train','train_region',name='train_region'),
 url(r'^query_status','query_status',name='query_status'),
 url(r'^stat','region_statistics',name='region_statistics'),
 url(r'^download','custom_download',name='custom_download'),
 url(r'^load_region_statistics','load_region_statistics',name='load_region_statistics'),
 url(r'^gate', 'getRealTimePoliceIndex', name='getRealTimePoliceIndex'),
 url(r'^dadui', 'dadui_visualize', name='dadui_visualize'),
 url(r'^init', 'init_db_of_call_incidences', name='init_db_of_call_incidences')
)
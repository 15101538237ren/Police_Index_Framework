# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from import_data import import_police_data
def index(request):
    input_file_path = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2017/police/201612.xls"
    year = 2016
    month = 12
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
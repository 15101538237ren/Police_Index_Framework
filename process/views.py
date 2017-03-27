# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from import_data import import_police_data
def index(request):
    input_file_path = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2017/police/201701.xls"
    year = 2017
    month = 1
    import_police_data(input_file_path,year,month)
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
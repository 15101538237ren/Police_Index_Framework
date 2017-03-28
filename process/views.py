# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from import_data import import_call_incidence_data
def index(request):
    input_file_path = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2017/shuju/122_17-02.xls"
    path_pkl_path = "/Users/Ren/PycharmProjects/PoliceIndex/boundary.pkl"
    # import_app_incidence_data(input_file_path)
    import_call_incidence_data(input_file_path,path_pkl_path)
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
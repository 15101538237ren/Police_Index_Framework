# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from import_data import import_call_incidence_data
from train import *
from helpers import pinyin_hash

def index(request):
    input_file_path = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2017/shuju/122_17-02.xls"
    path_pkl_path = "/Users/Ren/PycharmProjects/PoliceIndex/boundary.pkl"
    # import_app_incidence_data(input_file_path)
    #import_call_incidence_data(input_file_path,path_pkl_path)
    from_time = datetime.datetime(2017,2,1,0,0,0,0)
    to_time = datetime.datetime(2017,2,28,23,59,59,0)
    # time_list = generate_str_arr_from_date_to_date(from_time,to_time,10)
    evecs = train(from_time, to_time, region=0, is_week=0, duration=10)
    pca_count = 2
    test_region(evecs,pca_count,from_time, to_time, region=pinyin_hash["chaoyang"], is_week=0, duration=10)
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
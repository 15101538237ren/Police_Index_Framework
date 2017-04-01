# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from process.train import *
from process.helpers import pinyin_hash,week_hash
import datetime
# evecs_tmp = np.array()
def index(request):
    region = int(request.POST.get("train_region", 0))
    week_agg = int(request.POST.get("week_agg", 0))
    from_date = request.POST.get("date_start", "2017-02-01")
    start_time = "0:0:0"
    end_time = "23:59:59"
    end_date = request.POST.get("date_end", "2017-02-28")
    start_dt = datetime.datetime.strptime(from_date + " " + start_time, "%Y-%m-%d %H:%M:%S")
    end_dt = datetime.datetime.strptime(end_date + " " + end_time, "%Y-%m-%d %H:%M:%S")
    duration = 10
    trainRegion(start_dt, end_dt, region, week_agg, duration)
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
def a(request):
    if request.method == 'GET':
        regions = region_hash
        week_agg = week_hash
        ab=1
        return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
    else:
        region = int(request.POST.get("train_region",0))
        week_agg = int(request.POST.get("week_agg",0))
        from_date = request.POST.get("date_start","2017-02-01")
        start_time = "0:0:0"
        end_time = "23:59:59"
        end_date = request.POST.get("date_end","2017-02-28")
        start_dt = datetime.datetime.strptime(from_date+" "+start_time, "%Y-%m-%d %H:%M:%S")
        end_dt  = datetime.datetime.strptime(end_date+" "+end_time, "%Y-%m-%d %H:%M:%S")
        duration = 10
        pca_no = 2
        evecs = train(start_dt, end_dt, region=region, is_week=week_agg, duration=duration)
        if all( evecs[:,0] < np.zeros(len(evecs[:,0]))):
            evecs = evecs * -1
        app_incidence = evecs[0,0]
        violation = evecs[1,0]
        call_incidence =  evecs[2,0]
        crowd_index = evecs[3,0]
        evecs_tmp = evecs
        regions = region_hash
        week_agg = week_hash
        return render_to_response('process/pca_rst.html', locals(), context_instance=RequestContext(request))

def test_region_now(request):

    if request.method == 'POST':
        region = int(request.POST.get("train_region",0))
        week_agg = int(request.POST.get("week_agg",0))
        from_date = request.POST.get("date_start","2017-02-01")
        start_time = "0:0:0"
        end_time = "23:59:59"
        end_date = request.POST.get("date_end","2017-02-28")
        start_dt = datetime.datetime.strptime(from_date+" "+start_time, "%Y-%m-%d %H:%M:%S")
        end_dt  = datetime.datetime.strptime(end_date+" "+end_time, "%Y-%m-%d %H:%M:%S")
        duration = 10
        pca_no = 0
        evecs = train(start_dt, end_dt, region=region, is_week=week_agg, duration=duration)
        test_region(evecs,pca_no,start_dt, end_dt, region = region, is_week=week_agg, duration=duration)
        return render_to_response('process/pca_rst.html', locals(), context_instance=RequestContext(request))
def index2(request):
    input_file_path = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2017/shuju/122_17-02.xls"
    path_pkl_path = "/Users/Ren/PycharmProjects/PoliceIndex/boundary.pkl"
    # import_app_incidence_data(input_file_path)
    #import_call_incidence_data(input_file_path,path_pkl_path)
    from_time = datetime.datetime(2017,2,1,0,0,0,0)
    to_time = datetime.datetime(2017,2,28,23,59,59,0)
    is_week = 1
    duration = 10
    pca_no = 0
    train_region = 0
    test_region_no = pinyin_hash["chaoyang"]
    # time_list = generate_str_arr_from_date_to_date(from_time,to_time,10)
    evecs = train(from_time, to_time, region=train_region, is_week=is_week, duration=duration)
    test_region(evecs,pca_no,from_time, to_time, region = test_region_no, is_week=is_week, duration=duration)
    # print evecs[:,0]
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
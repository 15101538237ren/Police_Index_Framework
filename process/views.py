# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from process.train import *
from process.helpers import pinyin_hash,week_hash,ajax_required,success_response
from import_data import *
from helpers import region_hash_anti
import datetime,calendar
# evecs_tmp = np.array()
def index(request):
    year = 2017
    month = 2
    is_region = 1
    week_agg = 0
    duration = 10

    from_dt = datetime.datetime(year,month,1,0,0,0,0)
    if month !=12:
        end_dt = datetime.datetime(year,month+1,1,0,0,0,0)
    else:
        end_dt = datetime.datetime(year+1,1,1,0,0,0,0)

    dt_list = generate_str_arr_from_date_to_date(from_dt,end_dt,duration_minute=duration)
    slider_cnts = len(dt_list)

    # trainRegion(start_time = start_dt, end_time = end_dt, is_region = is_region, is_week= week_agg, duration=10)
    query_time = datetime.datetime.strptime("2017-02-10 11:30:00", "%Y-%m-%d %H:%M:%S")
    district_ids = pinyin_hash.values()
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
@ajax_required
def query_status(request):
    datetime_query = request.GET.get("query_dt","2017-02-01 0:0:0")
    datetime_query = datetime.datetime.strptime(datetime_query, "%Y-%m-%d %H:%M:%S")

    region_pca = OutputRegionIndex(datetime_query, duration=10)
    region_labels = {}
    for k,v in region_pca.iteritems():
        region_name = region_hash_anti[int(k)]
        region_index = v
        label = region_name + u":" + str(region_index/100.0)
        region_labels[k]= label
    for k,v in region_labels.iteritems():
        region_pca['r_'+k] = v
    return success_response(**region_pca)
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
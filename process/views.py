# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from process.train import *
from process.helpers import pinyin_hash,week_hash,ajax_required,success_response
from import_data import *
from helpers import region_hash_anti
import datetime
from django.db.models import Max
from os.path import normpath,join
from Police_Index_Framework.settings import BASE_DIR
from django.views.decorators.http import require_GET, require_POST
# evecs_tmp = np.array()
duration = 10
def index(request):
    year = 2017
    month = 2
    is_region = 1
    week_agg = 0

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
def realtime_index(request):

    now_time_dt = datetime.datetime.now()
    now_time = now_time_dt.strftime("%H:%M:%S")
    year = 2017
    month = 2
    is_region = 1
    week_agg = 0

    from_dt = datetime.datetime(year,month,1,0,0,0,0)
    if month !=12:
        end_dt = datetime.datetime(year,month+1,1,0,0,0,0)
    else:
        end_dt = datetime.datetime(year+1,1,1,0,0,0,0)

    dt_list = generate_str_arr_from_date_to_date(from_dt,end_dt,duration_minute=duration)
    slider_cnts = len(dt_list)

    # trainRegion(start_time = start_dt, end_time = end_dt, is_region = is_region, is_week= week_agg, duration=10)
    query_time = "2017:2:28:" + now_time

    district_ids = pinyin_hash.values()
    return render_to_response('process/real_time_index.html', locals(), context_instance=RequestContext(request))
@ajax_required
def query_status(request):

    year = 2017
    month = 2

    from_dt = datetime.datetime(year,month,1,0,0,0,0)
    if month !=12:
        end_dt = datetime.datetime(year,month+1,1,0,0,0,0)
    else:
        end_dt = datetime.datetime(year+1,1,1,0,0,0,0)

    real_time = int(request.GET.get("realtime",'0'))
    datetime_query = request.GET.get("query_dt","2017-02-01 0:0:0")
    dt_format="%Y-%m-%d %H:%M:%S"
    datetime_query = datetime.datetime.strptime(datetime_query,dt_format)

    if real_time:
        ct_time_str = format_time(datetime_query, dt_format)
        print ct_time_str
        datetime_query = datetime.datetime.strptime(ct_time_str, dt_format)
    qt = datetime.datetime(datetime_query.year,datetime_query.month,datetime_query.day,datetime_query.hour,0,0,0)
    region_pca = OutputRegionIndex(datetime_query, duration=duration)
    region_labels = {}
    for k,v in region_pca.iteritems():
        police_real = Police.objects.filter(create_time=qt,region=int(k))
        # if len(police_real)==0:
        #     police_real_cnt = -1
        # else:
        police_real_cnt = int(police_real[0].people_cnt)
        police_max = Police.objects.filter(create_time__range=[from_dt, end_dt],region=int(k)).aggregate(Max('people_cnt'))["people_cnt__max"]
        region_name = region_hash_anti[int(k)]
        region_index = v
        people_recommend = int((region_index/300.0)*police_max)
        label = region_name + u":" + str(region_index/100.0) +u"<br/> 实际警力:"+str(police_real_cnt)+u"<br/>建议警力:"+str(people_recommend)
        region_labels[k]= label
    for k,v in region_labels.iteritems():
        region_pca['r_'+k] = v
    return success_response(**region_pca)
def train_region(request):
    if request.method == 'GET':
        is_region = {u"所有区混合训练":0,u"区域分别训练":1}
        week_agg = week_hash
        return render_to_response('process/train.html', locals(), context_instance=RequestContext(request))
    else:
        is_region = int(request.GET.get("train_region",0))
        week_agg = int(request.GET.get("week_agg",0))
        from_date = request.GET.get("date_start","2017-02-01")
        start_time = "0:0:0"
        end_time = "23:59:59"
        end_date = request.GET.get("date_end","2017-02-28")
        start_dt = datetime.datetime.strptime(from_date+" "+start_time, "%Y-%m-%d %H:%M:%S")
        end_dt  = datetime.datetime.strptime(end_date+" "+end_time, "%Y-%m-%d %H:%M:%S")
        trainRegion(start_time = start_dt, end_time = end_dt, is_region = is_region, is_week= week_agg, duration=duration)
        ret_dict={}
        return success_response(**ret_dict)
@require_GET
def region_statistics(request):
        region = region_hash
        print BASE_DIR
        return render_to_response('process/statistics.html', locals(), context_instance=RequestContext(request))
@require_GET
@ajax_required
def load_region_statistics(request):
    region_id = int(request.GET.get("query_region",1))
    from_date = request.GET.get("date_start","2017-02-01")
    start_time = "0:0:0"
    end_time = "23:59:59"
    end_date = request.GET.get("date_end","2017-02-28")
    start_dt = datetime.datetime.strptime(from_date+" "+start_time, "%Y-%m-%d %H:%M:%S")
    end_dt  = datetime.datetime.strptime(end_date+" "+end_time, "%Y-%m-%d %H:%M:%S")
    dt_list = generate_str_arr_from_date_to_date(start_dt,end_dt,duration_minute=duration)
    json_load_file = normpath(join(BASE_DIR,  'static', 'data', 'region_index.json'))
    json_temp_wrt_file = normpath(join(BASE_DIR,  'static', 'data', 'temp_index.json'))
    get_region_index_to_json(json_load_file=json_load_file,tmp_wrt_file=json_temp_wrt_file,datetime_list=dt_list,region_id=region_id,duration=duration)
    response_addr = {'addr':'/static/data/temp_index.json'}
    return success_response(**response_addr)

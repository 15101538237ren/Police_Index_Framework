# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from process.train import *
from process.helpers import read_file,week_hash,ajax_required,success_response
from import_data import *
from crontab_jobs import *
from helpers import region_hash_anti
import datetime
from django.db.models import Max
from os.path import normpath,join
from Police_Index_Framework.settings import BASE_DIR,API_KEY
from django.views.decorators.http import require_GET, require_POST
from process.api import *

def custom_download(request):
    if request.method == 'GET':
        apikey = API_KEY
        return render_to_response('process/custom_download.html', locals(), context_instance=RequestContext(request))
    else:
        req = request.POST
        #查询的语句
        sql_content = req.get("sql_content", "")
        apikey = req.get("apikey", "")
        host = req.get("host", "")
        username = req.get("username", "")
        password = req.get("password", "")
        dbname = req.get("dbname", "")
        port = int(req.get("port", ""))

        if apikey != API_KEY or sql_content=="" or host=="" or username =="" or password =="" or dbname =="":
            return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
        else:
            rtn,filename = exe_sql_of_custom(host=host, username= username, password=password, dbname=dbname, port=port,sql_content=sql_content)
            if rtn!="":
                response = HttpResponse(read_file(rtn),
                            content_type='APPLICATION/OCTET-STREAM')  #设定文件头，这种设定可以让任意文件都能正确下载，而且已知文本文件不是本地打开
                response['Content-Disposition'] = 'attachment; filename='+filename #设定传输给客户端的文件名称
                response['Content-Length'] = os.path.getsize(rtn)  #传输给客户端的文件大小
                os.remove(rtn)
                return response
            else:
                errors = filename
                return render_to_response('process/errors.html', locals(), context_instance=RequestContext(request))

duration = 10
#大队边界可视化
def dadui_visualize(request):
    # dt_start = datetime.datetime(2017,1,1,0,0,0,0)
    dt_start = datetime.datetime(2016,5,4,0,0,0,0)
    # dt_start = datetime.datetime(2017,1,1,0,0,0,0)
    dt_end = datetime.datetime(2017,3,1,0,0,0,0)
    # getRealTimePoliceIndex(request)
    # import_violation_data_from_db(dt_start,dt_end)
    # get_crowd_index()
    # reload_dadui_boundary()
    # label_all_dadui_id_of_db(dt_start,dt_end)
    # get_peroidic_data()
    # generate_all_dadui_crowd_index(dt_start,dt_end)
    input_crowd_file_path = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2016_crowd.xlsx"
    output_file_path = "/Users/Ren/PycharmProjects/Police_Index_Framework/static/js/dadui_data.js"
    # wrt_data_to_js(output_file_path)
    # generate_datajs_dadui(output_file_path)
    # import_crowd_data(input_crowd_file_path=input_crowd_file_path)
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
def index(request):
    year = 2017
    month = 2
    is_region = 1
    week_agg = 0

    #按大队训练和测试
    is_group = 0

    from_dt = datetime.datetime(year,month,1,0,0,0,0)
    if month !=12:
        end_dt = datetime.datetime(year,month+1,1,0,0,0,0)
    else:
        end_dt = datetime.datetime(year+1,1,1,0,0,0,0)

    dt_list = generate_str_arr_from_date_to_date(from_dt, end_dt, duration_minute=duration)
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
    is_group = -1
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
        print(ct_time_str)
        datetime_query = datetime.datetime.strptime(ct_time_str, dt_format)
    qt = datetime.datetime(datetime_query.year,datetime_query.month,datetime_query.day,datetime_query.hour,0,0,0)
    region_pca, region_pca_xyzw = OutputRegionIndex(datetime_query, duration=duration,is_group=is_group)
    region_labels = {}
    for k,v in region_pca.items():
        if is_group > 0:
            #大队测试
            police_real = 0# Police.objects.filter(create_time=qt,group=int(k))
            police_max = 0#Police.objects.filter(create_time__range=[from_dt, end_dt],group=int(k)).aggregate(Max('people_cnt'))["people_cnt__max"]
            region_or_dadui_name = Region_Boundary.objects.filter(group=int(k))[0].group_name
        else:
            police_real = Police.objects.filter(create_time=qt,region=int(k))
            police_max = Police.objects.filter(create_time__range=[from_dt, end_dt],region=int(k)).aggregate(Max('people_cnt'))["people_cnt__max"]
            region_or_dadui_name = region_hash_anti[int(k)]
        police_real_cnt = int(police_real[0].people_cnt)
        people_recommend = int((v/3.0) * police_max)
        [PCA_app_accidence, PCA_violation, PCA_call_incidence, PCA_crowd_index] = region_pca_xyzw[k]
        label = region_or_dadui_name + u":" + str(v) +u"<br/> 实际警力:"+str(police_real_cnt)+u"<br/>建议警力:"+str(people_recommend)+u"<br/>122事故分指数:"+str(PCA_call_incidence)+u"<br/>拥堵延时分指数:"+str(PCA_crowd_index)+u"<br/>APP事故分指数:"+str(PCA_app_accidence)+u"<br/>违法分指数:"+str(PCA_violation)
        region_pca[k] = int(v * 100)
        region_labels[k]= label
    for k,v in region_labels.items():
        region_pca['r_'+k] = v
    return success_response(**region_pca)
def train_region(request):
    if request.method == 'GET':
        is_region = {u"所有区混合训练":0,u"区域分别训练":1}
        is_group = {u"不训练大队":-1, u"训练大队":1}
        week_agg = week_hash
        return render_to_response('process/train.html', locals(), context_instance=RequestContext(request))
    else:
        is_region = int(request.GET.get("train_region", 0))
        week_agg = int(request.GET.get("week_agg", 0))
        from_date = request.GET.get("date_start", "2017-02-01")
        is_group = int(request.GET.get("is_group", -1))
        start_time = "0:0:0"
        end_time = "23:59:59"
        end_date = request.GET.get("date_end","2017-02-28")
        start_dt = datetime.datetime.strptime(from_date+" "+start_time, "%Y-%m-%d %H:%M:%S")
        end_dt  = datetime.datetime.strptime(end_date+" "+end_time, "%Y-%m-%d %H:%M:%S")
        trainRegion(start_time = start_dt, end_time = end_dt, is_region = is_region, is_week= week_agg, duration=duration, is_group= is_group)
        ret_dict={}
        return success_response(**ret_dict)
@require_GET
def region_statistics(request):
        region = region_hash
        print(BASE_DIR)
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

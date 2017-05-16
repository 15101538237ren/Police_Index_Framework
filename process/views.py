# coding: utf-8
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse
from process.helpers import read_file,week_hash,ajax_required,success_response
from process.crontab_jobs import exe_sql_of_custom,get_app_incidence,get_call_incidence,get_violation,get_crowd_index
from os.path import normpath,join
from Police_Index_Framework.settings import BASE_DIR,API_KEY
from django.views.decorators.http import require_GET, require_POST
import os,urllib2,json,datetime,random
from crontab_jobs import save_prediction_info
from process.helpers import json_response
from process.models import Prediction_Info,Police,Region_Boundary,Crowd_Index
from Police_Index_Framework.settings import REAL_CROWD_URL,API_KEY
from process.train import generate_str_arr_from_date_to_date,trainRegion,get_region_index_to_json,format_time,OutputRegionIndex
from process.helpers import region_hash_anti,region_hash,pinyin_hash
from import_data import import_app_incidences_from_json,generate_datajs_dadui
from django.db.models import Max

#city: 表示城市
#order:(bool) 0表示按照指数的名称排序，1表示按照指数的大小排序（从大到小）
#serviceKey:
#callback:

def get_pseudo_index(region_pca, region_pca_xyzw,real_time_crowd_index,qt,region_id,data):
    police_from_dt = datetime.datetime(2017,2,1,0,0,0,0)
    police_end_dt = datetime.datetime(2017,3,1,0,0,0,0)
    daduis_of_region = Region_Boundary.objects.filter(region=region_id)
    dadui_cnt_of_region = float(len(daduis_of_region))
    region_index = region_pca[str(region_id)]
    [PCA_app_accidence, PCA_violation, PCA_call_incidence, PCA_crowd_index] = region_pca_xyzw[str(region_id)]
    PCA_app_accidence += (random.random()/1.0) * 0.5 - 0.25
    PCA_app_accidence = PCA_app_accidence if PCA_app_accidence > 0.1 else (random.random()/1.0) * 0.1 + 0.1

    PCA_violation += (random.random()/1.0) * 0.5 - 0.25
    PCA_violation = PCA_violation if PCA_violation > 0.1 else (random.random()/1.0) * 0.1 + 0.1
    PCA_call_incidence += (random.random()/1.0) * 0.5 - 0.25
    PCA_call_incidence = PCA_call_incidence if PCA_call_incidence > 0.1 else (random.random()/1.0) * 0.1 + 0.1

    PCA_crowd_index = real_time_crowd_index / 3.0 if real_time_crowd_index > 0 else (PCA_crowd_index + (random.random()/1.0 * 0.5)-0.25)
    PCA_crowd_index = PCA_crowd_index if PCA_crowd_index > 0.1 else (0.1 + random.random() * 0.1)

    r_index = PCA_app_accidence + PCA_violation + PCA_call_incidence + PCA_crowd_index

    police_reals = Police.objects.filter(create_time=qt,region=region_id)
    police_max = Police.objects.filter(create_time__range=[police_from_dt, police_end_dt],region=region_id).aggregate(Max('people_cnt'))["people_cnt__max"]
    if len(police_reals):
        police_real_cnt = int(int(police_reals[0].people_cnt)/ dadui_cnt_of_region + random.randint(5,15))
    else:
        police_real_cnt = random.randint(10,40)

    people_recommend = int((r_index/3.0) * (float(police_max) / dadui_cnt_of_region) + random.randint(5,10))
    people_recommend = people_recommend if people_recommend >= 10 else 10 + random.randint(0,5)

    data["index"] = r_index
    data["violation_index"] = PCA_violation
    data["accidents_index"] = PCA_app_accidence + PCA_call_incidence
    data["crowd_index"] = PCA_crowd_index
    data["real_police_cnt"] = police_real_cnt
    data["suggested_police_cnt"] = people_recommend
    return data

def dump_index_of(dt):
    req = urllib2.Request(REAL_CROWD_URL)
    res = urllib2.urlopen(req).read()
    result = json.loads(res.decode("utf-8"))
    data_list = []
    datetime_query = datetime.datetime(dt.year,dt.month,dt.day,dt.hour,dt.minute,0,0)
    qt = datetime.datetime(dt.year,dt.month,dt.day,dt.hour,0,0,0)

    duration = 10
    is_group = -1
    region_pca, region_pca_xyzw = OutputRegionIndex(datetime_query, duration=duration,is_group=is_group)
    if ("status" in result.keys()) and ("data" in result.keys()):
        if "code" in result["status"]:
            if result["status"]["code"] == 0:
                succ = 1
                for idx, data in enumerate(result["data"]):
                    real_time_crowd_index = -1.0
                    #real_time_crowd_index = #data["index"] if "index" in result["data"][idx].keys() else ((random.random()/1.0)*0.5 + 0.5)
                    id_str = data["id"] if "id" in result["data"][idx].keys() else ""
                    dadui_id = int(id_str.split("_")[1])
                    region_ids = Region_Boundary.objects.filter(group=dadui_id)
                    if len(region_ids) and region_ids[0].region!= -1:
                        region_id = region_ids[0].region
                        get_pseudo_index(region_pca, region_pca_xyzw,real_time_crowd_index,qt,region_id,data)
                        data_list.append(data)
                    else:
                        #没有行政区,按东西城的平均
                        data_tmp = []
                        for region_id in [1,2]:
                            data_of_temp = get_pseudo_index(region_pca, region_pca_xyzw,real_time_crowd_index,qt,region_id,data)
                            data_tmp.append(data_of_temp)
                        data["index"] = (data_tmp[0]["index"] + data_tmp[1]["index"])/2.0
                        data["violation_index"] = (data_tmp[0]["violation_index"] + data_tmp[1]["violation_index"])/2.0
                        data["accidents_index"] = (data_tmp[0]["accidents_index"] + data_tmp[1]["accidents_index"])/2.0
                        data["crowd_index"] = (data_tmp[0]["crowd_index"] + data_tmp[1]["crowd_index"])/2.0
                        data["real_police_cnt"] = int((data_tmp[0]["real_police_cnt"] + data_tmp[1]["real_police_cnt"])/2.0)
                        data["suggested_police_cnt"] = int((data_tmp[0]["suggested_police_cnt"] + data_tmp[1]["suggested_police_cnt"])/2.0)
                        region_id = -1

                    prediction_info = Prediction_Info(PCAx=float(data["accidents_index"])/2.0, PCAy=data["violation_index"], PCAz=float(data["accidents_index"])/2.0,
                                              PCAw=data["crowd_index"],expect_police=data["suggested_police_cnt"], real_police=data["real_police_cnt"],
                                              create_time=datetime_query, group=dadui_id, region=region_id,index=data["index"])
                    prediction_info.save()

                    data_list.append(data)
    print "finish dump_index_of %s" % dt.strftime("%Y-%m-%d %H:%M:%S")
    return data_list
def pre_dump_all_index_result():
    info_count = Prediction_Info.objects.count()
    print "info count %d" % info_count
    if info_count != 2736:
        Prediction_Info.objects.all().delete()
        print "delete all Prediction_Info objs"
        dt_start = datetime.datetime.strptime("2017-02-28 00:00:00","%Y-%m-%d %H:%M:%S")
        dt_end = datetime.datetime.strptime("2017-03-01 00:00:00","%Y-%m-%d %H:%M:%S")
        dt_tmp = dt_start
        interval_minutes = 10
        while dt_tmp < dt_end:
            dt_tmp += datetime.timedelta(minutes=interval_minutes)
            dump_index_of(dt_tmp)
    print "finish pre_dump_all_index_result!"
def get_real_time_index_of(dt):
    dt += datetime.timedelta(minutes=10)
    now_minute = int(dt.minute / 10) * 10
    datetime_query = datetime.datetime(2017,2,28,dt.hour,now_minute,0,0)
    req = urllib2.Request(REAL_CROWD_URL)
    res = urllib2.urlopen(req).read()
    result = json.loads(res.decode("utf-8"))
    data_list = []
    succ = 0

    if ("status" in result.keys()) and ("data" in result.keys()):
        if "code" in result["status"]:
            if result["status"]["code"] == 0:
                succ = 1
                for idx, data in enumerate(result["data"]):
                    real_time_crowd_index = data["index"] if "index" in result["data"][idx].keys() else ((random.random()/1.0)*0.5 + 0.5)
                    id_str = data["id"] if "id" in result["data"][idx].keys() else ""
                    dadui_id = int(id_str.split("_")[1])
                    prediction_infos = Prediction_Info.objects.filter(create_time=datetime_query, group=int(dadui_id))
                    if len(prediction_infos):
                        prediction_info = prediction_infos[0]
                    else:
                        prediction_info = Prediction_Info.objects.filter(create_time=datetime_query, region= -1)[0]
                    crowd_index_of_partial = real_time_crowd_index / 3.0
                    data["index"] = round(float(prediction_info.index) - float(prediction_info.PCAw) + float(crowd_index_of_partial),4)
                    data["violation_index"] = round(float(prediction_info.PCAy),4)
                    data["accidents_index"] = round(float(prediction_info.PCAx) + float(prediction_info.PCAz),4)
                    data["crowd_index"] = round(crowd_index_of_partial,4)
                    data["real_police_cnt"] = int(prediction_info.real_police)
                    suggested_police_cnt= (int(prediction_info.expect_police) + int(int(prediction_info.expect_police) * ((float(prediction_info.index) - data["index"])/float(prediction_info.index))))
                    data["suggested_police_cnt"] = suggested_police_cnt if suggested_police_cnt > 10 else 10 + random.randint(0,5)
                    data_list.append(data)
    return data_list
@json_response
def getRealTimePoliceIndex(request):
    # save_prediction_info()

    if request.method =='GET':
        req_dict = request.GET
    else:
        req_dict = request.POST

    apikey = req_dict.get("apikey", "")

    if apikey =="" or apikey != API_KEY:
        return []
    dt = datetime.datetime.now()
    return get_real_time_index_of(dt)

@ajax_required
def visulization_of_time(request):
    datetime_query = request.REQUEST.get("query_dt","2017-05-16 08:00:00")

    dt_format = "%Y-%m-%d %H:%M:%S"

    datetime_query = datetime.datetime.strptime(datetime_query,dt_format)
    data_list = get_real_time_index_of(datetime_query)
    region_pca = {}
    region_labels = {}
    for data in data_list:
        dadui_id = int(data["id"].split("_")[1])
        rindex = float(data["index"])
        region_or_dadui_name = data["name"]
        label = region_or_dadui_name + u":" + str(rindex) +u"<br/> 实际警力:"+str(data["real_police_cnt"])+u"<br/>建议警力:"+str(data["suggested_police_cnt"])+u"<br/>事故分指数:"+str(data["accidents_index"])+u"<br/>拥堵延时分指数:"+str(data["crowd_index"])+u"<br/>违法分指数:"+str(data["violation_index"])
        region_pca[str(dadui_id)] = int(rindex * 100)
        region_labels[str(dadui_id)]= label
    for k,v in region_labels.items():
        region_pca['r_'+k] = v
    return success_response(**region_pca)

def index_of_validation(request):
    get_crowd_index()
    year = 2017
    month = 2
    is_region = 1
    week_agg = 0
    #按大队训练和测试
    is_group = 1

    from_dt = datetime.datetime(year,month,1,0,0,0,0)
    if month !=12:
        end_dt = datetime.datetime(year,month+1,1,0,0,0,0)
    else:
        end_dt = datetime.datetime(year+1,1,1,0,0,0,0)
    duration = 10
    dt_list = generate_str_arr_from_date_to_date(from_dt, end_dt, duration_minute=duration)
    slider_cnts = len(dt_list)

    # trainRegion(start_time = start_dt, end_time = end_dt, is_region = is_region, is_week= week_agg, duration=10)
    query_time = datetime.datetime.strptime("2017-02-10 11:30:00", "%Y-%m-%d %H:%M:%S")
    if is_group > 0:
        district_ids = [item.group for item in Region_Boundary.objects.filter(region__gt=0)]
    else:
        district_ids = pinyin_hash.values()
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
@json_response
def getRealTimePoliceIndex_bk(request):
    # save_prediction_info()
    if request.method =='GET':
        req_dict = request.GET
    else:
        req_dict = request.POST

    apikey = req_dict.get("apikey", "")

    if apikey =="" or apikey != API_KEY:
        return []
    req = urllib2.Request(REAL_CROWD_URL)
    res = urllib2.urlopen(req).read()
    result = json.loads(res.decode("utf-8"))
    data_list = []
    succ = 0
    dt = datetime.datetime.now()
    now_minute = int(dt.minute / 10) * 10
    # datetime_query = datetime.datetime(2017,2,28,8,0,0,0)
    datetime_query = datetime.datetime(dt.year,dt.month,dt.day,dt.hour,now_minute,0,0)

    if ("status" in result.keys()) and ("data" in result.keys()):
        if "code" in result["status"]:
            if result["status"]["code"] == 0:
                succ = 1
                for idx, data in enumerate(result["data"]):
                    id_str = data["id"] if "id" in result["data"][idx].keys() else ""
                    dadui_id = int(id_str.split("_")[1])
                    print "dadui id %d " % dadui_id
                    prediction_infos = Prediction_Info.objects.filter(create_time=datetime_query, group=int(dadui_id))
                    if len(prediction_infos):
                        prediction_info = prediction_infos[0]
                        data["index"] = prediction_info.index
                        data["violation_index"] = prediction_info.PCAy
                        data["accidents_index"] = prediction_info.PCAx + prediction_info.PCAz
                        data["crowd_index"] = prediction_info.PCAw
                        data["real_police_cnt"] = prediction_info.real_police
                        data["suggested_police_cnt"] = prediction_info.expect_police
                        data_list.append(data)
                    else:
                        if dadui_id == 10001:
                            data["index"] = round(random.random() * 3.0, 4)
                            data["violation_index"] = round(data["index"] / 3.0, 4)
                            data["accidents_index"] = round(data["index"] / 3.0, 4)
                            data["crowd_index"] = round(data["index"] / 3.0, 4)
                            data["real_police_cnt"] = random.randint(50,100)
                            data["suggested_police_cnt"] = random.randint(50,100)
                            data_list.append(data)
    return data_list

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

        if apikey != API_KEY or sql_content=="" or host=="" or username =="" or dbname =="":
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

#大队边界可视化
def dadui_visualize(request):
    # dt_start = datetime.datetime(2017,1,1,0,0,0,0)
    dt_start = datetime.datetime(2017,5,1,0,0,0,0)
    # dt_start = datetime.datetime(2017,1,1,0,0,0,0)
    dt_end = datetime.datetime(2017,5,1,8,0,0,0)
    # input_file = "/Users/Ren/Downloads/20170505222412.json"
    # import_app_incidences_from_json(input_file)
    # get_app_incidence(dt_start,dt_end)
    # get_call_incidence(dt_start,dt_end)
    # get_violation(dt_start,dt_end)
    # get_crowd_index()
    # getRealTimePoliceIndex(request)
    # import_violation_data_from_db(dt_start,dt_end)
    # get_crowd_index()
    # reload_dadui_boundary()
    # label_all_dadui_id_of_db(dt_start,dt_end)
    # get_peroidic_data()
    # generate_all_dadui_crowd_index(dt_start,dt_end)
    # input_crowd_file_path = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2016_crowd.xlsx"
    output_file_path = "/Users/Ren/PycharmProjects/Police_Index_Framework/static/js/dadui_data.js"
    # wrt_data_to_js(output_file_path)
    generate_datajs_dadui(output_file_path)
    # import_crowd_data(input_crowd_file_path=input_crowd_file_path)
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))

def init_db_of_call_incidences(request):
    dt_start = datetime.datetime(2016,5,4,0,0,0,0)
    dt_end = datetime.datetime(2017,1,1,0,0,0,0)
    get_app_incidence(dt_start, dt_end)
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
def index(request):
    pre_dump_all_index_result()
    year = 2017
    month = 2
    is_region = 1
    week_agg = 0
    #按大队训练和测试
    is_group = 1
    vs_time = 1
    from_dt = datetime.datetime(year,month,1,0,0,0,0)
    if month !=12:
        end_dt = datetime.datetime(year,month+1,1,0,0,0,0)
    else:
        end_dt = datetime.datetime(year+1,1,1,0,0,0,0)
    duration = 10
    dt_list = generate_str_arr_from_date_to_date(from_dt, end_dt, duration_minute=duration)
    slider_cnts = len(dt_list)

    # trainRegion(start_time = start_dt, end_time = end_dt, is_region = is_region, is_week= week_agg, duration=10)
    query_time = datetime.datetime.strptime("2017-02-10 11:30:00", "%Y-%m-%d %H:%M:%S")
    if is_group > 0:
        district_ids = [item.group for item in Region_Boundary.objects.all()]
    else:
        district_ids = pinyin_hash.values()
    return render_to_response('process/index.html', locals(), context_instance=RequestContext(request))
def realtime_index(request):

    now_time_dt = datetime.datetime.now()
    now_time = now_time_dt.strftquery_statusime("%H:%M:%S")
    year = 2017
    month = 2
    is_region = 1
    week_agg = 0

    from_dt = datetime.datetime(year,month,1,0,0,0,0)
    if month !=12:
        end_dt = datetime.datetime(year,month+1,1,0,0,0,0)
    else:
        end_dt = datetime.datetime(year+1,1,1,0,0,0,0)
    duration = 10
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
    is_group = int(request.GET.get("is_group",-1))
    print "is_group %d" % is_group
    real_time = int(request.GET.get("realtime",'0'))
    datetime_query = request.GET.get("query_dt","2017-02-01 00:00:00")
    dt_format="%Y-%m-%d %H:%M:%S"
    datetime_query = datetime.datetime.strptime(datetime_query,dt_format)
    duration = 30
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
            police_real = 0#Police.objects.filter(create_time=qt,group=int(k))
            police_max = 100 #Police.objects.filter(create_time__range=[from_dt, end_dt],group=int(k)).aggregate(Max('people_cnt'))["people_cnt__max"]
            region_or_dadui_name = Region_Boundary.objects.filter(group=int(k))[0].group_name
            police_real_cnt = police_real
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
        duration = 30
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
    duration = 30
    dt_list = generate_str_arr_from_date_to_date(start_dt,end_dt,duration_minute=duration)
    json_load_file = normpath(join(BASE_DIR,  'static', 'data', 'region_index.json'))
    json_temp_wrt_file = normpath(join(BASE_DIR,  'static', 'data', 'temp_index.json'))
    get_region_index_to_json(json_load_file=json_load_file,tmp_wrt_file=json_temp_wrt_file,datetime_list=dt_list,region_id=region_id,duration=duration)
    response_addr = {'addr':'/static/data/temp_index.json'}
    return success_response(**response_addr)

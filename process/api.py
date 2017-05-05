# -*- coding: utf-8 -*-

##这个文件用来便于外部访问，请求实时指挥指数

import datetime,json
from process.models import Police,Prediction_Info, Region_Boundary
from helpers import region_hash_anti
from django.db.models import Max
from process.train import OutputRegionIndex
from django.http import JsonResponse
from process.helpers import json_response
import urllib2,random
from Police_Index_Framework.settings import REAL_CROWD_URL

def insertData():
    from_dt = datetime.datetime(2016, 12, 1, 0, 0, 0, 0)
    end_dt = datetime.datetime(2016, 12, 31, 0, 0, 0, 0)
    dt_list = []
    now_dt = from_dt
    while(now_dt <= end_dt):
        dt_list.append(now_dt)
        now_dt += datetime.timedelta(minutes=10)
    duration = 10
    for now_dt in dt_list:
        region_pca,region_pca_xyzw = OutputRegionIndex(now_dt, duration = duration)
        ##区县编号为k, 指数计算值为v
        for k, v in region_pca.items():
            police_real = Police.objects.filter(create_time=now_dt, region=int(k))
            police_real_cnt = int(police_real[0].people_cnt)
            police_max = \
            Police.objects.filter(create_time__range=[from_dt, end_dt], region=int(k)).aggregate(Max('people_cnt'))[
                "people_cnt__max"]
            region_name = region_hash_anti[int(k)]
            region_index = v / 100.0   ## 指挥指数
            people_recommend = int((region_index / 300.0) * police_max)
            label = region_name + u":" + str(region_index / 100.0) + u"<br/> 实际警力:" + str(
                police_real_cnt) + u"<br/>建议警力:" + str(people_recommend)
            tmp_pca_xyzw = region_pca_xyzw[k]
            PCA_x = tmp_pca_xyzw[0]
            PCA_y = tmp_pca_xyzw[1]
            PCA_z = tmp_pca_xyzw[2]
            PCA_w = tmp_pca_xyzw[3]
            predict_info = Prediction_Info(region=k, group=-1, PCAx=PCA_x, PCAy=PCA_y, PCAz=PCA_z, PCAw=PCA_w, index=region_index, expect_police=people_recommend, real_police=police_real_cnt, create_time=now_dt)
            predict_info.save()
#city: 表示城市
#order:(bool) 0表示按照指数的名称排序，1表示按照指数的大小排序（从大到小）
#serviceKey:
#callback:
@json_response
def getRealTimePoliceIndex(request):
    if request.method == "GET":
        # service = request.GET.get("service", None)
        # serviceKey = request.GET.get("serviceKey", None)
        # callback = request.GET.get("callback", None)
        # reqData = request.GET.get("reqData", None)
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
                        index = data["index"] if "index" in result["data"][idx].keys() else 0.0
                        data["violation_index"] = round(index/3.0 +random.random(),4)
                        data["accidents_index"] = round(index/3.0 +random.random(),4)
                        data["crowd_index"] = round(index/3.0 +random.random(),4)
                        data["real_police_cnt"] = random.randint(1,200)
                        data["suggested_police_cnt"] = random.randint(1,200)
                        data_list.append(data)
        if not succ:
            temp_data_list = [{"description":"","freespeed":42.9933,"id":"22_10002","index":1.8766,"name":"西单大队","number":1,"speed":14.946},
                        {"description":"","freespeed":39.0491,"id":"22_27","index":2.1908,"name":"东单大队","number":2,"speed":15.6774},
                        {"description":"","freespeed":28.176,"id":"22_15","index":1.236,"name":"府右街大队","number":3,"speed":11.576},
                        {"description":"","freespeed":47.3186,"id":"22_10004","index":2.3528,"name":"西外大队","number":4,"speed":20.1117},
                        {"description":"","freespeed":31.5018,"id":"22_28","index":2.152,"name":"东四大队","number":5,"speed":14.6384},
                        {"description":"","freespeed":39.0468,"id":"22_10001","index":0.4959,"name":"中心区交通支队","number":6,"speed":18.6298},
                        {"description":"","freespeed":43.02,"id":"22_29","index":1.4246,"name":"和平里大队","number":7,"speed":21.2481},
                        {"description":"","freespeed":30.2102,"id":"22_10003","index":1.7829,"name":"西四大队","number":8,"speed":15.2356},
                        {"description":"","freespeed":37.1552,"id":"22_16","index":1.1904,"name":"广安门大队","number":9,"speed":19.6548},
                        {"description":"","freespeed":42.0894,"id":"22_30","index":2.2588,"name":"前门大队","number":10,"speed":22.6428},
                        {"description":"","freespeed":46.9894,"id":"22_31","index":1.376,"name":"天坛大队","number":11,"speed":28.0366},
                        {"description":"","freespeed":47.6813,"id":"22_17","index":0.6297,"name":"樱桃园大队","number":12,"speed":29.3738}]
            data_list = temp_data_list
        return data_list

#callback:
@json_response
def test(request):
    req = urllib2.Request(REAL_CROWD_URL)
    res = urllib2.urlopen(req).read()
    result = json.loads(res.decode("utf-8"))
    data_list = []
    succ = 0
    dt = datetime.datetime.now()
    now_minute = int(dt.minute / 10) * 10
    duration = 10
    datetime_query = datetime.datetime(dt.year,dt.month,dt.day,dt.hour,now_minute,0,0)
    qt = datetime.datetime(datetime_query.year,datetime_query.month,datetime_query.day,datetime_query.hour,0,0,0)
    is_group = 1
    POLICE_FROM_DT = datetime.datetime.strptime("2016-12-01 00:00:00","%Y-%m-%d %H:%M:%S")
    POLICE_END_DT = datetime.datetime.strptime("2017-03-01 00:00:00","%Y-%m-%d %H:%M:%S")
    region_pca, region_pca_xyzw = OutputRegionIndex(datetime_query, duration=duration,is_group=is_group)
    if ("status" in result.keys()) and ("data" in result.keys()):
        if "code" in result["status"]:
            if result["status"]["code"] == 0:
                succ = 1
                for idx, data in enumerate(result["data"]):
                    id_str = data["id"] if "id" in result["data"][idx].keys() else ""
                    dadui_id = int(id_str.split("_")[1])
                    police_max = Police.objects.filter(create_time__range=[POLICE_FROM_DT, POLICE_END_DT],group=int(dadui_id)).aggregate(Max('people_cnt'))["people_cnt__max"]
                    index = region_pca[str(dadui_id)]

                    police_real =  Police.objects.filter(create_time=qt,group=int(dadui_id))
                    police_real_cnt = int(police_real[0].people_cnt)
                    people_recommend = int((index/3.0) * police_max)
                    [PCA_app_accidence, PCA_violation, PCA_call_incidence, PCA_crowd_index] = region_pca_xyzw[str(dadui_id)]
                    data["index"] = index
                    data["violation_index"] = PCA_violation
                    data["accidents_index"] = PCA_app_accidence + PCA_call_incidence
                    data["crowd_index"] = PCA_crowd_index
                    data["real_police_cnt"] = police_real_cnt
                    data["suggested_police_cnt"] =people_recommend
                    data_list.append(data)
    return data_list
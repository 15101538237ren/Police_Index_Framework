# -*- coding: utf-8 -*-

##这个文件用来便于外部访问，请求实时指挥指数

import datetime,json
from process.models import Police,Prediction_Info, Region_Boundary
from helpers import region_hash_anti
from django.db.models import Max
from process.train import *
from django.http import JsonResponse
from process.helpers import json_response
import urllib2,random


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



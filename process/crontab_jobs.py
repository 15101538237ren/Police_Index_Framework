# -*- coding: utf-8 -*-
import os,datetime
from process.models import *
import urllib,urllib2,json

#目前数据库中的所有大队id列表
group_ids = [item.group for item in Region_Boundary.objects.all()]

def get_crowd_index():
    real_index_url = 'https://tp-restapi.amap.com/gate?sid=30010&reqData={%22city%22:%22110000%22,%22dateType%22:0,%22userdefined%22:%22true%22}&serviceKey=2F77255FF77D948DF3FED20E0C19B14F'
    req = urllib2.Request(real_index_url)
    res = urllib2.urlopen(req).read()
    result = json.loads(res.decode("utf-8"))
    succ = 0
    if ("status" in result.keys()) and ("data" in result.keys()):
        if "code" in result["status"]:
            if result["status"]["code"] == 0:
                succ = 1
                for idx, data in enumerate(result["data"]):
                    group_id =  int(data["id"].split("_")[1]) if "id" in result["data"][idx].keys() else -1
                    group_name = data["name"] if "name" in result["data"][idx].keys() else u"非法"
                    if group_id == -1 or group_name == u"非法":
                        continue
                    if group_id not in group_ids:
                        rid = "22_"+str(group_id)
                        succ = get_boundary_of(rid, group_name)
                        group_ids.append(group_id)
                        print "get_boundary_of %s: %d" %(rid, succ)
                    index = data["index"] if "index" in result["data"][idx].keys() else 0.0
                    speed = data["speed"] if "speed" in result["data"][idx].keys() else 0.0
                    freespeed = data["freespeed"] if "freespeed" in result["data"][idx].keys() else 0.0
    return succ
#获取指定区域的id
def get_boundary_of(rid, group_name):
    boundary_url = 'https://tp-restapi.amap.com/gate?sid=30005&reqData={%22city%22:%22110000%22,%22linksType%22:22,%22ids%22:%22'+str(rid)+'%22}&serviceKey=2F77255FF77D948DF3FED20E0C19B14F'
    req = urllib2.Request(boundary_url)
    res = urllib2.urlopen(req).read()
    result = json.loads(res.decode("utf-8"))

    succ = 0
    if ("status" in result.keys()) and ("data" in result.keys()):
        if "code" in result["status"]:
            if result["status"]["code"] == 0:
                succ = 1
                group_id = result["data"]["id"] if "id" in result["data"].keys() else -1
                geo_boundary = result["data"]["geo"] if "geo" in result["data"].keys() else ""
                if group_id!=-1 and geo_boundary != "":
                    region_boundary = Region_Boundary(region=-1, group= group_id,group_name= group_name, geo_boundary=geo_boundary)
                    region_boundary.save()
                    print "id :%d, geo_len: %d" % (group_id, len(geo_boundary))
                else:
                    succ = 0
                    print "get boundary of %s failed" % rid
    return succ
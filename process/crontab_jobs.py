# -*- coding: utf-8 -*-
import os,datetime
from process.models import *
import urllib,urllib2,json,MySQLdb,pickle
from Police_Index_Framework.settings import roadset
from process.helpers import pinyin_hash,check_point
from process.convert import bd2gcj
from process.models import App_Incidence
from Police_Index_Framework.settings import BASE_DIR
from process.import_data import MAXINT

#目前数据库中的所有大队id列表
group_ids = [item.group for item in Region_Boundary.objects.all()]
group_shortnames = [item.group_short_name for item in Dadui_ID.objects.all()]

zhongche_host =''
zhongche_username = ''
zhongche_pwd = ''
zhongche_app_accidence_db_name = ''
zhongche_port = 3306

dadui_boundary_pkl_path = BASE_DIR + os.sep + "data" + os.sep + "dadui_boundary.pkl"
dadui_boundary_pklfile = open(dadui_boundary_pkl_path,"rb")
dadui_boundaries = pickle.load(dadui_boundary_pklfile)
dadui_boundary_pklfile.close()

dadui_regions = list(set([item_ddr.region_122_id for item_ddr in Dadui_ID.objects.filter(group_gaode_id__gt=-1)]))

def update_dadui_regions():
    global dadui_regions
    dadui_regions = list(set([item_ddr.region_122_id for item_ddr in Dadui_ID.objects.filter(group_gaode_id__gt=-1)]))
#重新加载大队边界的数据
def reload_dadui_boundary():
    dadui_boundaries_temp = Region_Boundary.objects.all()
    dadui_boundaries_rtn = []
    for dadui_boundary in dadui_boundaries_temp:
        region = dadui_boundary.region
        dadui_id = dadui_boundary.group
        dadui_name = dadui_boundary.group_name
        #区域编号尚未赋值
        if region == -1:
            region_id = Dadui_ID.objects.filter(group_gaode_id= dadui_id)
            if len(region_id) > 0:
                dadui_boundary.region = region_id[0].region_122_id
                dadui_boundary.save()

        geo_boundary = json.loads(dadui_boundary.geo_boundary)
        if len(geo_boundary) > 0:
            #多个边界区域
            dadui_boundaries_rtn_i = []
            if isinstance(geo_boundary[0],list):
                geo_boundary_list = [item for item in geo_boundary]
            else:
                geo_boundary_list = [geo_boundary]

            for gb in geo_boundary_list:
                boundary_dict = {}
                maxX = maxY = -MAXINT
                minX = minY = MAXINT
                group = dadui_id
                group_name = dadui_name
                region = dadui_boundary.region
                ll_list = []
                for item in gb:
                    x = item[u'x']
                    y = item[u'y']
                    if x > maxX:
                        maxX = x
                    if x < minX:
                        minX = x
                    if y > maxY:
                        maxY = y
                    if x < minY:
                        minY = y
                    ll_list.append([x,y])
                boundary_dict["maxX"] = maxX
                boundary_dict["maxY"] = maxY
                boundary_dict["minX"] = minX
                boundary_dict["minY"] = minY
                boundary_dict["group"] = group
                boundary_dict["group_name"] = group_name
                boundary_dict["region"] = region
                boundary_dict["data"] = ll_list
                dadui_boundaries_rtn_i.append(boundary_dict)
            dadui_boundaries_rtn.append(dadui_boundaries_rtn_i)
    outpkl_file = open(dadui_boundary_pkl_path,"wb")
    pickle.dump(dadui_boundaries_rtn,outpkl_file,-1)
    outpkl_file.close()
    return dadui_boundaries_rtn

def label_all_dadui_id_of_db(dt_start,dt_end):
    app_incidences = App_Incidence.objects.filter(create_time__range=[dt_start,dt_end])
    print "len app_incidences %d" % len(app_incidences)
    lbl_cnt = 0
    for idx,app_incidence in enumerate(app_incidences):
        lng = float(app_incidence.longitude)
        lat = float(app_incidence.latitude)

        #查询经纬度对应的大队id
        if (app_incidence.region in dadui_regions) and (app_incidence.group <= 0):
            for dadui_boundary in dadui_boundaries:
                flag_dadui = False
                for boundary_item in dadui_boundary:
                    if (not (boundary_item['minX'] <= lng and lng <= boundary_item['maxX'] and boundary_item['minY'] <=lat and lat <= boundary_item['maxY'])):
                        continue
                    flag_dadui = check_point(boundary_item["data"],lng,lat)
                    if flag_dadui:
                        app_incidence.group = boundary_item["group"]
                        app_incidence.save()
                        lbl_cnt += 1
                        break
                if flag_dadui:
                    break
        if idx % 10000 == 0:
                print "imported %d app_incidences, labeled %d " % (idx, lbl_cnt)

    violations = Violation.objects.filter(create_time__range=[dt_start,dt_end])
    print "len violations %d" % len(violations)
    lbl_cnt = 0
    for idx,violation in enumerate(violations):
        lng = float(violation.longitude)
        lat = float(violation.latitude)

        #查询经纬度对应的大队id
        if (violation.region in dadui_regions) and (violation.group <= 0):
            for dadui_boundary in dadui_boundaries:
                flag_dadui = False
                for boundary_item in dadui_boundary:
                    if (not (boundary_item['minX'] <= lng and lng <= boundary_item['maxX'] and boundary_item['minY'] <=lat and lat <= boundary_item['maxY'])):
                        continue
                    flag_dadui = check_point(boundary_item["data"],lng,lat)
                    if flag_dadui:
                        violation.group = boundary_item["group"]
                        violation.save()
                        lbl_cnt += 1
                        break
                if flag_dadui:
                    break
        if idx % 10000 == 0:
                print "imported %d violations, labeled %d " % (idx, lbl_cnt)

    call_incidences = Call_Incidence.objects.filter(create_time__range=[dt_start,dt_end])
    print "len call_incidences %d" % len(call_incidences)
    lbl_cnt = 0
    for idx,call_incidence in enumerate(call_incidences):
        lng = float(call_incidence.longitude)
        lat = float(call_incidence.latitude)

        #查询经纬度对应的大队id
        if (call_incidence.region in dadui_regions) and (call_incidence.group <= 0):
            for dadui_boundary in dadui_boundaries:
                flag_dadui = False
                for boundary_item in dadui_boundary:
                    if (not (boundary_item['minX'] <= lng and lng <= boundary_item['maxX'] and boundary_item['minY'] <=lat and lat <= boundary_item['maxY'])):
                        continue
                    flag_dadui = check_point(boundary_item["data"],lng,lat)
                    if flag_dadui:
                        call_incidence.group = boundary_item["group"]
                        call_incidence.save()
                        lbl_cnt += 1
                        break
                if flag_dadui:
                    break
        if idx % 10000 == 0:
                print "imported %d call_incidences, labeled %d " % (idx, lbl_cnt)
#定时获取中车的app事故数据
def get_app_incidence(dt_start,dt_end):
    try:
        conn=MySQLdb.connect(host=zhongche_host,user=zhongche_username,passwd=zhongche_username,db=zhongche_app_accidence_db_name,port=zhongche_port)
        cur=conn.cursor()
        cur.execute("select longitude, latitude, latlng_address, create_time from ig_task_info where proof_finish = '1' and create_time >= cast('"+dt_start.strftime("%Y-%m-%d %H:%M:%S")+"' as datetime) and create_time < cast('"+dt_end.strftime("%Y-%m-%d %H:%M:%S")+"' as datetime) ")

        result = cur.fetchall()

        print "len results %d" % len(result)
        for idx,(lng, lat, address, create_time) in enumerate(result):
            lng = float(lng)
            lat = float(lat)
            #先用百度的边界查询在哪个区
            for j in range(len(roadset)):
                if roadset[j]["name"] in pinyin_hash.keys():
                    if (not (roadset[j]['minX'] <= lng and lng <= roadset[j]['maxX'] and roadset[j]['minY'] <=lat and lat <= roadset[j]['maxY'])):
                        continue
                    data_set = roadset[j]["data"]
                    flag = check_point(data_set,lng,lat)
                    if flag:
                        region = pinyin_hash[roadset[j]["name"]]
                        point = [lng, lat]
                        lng,lat = bd2gcj(point)
                        #转换成高德坐标再存

                        #查询经纬度对应的大队id
                        group = -1
                        if region in dadui_regions:
                            for dadui_boundary in dadui_boundaries:
                                flag_dadui = False
                                for boundary_item in dadui_boundary:
                                    if (not (boundary_item['minX'] <= lng and lng <= boundary_item['maxX'] and boundary_item['minY'] <=lat and lat <= boundary_item['maxY'])):
                                        continue
                                    flag_dadui = check_point(boundary_item["data"],lng,lat)
                                    if flag_dadui:
                                        group = boundary_item["group"]
                                        break
                                if flag_dadui:
                                    break
                        app_incidence = App_Incidence(longitude=lng, latitude=lat, place=address, create_time=create_time, region=region, group = group)
                        app_incidence.save()
            print "imported %d app_incidences" % idx
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
         print "Mysql Error %d: %s" % (e.args[0], e.args[1])

#定时获取高德拥堵指数,存入数据库
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
                    group_shortname = group_name.replace(u"大队",u"")
                    #大队和122的有交集
                    if group_shortname in group_shortnames:
                        dadui = Dadui_ID.objects.filter(group_short_name=group_shortname)[0]
                        region = dadui.region_122_id
                        if dadui.group_gaode_id == -1:
                            dadui.group_gaode_id = group_id
                        if dadui.group_gaode_name.strip() == u"":
                            dadui.group_gaode_name = group_name
                        dadui.save()
                    else:
                        region = -1
                    index = data["index"] if "index" in result["data"][idx].keys() else 0.0
                    speed = data["speed"] if "speed" in result["data"][idx].keys() else 0.0
                    freespeed = data["freespeed"] if "freespeed" in result["data"][idx].keys() else 0.0
                    number = data["number"] if "number" in result["data"][idx].keys() else -1
                    create_time = datetime.datetime.now()
                    crowd_index = Crowd_Index(region=region, group=group_id,group_name=group_name,avg_car_speed=speed, freespeed=freespeed,crowd_index=index, create_time=create_time, number=number)
                    crowd_index.save()
    return succ

#没有rid对应的大队边界时,获取指定区域行政区边界,存入数据库
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
                    geo_boundary = json.dumps(geo_boundary)
                    region_boundary = Region_Boundary(region=-1, group= group_id,group_name= group_name, geo_boundary=geo_boundary)
                    region_boundary.save()
                    print "id :%d, geo_len: %d" % (group_id, len(geo_boundary))
                else:
                    succ = 0
                    print "get boundary of %s failed" % rid
                global dadui_boundaries
                dadui_boundaries = reload_dadui_boundary()
                update_dadui_regions()
    return succ
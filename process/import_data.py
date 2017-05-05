# -*- coding: utf-8 -*-
import xlrd,os,datetime,pytz,csv,calendar,json
from process.models import *
from process.helpers import pinyin_hash,check_point,region_hash2
from process.baidumap import BaiduMap
from process.convert import bd2gcj,gcj2bd
from Police_Index_Framework.settings import roadset
from crontab_jobs import dadui_regions
import MySQLdb
district_row_no = {"dongcheng":3, "xicheng":4, "chaoyang":5, "haidian":6,"fengtai":7,"shijingshan":8,"daxing":19}
sheet_idx = {2:"dongcheng",3:"xicheng",4:"haidian",5:"chaoyang",6:"daxing",7:"shijingshan",8:"fengtai"}
dadui_hash = {u"中关村(西苑)队":u"海淀",u"樱桃园大队":u"西城",u"亚运村队":u"朝阳",u"西外队":u"西城",u"西四队":u"西城",u"西单队":u"西城",u"温泉队":u"海淀",u"天坛大队":u"东城",u"双桥队":u"朝阳",u"清河队":u"海淀",u"前门大队":u"东城",u"劲松(东三环)队":u"朝阳",u"机场队":u"朝阳",u"黄庄(西三环)队":u"海淀",u"呼家楼队":u"朝阳",u"和平里队":u"东城",u"广安门大队":u"西城",u"公主坟队":u"海淀",u"府右街队":u"西城",u"东外队":u"朝阳",u"东四队":u"东城",u"东单队":u"东城",u"大红门队":u"丰台",u"方庄队":u"丰台",u"丰北队":u"丰台",u"卢沟桥队":u"丰台",u"西站队":u"丰台",}
excel_dict = {}
MAXINT = 999999999
LNG_INDEX = 0
LAT_INDEX = 1
EPS = 0.000001

#从另外一个数据库中将122报警数据导入到此数据库

def import_call_incidence_data_fromdb(dt_start,dt_end):
    try:
        conn=MySQLdb.connect(host='localhost',user='ren',passwd='harry123',db='accidents_prediction',port=3306)
        cur=conn.cursor()
        cur.execute("SELECT * FROM preprocessing_call_incidence where create_time >= cast('"+dt_start.strftime("%Y-%m-%d %H:%M:%S")+"' as datetime) and create_time < cast('"+dt_end.strftime("%Y-%m-%d %H:%M:%S")+"' as datetime) ")
        result = cur.fetchall()
        print "len results %d" % len(result)
        for idx,(id, removed, create_time, lng, lat, place) in enumerate(result):
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
                        call_incidence = Call_Incidence(region=region, group = 0,create_time = create_time, longitude=lng, latitude=lat, event_content=u"",place = place)
                        call_incidence.save()

            if idx % 10000 == 0:
                print "imported %d call incidences" % idx
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
         print "Mysql Error %d: %s" % (e.args[0], e.args[1])

def import_violation_data_from_db(dt_start,dt_end):
    try:
        conn=MySQLdb.connect(host='localhost',user='ren',passwd='harry123',db='accidents_prediction',port=3306)
        cur=conn.cursor()
        cur.execute("SELECT * FROM preprocessing_violation where create_time >= cast('"+dt_start.strftime("%Y-%m-%d %H:%M:%S")+"' as datetime) and create_time < cast('"+dt_end.strftime("%Y-%m-%d %H:%M:%S")+"' as datetime) ")
        result = cur.fetchall()
        print "len results %d" % len(result)
        for idx,(id, removed, lng, lat, create_time) in enumerate(result):
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
                        violation = Violation(breach_type= -1,region=region, group = 0,create_time = create_time, longitude=lng, latitude=lat)
                        violation.save()

            if idx % 10000 == 0:
                print "imported %d violations" % idx
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
         print "Mysql Error %d: %s" % (e.args[0], e.args[1])

#修正一些区的编号不正确的问题
def correct_region_id_of_db():
    print "start fetch violations"
    violations = Violation.objects.all()
    print "fetched %d violations" % len(violations)
    for idx,violation in enumerate(violations):
        region = violation.region
        #大兴修正
        if region == 8:
            violation.region = 15
            violation.save()
        #石景山修正
        elif region == 9:
            violation.region = 8
            violation.save()
        if idx % 10000 ==0:
            print "handle violation of %d objs" % idx

    print "start fetch call_incidences"
    call_incidences = Call_Incidence.objects.all()
    print "fetched %d call_incidences" % len(call_incidences)

    for idx,call_incidence in enumerate(call_incidences):
        region = call_incidence.region
        #大兴修正
        if region == 8:
            call_incidence.region = 15
            call_incidence.save()
        #石景山修正
        elif region == 9:
            call_incidence.region = 8
            call_incidence.save()

        if idx % 10000 ==0:
            print "handle call_incidence of %d objs" % idx

    print "start fetch app_incidences"
    app_incidences = App_Incidence.objects.all()
    print "fetched %d app_incidences" % len(app_incidences)

    for idx,app_incidence in enumerate(app_incidences):
        region = app_incidence.region
        #大兴修正
        if region == 8:
            app_incidence.region = 15
            app_incidence.save()
        #石景山修正
        elif region == 9:
            app_incidence.region = 8
            app_incidence.save()

        if idx % 10000 ==0:
            print "handle app_incidence of %d objs" % idx

    print "start fetch crowd_indexs"
    crowd_indexs = Crowd_Index.objects.all()
    print "fetched %d crowd_indexs" % len(crowd_indexs)

    for idx,crowd_index in enumerate(crowd_indexs):
        region = crowd_index.region
        #大兴修正
        if region == 8:
            crowd_index.region = 15
            crowd_index.save()
        #石景山修正
        elif region == 9:
            crowd_index.region = 8
            crowd_index.save()

        if idx % 10000 ==0:
            print "handle crowd_index of %d objs" % idx

    print "start fetch polices"
    polices = Police.objects.all()
    print "fetched %d polices" % len(polices)

    for idx,police in enumerate(polices):
        region = police.region
        #大兴修正
        if region == 8:
            police.region = 15
            police.save()
        #石景山修正
        elif region == 9:
            police.region = 8
            police.save()

        if idx % 10000 ==0:
            print "handle police of %d objs" % idx

    print "start fetch train_parameters"
    train_parameters = Train_Parameter.objects.all()
    print "fetched %d train_parameters" % len(train_parameters)

    for idx,train_parameter in enumerate(train_parameters):
        region = train_parameter.region
        #大兴修正
        if region == 8:
            train_parameter.region = 15
            train_parameter.save()
        #石景山修正
        elif region == 9:
            train_parameter.region = 8
            train_parameter.save()

        if idx % 10000 ==0:
            print "handle train_parameter of %d objs" % idx

#将数据库中所有经纬度从百度坐标转换为高德坐标
def convert_baidu_to_gaode_of_database():
    print "start fetch violations"
    violations = Violation.objects.all()
    print "fetched %d violations" % len(violations)
    for idx,violation in enumerate(violations):
        lng = float(violation.longitude)
        lat = float(violation.latitude)
        point = [lng, lat]
        lng,lat = bd2gcj(point)
        violation.longitude = lng
        violation.latitude = lat
        violation.save()

        if idx % 10000 ==0:
            print "handle violation of %d objs" % idx

    print "start fetch call_incidences"
    call_incidences = Call_Incidence.objects.all()
    print "fetched %d call_incidences" % len(call_incidences)

    for idx,call_incidence in enumerate(call_incidences):
        lng = float(call_incidence.longitude)
        lat = float(call_incidence.latitude)
        point = [lng, lat]
        lng,lat = bd2gcj(point)
        call_incidence.longitude = lng
        call_incidence.latitude = lat
        call_incidence.save()

        if idx % 10000 ==0:
            print "handle call_incidence of %d objs" % idx

    print "start fetch app_incidences"
    app_incidences = App_Incidence.objects.all()
    print "fetched %d app_incidences" % len(app_incidences)

    for idx,app_incidence in enumerate(app_incidences):
        lng = float(app_incidence.longitude)
        lat = float(app_incidence.latitude)
        point = [lng, lat]
        lng,lat = bd2gcj(point)
        app_incidence.longitude = lng
        app_incidence.latitude = lat
        app_incidence.save()

        if idx % 10000 ==0:
            print "handle app_incidence of %d objs" % idx

# 获取excel的列对应的数字编号
def get_excel_index():
    excel_index_list = [chr(i) for i in range(65,91)]
    global excel_dict
    excel_dict = {ch:i for i,ch in enumerate(excel_index_list)}
    #print(excel_dict)

def unicode_csv_reader(gbk_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(gbk_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'gbk') for cell in row]

#导入警力数据(输入文件xls的路径(不含中文),年,月,开始日期
def import_police_data(input_police_file_path , year , month, date_start_day=1):
    file = xlrd.open_workbook(input_police_file_path)
    file_sheet = file.sheets()

    #日期记录编号
    day_num = date_start_day

    for sheet in file_sheet:
        ncols = sheet.ncols
        for disstrict_name , i in district_row_no.items():
            for j in range(2, ncols):
                if sheet.cell(i,j).value != '':
                   police = Police(region = pinyin_hash[disstrict_name],group=0 , people_cnt=int(sheet.cell(i,j).value),create_time=datetime.datetime(year=year,month=month,day=day_num,hour=j-2,minute=0 ,second=0))
                   police.save()
        day_num += 1
    print("import police data to database seccessfully!")

#导入拥堵延时指数数据
#input_file_path: 输入文件xls的路径(不含中文)
def import_crowd_data(input_crowd_file_path):
    get_excel_index()
    print "in crowd data"
    # return  0
    file = xlrd.open_workbook(input_crowd_file_path)
    file_sheets = file.sheets()
    for idx in range(2,len(file_sheets)):
        print "idx = %d " % idx
        file_sheet = file.sheets()[idx]
        nrows = file_sheet.nrows
        ncols = file_sheet.ncols
        if idx == 1:
            REGION_INDEX = 'A'
            TIME_INDEX = 'C'
            CROWD_INDEX = 'D'
            AVE_SPEED_INDEX = 'E'
        else:
            REGION_INDEX = 'A'
            TIME_INDEX = 'B'
            CROWD_INDEX = 'C'
            AVE_SPEED_INDEX = 'D'
        for i in range(1, nrows):
            if i % 1000 ==0:
                    print "handled %d lines" % (i)
            region_value = file_sheet.cell(i, excel_dict[REGION_INDEX]).value
            region = region_hash2[region_value]
            create_time_str = file_sheet.cell(i, excel_dict[TIME_INDEX]).value
            avg_car_speed = file_sheet.cell(i, excel_dict[AVE_SPEED_INDEX]).value
            crowd_index = file_sheet.cell(i, excel_dict[CROWD_INDEX]).value

            create_time = datetime.datetime.strptime(create_time_str, "%Y-%m-%d %H:%M")
            if region in dadui_regions:
                region_boundaries = Region_Boundary.objects.filter(region=region)
                for idx2,region_boundary in enumerate(region_boundaries):
                    #大队编号
                    group_id = region_boundary.group
                    crowd_index_instance = Crowd_Index(region=region,group=group_id, bussiness_area=None, avg_car_speed=avg_car_speed, crowd_index=crowd_index,create_time=create_time, freespeed=-1, group_name=region_boundary.group_name, number=idx2+1)
                    crowd_index_instance.save()

            crowd_index_instance = Crowd_Index(region=region,group=0 ,bussiness_area=None, avg_car_speed=avg_car_speed, crowd_index=crowd_index,create_time=create_time, freespeed=-1, group_name="", number=-1)
            crowd_index_instance.save()
    print "import crowd data_successful"
#导入违法数据
def import_violation_data(input_violation_file):
    get_excel_index()

    file = xlrd.open_workbook(input_violation_file)
    table = file.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols

    num = 0  #用来记录在roadset中的数据点的个数，部分数据点不在该区域内，说明是别的区的
    for i in range(1,nrows):
        if i % 10000 == 0:
            print("handled %d lines" % i)
        # 当前读到的行的时间
        longitude = table.row(i)[excel_dict['O']].value
        latitude = table.row(i)[excel_dict['P']].value
        dt_line = xlrd.xldate.xldate_as_datetime(table.cell(i,excel_dict['N']).value, 0)  # datetime type
        create_time_str = dt_line.strftime("%Y-%m-%d %H:%M:%S")
        breach_type_str = table.cell(i,excel_dict['I']).value

        if latitude.strip()!="0" and longitude.strip()!="0" and latitude.strip()!="" and longitude.strip()!="" and breach_type_str!="":
            breach_type = int(breach_type_str)
            lat = float(latitude)
            lon = float(longitude)

            for j in range(len(roadset)):
                if roadset[j]["name"] in pinyin_hash.keys():
                    if (not (roadset[j]['minX'] <= lon and lon <= roadset[j]['maxX'] and roadset[j]['minY'] <=lat and lat <= roadset[j]['maxY'])):
                        continue
                    data_set = roadset[j]["data"]
                    flag = check_point(data_set,lon,lat)
                    if flag:
                        num += 1
                        region = pinyin_hash[roadset[j]["name"]]
                        create_time = datetime.datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S")
                        violation = Violation(breach_type=breach_type,region=region,longitude=lon,latitude=lat,create_time=create_time,group=0)
                        violation.save()
                        break
    print("num="+str(num)+",nrows="+str(nrows))
    print("load violation successful!")
    
#导入APP事故举报数据
def import_app_incidence_data(input_app_incidence_file):
    get_excel_index()
    LON_INDEX = 'D'
    LAT_INDEX = 'E'
    PLACE_INDEX = 'F'
    TIME_INDEX = 'H'   ##这里的时间选的是excel中的accident_time，虽然accident_time比create_time要晚
    AREA_NAME_INDEX = 'G'

    file = xlrd.open_workbook(input_app_incidence_file)
    table = file.sheets()[0]
    nrows = table.nrows
    ncols = table.ncols
    for i in range(1,nrows):
        longitude = table.cell(i, excel_dict[LON_INDEX]).value
        latitude = table.cell(i, excel_dict[LAT_INDEX]).value
        place = table.cell(i, excel_dict[PLACE_INDEX]).value
        create_time = xlrd.xldate.xldate_as_datetime(table.cell(i, excel_dict[TIME_INDEX]).value,0) ##将float类型的时间转换成datetime类型
        # create_time_str = create_time.strftime("%Y-%m-%d %H:%M:%S")
        region_text = table.cell(i, excel_dict[AREA_NAME_INDEX]).value
        if region_text in region_hash2.keys():
            region = region_hash2[region_text]
            # output_str = str(longitude) + "," + str(latitude) + "," + place + "," + create_time_str + "," + str(region)
            app_incidence = App_Incidence(longitude=longitude,latitude=latitude,place=place,create_time=create_time,region=region,group=0)
            app_incidence.save()
    print("load app incidence data successful!")

#导入122电话事故举报数据
def import_call_incidence_data(input_call_incidence_file):
    get_excel_index()
    TIME_INDEX = 'O'
    LON_INDEX = 'H'  #数据中存在经纬度都是0的情况，表示经纬度不存在
    LAT_INDEX = 'I'
    CONTENT_INDEX = 'M'
    PLACE_INDEX = 'T'

    file = xlrd.open_workbook(input_call_incidence_file)
    file_sheets = file.sheets()
    num = 0
    bdmap = BaiduMap("北京市")
    for table in file_sheets:
        nrows = table.nrows
        ncols = table.ncols
        num += 1
        print("num=" + str(num))
        for i in range(1, nrows - 1):

            create_time = xlrd.xldate.xldate_as_datetime(table.cell(i, excel_dict[TIME_INDEX]).value, 0)  ##将float类型的时间转换成datetime类型
            create_time_str = create_time.strftime("%Y-%m-%d %H:%M:%S")
            longitude = table.cell(i, excel_dict[LON_INDEX]).value  ##float类型
            latitude = table.cell(i, excel_dict[LAT_INDEX]).value
            event_content = table.cell(i, excel_dict[CONTENT_INDEX]).value
            place = table.cell(i, excel_dict[PLACE_INDEX]).value
            if(longitude == 0 or latitude == 0):
                try:
                    bd_point = bdmap.getLocation(place)
                    if bd_point is None:
                        continue
                        # print "%s---%s,%s %f" % (line, bd_point[0], bd_point[1], bd_point[2])
                    #gcj_point = convert.bd2gcj(bd_point)
                    # print "%s,%s,%s" % ("bd2gcj", gcj_point[0], gcj_point[1])
                    #gps_point = convert.gcj2gps(gcj_point)
                    # print "%s,%s,%s" % ("gcj2gps", gps_point[0], gps_point[1])
                    # 地点名称,经度,纬度,可信度
                    #rtd_gps_info = (place, bd_point[0], bd_point[1], bd_point[2])
                    longitude = bd_point[0]
                    latitude = bd_point[1]
                except Exception as e:
                    longitude, latitude, region = -1, -1, -1
                    # print(line + "---bdmap error!! info:" + str(e))
                    continue
            for j in range(len(roadset)):
                # print("roadset="+roadset[j]["name"]+", minX="+str(roadset[j]['minX'])+",maxX=" +str(roadset[j]['maxX'])+",minY="+str(roadset[j]['minY'])+',maxY='+str(roadset[j]['maxY']))
                if roadset[j]["name"] in pinyin_hash.keys():
                    if (not (roadset[j]['minX'] <= longitude and longitude <= roadset[j]['maxX'] and roadset[j][
                        'minY'] <= latitude and latitude <= roadset[j]['maxY'])):
                        continue
                    # print("YES")
                    data_set = roadset[j]["data"]
                    flag = check_point(data_set, longitude, latitude)
                    if flag:
                        # print("in")
                        num += 1
                        region = pinyin_hash[roadset[j]["name"]]
                        # output_str = str(region) + "," + create_time_str + "," + str(longitude) + "," + str(latitude) + "," + event_content + "," + place
                        call_incidence = Call_Incidence(region=region,create_time=create_time,longitude=longitude,latitude=latitude,event_content=event_content,group=0)
                        call_incidence.save()
                        break
    print("import call 122 finished!")


def get_region_boundary_list(geo_boundary):
    geo_center_x, geo_center_y = 0.0, 0.0
    rb_coord_list = []
    idx = 0
    for item in geo_boundary:
        lng = item["x"]
        lat = item["y"]
        point = [lng, lat]
        #将高德坐标转换成百度坐标
        lng,lat = gcj2bd(point)
        rb_coord_list.append([lng, lat])
        if(idx < len(geo_boundary) -1):
            geo_center_x += lng
            geo_center_y += lat
        idx += 1
    geo_center_x /= float(len(geo_boundary) - 1)
    geo_center_y /= float(len(geo_boundary) - 1)
    return rb_coord_list,geo_center_x, geo_center_y
def generate_datajs_dadui(path):
    file = open(path, "w")
    file.write("var data = ")
    region_boundary_dict = {}
    geo_center_dict = {}
    region_boundary = Region_Boundary.objects.all()

    for rb in region_boundary:
        geo_boundary = json.loads(rb.geo_boundary)
        if isinstance(geo_boundary[0], list):
            rb_coord_list = []
            geo_center_list = []
            for boundary_item in geo_boundary:
                rb_coord_list_tmp,geo_center_x, geo_center_y = get_region_boundary_list(boundary_item)
                rb_coord_list.append(rb_coord_list_tmp)
                geo_center_list.append([geo_center_x, geo_center_y])
            region_boundary_dict[str(rb.group)] = rb_coord_list
            geo_center_dict[str(rb.group)] = geo_center_list
        else:
            rb_coord_list_tmp,geo_center_x, geo_center_y = get_region_boundary_list(geo_boundary)
            region_boundary_dict[str(rb.group)] = [rb_coord_list_tmp]
            geo_center_dict[str(rb.group)] = [[geo_center_x, geo_center_y]]
    region_boundary_json = json.dumps(region_boundary_dict)
    geo_center_json = json.dumps(geo_center_dict)
    file.write(region_boundary_json + ";\n")
    file.write("var geocenter = ")
    file.write(geo_center_json + ";\n")
    file.close()

def wrt_data_to_js(out_file_path):
    out_file = open(out_file_path,"w")
    bdrs = json.loads('{"1":[[116.442707, 39.908962], [116.440535, 39.934234], [116.45024, 39.93446], [116.454134, 39.950601], [116.44497, 39.952238], [116.446594, 39.957907], [116.43663, 39.956121], [116.437014, 39.965433], [116.431655, 39.96543], [116.431673, 39.968272], [116.420495, 39.968249], [116.414144, 39.979655], [116.414482, 39.96835], [116.396364, 39.969351], [116.393613, 39.966062], [116.393758, 39.963015], [116.399881, 39.96342], [116.402897, 39.934735], [116.405809, 39.93423], [116.406024, 39.929754], [116.397306, 39.928574], [116.398119, 39.91388], [116.402086, 39.914015], [116.404366, 39.905116], [116.404872, 39.878463], [116.3877, 39.877337], [116.387944, 39.87347], [116.397662, 39.871581], [116.401907, 39.865188], [116.420505, 39.865369], [116.423156, 39.873252], [116.419873, 39.878168], [116.449648, 39.877668], [116.450797, 39.894688], [116.45749, 39.895901], [116.453665, 39.900457], [116.455132, 39.908642], [116.442707, 39.908962]],"2":[[116.40249, 39.906514], [116.402086, 39.914015], [116.398119, 39.91388], [116.397306, 39.928574], [116.406024, 39.929754], [116.405809, 39.93423], [116.402897, 39.934735], [116.399881, 39.96342], [116.393758, 39.963015], [116.393613, 39.966062], [116.400581, 39.979365], [116.387785, 39.978807], [116.389667, 39.974264], [116.376901, 39.973511], [116.378502, 39.954835], [116.362998, 39.949865], [116.362253, 39.957521], [116.358141, 39.956251], [116.357253, 39.948746], [116.334715, 39.948162], [116.339702, 39.943468], [116.342505, 39.909573], [116.341152, 39.902656], [116.332493, 39.902619], [116.327789, 39.880976], [116.349776, 39.881578], [116.350725, 39.879437], [116.356864, 39.879846], [116.358673, 39.87466], [116.404872, 39.878463], [116.40249, 39.906514]],"6":[[116.341137, 39.923964], [116.339679, 39.94356], [116.334715, 39.948162], [116.357253, 39.948746], [116.358141, 39.956251], [116.362253, 39.957521], [116.362998, 39.949865], [116.378502, 39.954835], [116.37692, 39.973552], [116.389736, 39.974387], [116.387287, 39.993956], [116.362761, 40.026109], [116.363069, 40.02954], [116.357718, 40.032531], [116.401464, 40.039194], [116.396604, 40.04379], [116.397325, 40.047524], [116.378543, 40.050829], [116.37375, 40.057042], [116.379802, 40.060106], [116.378836, 40.063911], [116.389051, 40.066847], [116.386902, 40.07159], [116.379795, 40.071643], [116.376853, 40.075298], [116.369691, 40.074844], [116.369768, 40.07191], [116.353507, 40.069364], [116.349949, 40.061113], [116.346675, 40.060861], [116.34552, 40.064731], [116.335378, 40.06064], [116.325006, 40.067249], [116.313008, 40.068525], [116.310228, 40.066449], [116.296905, 40.089609], [116.286401, 40.086145], [116.280513, 40.097876], [116.265798, 40.10745], [116.271527, 40.110243], [116.269771, 40.117429], [116.264818, 40.118596], [116.263369, 40.110845], [116.246619, 40.114369], [116.251428, 40.118582], [116.254817, 40.141222], [116.239751, 40.142021], [116.223719, 40.147867], [116.214447, 40.146781], [116.209906, 40.167109], [116.201798, 40.166439], [116.197998, 40.161694], [116.190154, 40.164269], [116.188151, 40.153554], [116.181289, 40.148843], [116.176081, 40.148902], [116.176031, 40.145915], [116.171412, 40.146314], [116.176745, 40.143174], [116.179721, 40.13387], [116.174848, 40.134699], [116.177839, 40.130436], [116.141183, 40.127954], [116.137391, 40.121312], [116.120823, 40.121343], [116.113567, 40.124048], [116.108368, 40.122302], [116.10376, 40.127436], [116.081711, 40.121954], [116.077221, 40.111653], [116.063592, 40.103311], [116.056474, 40.092332], [116.063413, 40.083336], [116.071468, 40.079457], [116.072308, 40.073843], [116.078539, 40.068341], [116.075555, 40.058363], [116.0821, 40.043526], [116.085314, 40.039136], [116.092141, 40.037016], [116.107208, 40.039888], [116.144993, 40.035981], [116.155357, 40.028917], [116.164319, 40.027556], [116.182703, 40.012638], [116.179676, 40.007247], [116.167804, 40.006381], [116.157626, 39.999989], [116.16467, 39.990209], [116.174553, 39.993657], [116.175724, 39.983666], [116.185043, 39.988499], [116.185431, 39.994544], [116.191454, 39.992044], [116.192751, 39.976711], [116.208046, 39.967038], [116.209915, 39.962145], [116.225593, 39.94995], [116.220405, 39.939699], [116.222384, 39.933733], [116.213491, 39.930676], [116.213391, 39.923814], [116.238498, 39.922], [116.259497, 39.927929], [116.259612, 39.9237], [116.25575, 39.921998], [116.259455, 39.921458], [116.25952, 39.903235], [116.301619, 39.90306], [116.302701, 39.892937], [116.305624, 39.895923], [116.313912, 39.896884], [116.310609, 39.898681], [116.319901, 39.902635], [116.341152, 39.902656], [116.341137, 39.923964]],"8":[[116.381464, 39.791614], [116.373981, 39.790829], [116.373788, 39.805579], [116.363526, 39.806492], [116.36231, 39.811396], [116.350569, 39.81346], [116.346976, 39.807642], [116.334793, 39.80701], [116.333171, 39.803811], [116.329653, 39.803931], [116.328358, 39.789516], [116.324301, 39.789189], [116.316446, 39.775618], [116.311058, 39.778993], [116.304814, 39.797705], [116.299128, 39.79707], [116.297442, 39.799567], [116.30255, 39.801777], [116.300383, 39.80406], [116.29561, 39.8028], [116.29357, 39.805137], [116.268574, 39.799022], [116.265202, 39.803607], [116.257664, 39.798946], [116.261125, 39.769293], [116.2589, 39.75605], [116.250508, 39.747446], [116.254304, 39.736976], [116.251844, 39.724818], [116.236021, 39.713468], [116.236438, 39.704961], [116.232517, 39.700565], [116.235101, 39.695099], [116.228525, 39.688562], [116.233061, 39.681297], [116.223666, 39.657541], [116.222425, 39.647618], [116.227166, 39.632502], [116.225057, 39.614221], [116.233313, 39.599622], [116.227915, 39.584526], [116.245105, 39.556047], [116.250727, 39.552413], [116.251984, 39.521643], [116.258316, 39.516687], [116.261105, 39.50889], [116.282528, 39.501232], [116.285552, 39.497833], [116.310498, 39.493163], [116.325583, 39.480138], [116.332267, 39.468477], [116.349029, 39.458592], [116.351422, 39.453985], [116.371229, 39.453886], [116.372291, 39.457582], [116.383324, 39.459122], [116.394203, 39.456088], [116.399532, 39.458963], [116.425853, 39.454582], [116.429217, 39.449554], [116.439309, 39.445717], [116.457641, 39.452528], [116.462321, 39.46309], [116.456546, 39.468347], [116.454885, 39.482176], [116.44748, 39.492161], [116.427339, 39.502878], [116.413425, 39.529626], [116.425291, 39.528906], [116.432281, 39.522346], [116.441316, 39.522359], [116.446318, 39.524486], [116.449053, 39.535027], [116.483584, 39.545471], [116.484288, 39.555351], [116.51236, 39.561538], [116.533535, 39.579411], [116.530868, 39.603113], [116.561077, 39.604456], [116.575397, 39.60992], [116.574035, 39.615511], [116.578352, 39.625892], [116.585801, 39.626099], [116.585933, 39.629159], [116.608882, 39.627922], [116.60958, 39.617675], [116.618347, 39.614326], [116.63956, 39.598435], [116.649575, 39.602253], [116.65341, 39.612935], [116.701393, 39.602494], [116.710341, 39.59463], [116.735224, 39.599557], [116.712803, 39.615639], [116.712707, 39.620278], [116.732272, 39.622677], [116.729067, 39.629092], [116.733155, 39.64067], [116.72791, 39.643192], [116.719037, 39.642614], [116.715298, 39.646085], [116.70976, 39.663174], [116.710236, 39.679719], [116.693069, 39.682482], [116.675993, 39.68148], [116.673469, 39.685993], [116.677234, 39.686566], [116.676741, 39.693578], [116.670488, 39.691879], [116.659802, 39.694028], [116.652955, 39.705726], [116.655871, 39.709855], [116.660465, 39.708853], [116.660878, 39.713958], [116.651277, 39.716906], [116.645859, 39.722983], [116.645438, 39.730645], [116.637961, 39.730287], [116.634223, 39.734718], [116.625531, 39.732035], [116.62283, 39.727838], [116.619619, 39.728867], [116.612454, 39.724849], [116.613074, 39.718513], [116.607379, 39.719882], [116.607428, 39.715263], [116.581503, 39.715533], [116.579596, 39.720216], [116.55286, 39.72121], [116.545338, 39.719243], [116.533708, 39.723595], [116.535887, 39.726998], [116.541676, 39.726222], [116.539627, 39.744757], [116.546568, 39.74421], [116.547969, 39.746464], [116.547755, 39.748454], [116.534634, 39.7487], [116.54035, 39.756615], [116.525359, 39.756949], [116.529939, 39.766364], [116.528427, 39.773925], [116.534219, 39.768421], [116.547066, 39.767162], [116.550335, 39.76952], [116.545704, 39.774366], [116.554858, 39.775712], [116.551247, 39.779949], [116.544078, 39.776178], [116.537508, 39.78367], [116.547537, 39.787008], [116.536327, 39.798533], [116.543233, 39.802877], [116.540702, 39.806449], [116.548019, 39.809831], [116.545414, 39.820736], [116.541229, 39.823766], [116.546729, 39.829532], [116.532967, 39.832723], [116.532584, 39.83575], [116.520692, 39.835145], [116.515981, 39.829544], [116.516491, 39.822714], [116.50154, 39.821867], [116.501637, 39.824196], [116.496314, 39.824938], [116.491975, 39.818782], [116.480899, 39.815293], [116.475494, 39.82014], [116.469959, 39.819999], [116.460356, 39.828481], [116.450671, 39.826127], [116.446775, 39.835831], [116.427606, 39.836076], [116.426128, 39.832878], [116.422414, 39.835591], [116.420636, 39.830117], [116.424287, 39.828389], [116.425879, 39.821073], [116.416286, 39.8225], [116.416209, 39.817351], [116.427931, 39.816515], [116.430595, 39.80969], [116.435096, 39.80971], [116.434512, 39.7985], [116.428264, 39.798983], [116.426144, 39.793452], [116.402776, 39.793023], [116.404908, 39.772039], [116.398612, 39.771406], [116.397113, 39.787789], [116.385589, 39.784822], [116.385112, 39.791699], [116.381464, 39.791614]],"7":[[116.256504, 39.901832], [116.247435, 39.900952], [116.240275, 39.897855], [116.240775, 39.895463], [116.234411, 39.89479], [116.234483, 39.889278], [116.226217, 39.887366], [116.224868, 39.882421], [116.217259, 39.884172], [116.218901, 39.880592], [116.214799, 39.880066], [116.206242, 39.889109], [116.190577, 39.886765], [116.173838, 39.895537], [116.169036, 39.893538], [116.161725, 39.895637], [116.157161, 39.890453], [116.146718, 39.890631], [116.117558, 39.878682], [116.11003, 39.879466], [116.107895, 39.873363], [116.102273, 39.874836], [116.093556, 39.871985], [116.084896, 39.876347], [116.076807, 39.874628], [116.073513, 39.872018], [116.076684, 39.859606], [116.071776, 39.860556], [116.06999, 39.857209], [116.066515, 39.85984], [116.060452, 39.852314], [116.064312, 39.848731], [116.078763, 39.844895], [116.089112, 39.833674], [116.091293, 39.838849], [116.090487, 39.832231], [116.093187, 39.836506], [116.095644, 39.835118], [116.0946, 39.82529], [116.090663, 39.825264], [116.095381, 39.823038], [116.091005, 39.818077], [116.09173, 39.801737], [116.097615, 39.788216], [116.107431, 39.78888], [116.108873, 39.792459], [116.110369, 39.78959], [116.110568, 39.792665], [116.115718, 39.792642], [116.115005, 39.795307], [116.121125, 39.795265], [116.122399, 39.797641], [116.126981, 39.796911], [116.127687, 39.791932], [116.138923, 39.790363], [116.137427, 39.788825], [116.141971, 39.78709], [116.131317, 39.783576], [116.129824, 39.786123], [116.123971, 39.780286], [116.127152, 39.779628], [116.127281, 39.776305], [116.124423, 39.777118], [116.12792, 39.768454], [116.128509, 39.772494], [116.131038, 39.768706], [116.144619, 39.774184], [116.145812, 39.770833], [116.153328, 39.77254], [116.152942, 39.776116], [116.166792, 39.77348], [116.172405, 39.780018], [116.175093, 39.791002], [116.190438, 39.790366], [116.190902, 39.786516], [116.194623, 39.788074], [116.206846, 39.783949], [116.208419, 39.805525], [116.215719, 39.812206], [116.214865, 39.817114], [116.222484, 39.822667], [116.220145, 39.829412], [116.234878, 39.831177], [116.247313, 39.821725], [116.25883, 39.799165], [116.265202, 39.803607], [116.268574, 39.799022], [116.29357, 39.805137], [116.29561, 39.8028], [116.300383, 39.80406], [116.30255, 39.801777], [116.297442, 39.799567], [116.299128, 39.79707], [116.304814, 39.797705], [116.313532, 39.776071], [116.316446, 39.775618], [116.324301, 39.789189], [116.328358, 39.789516], [116.329653, 39.803931], [116.333171, 39.803811], [116.334793, 39.80701], [116.346976, 39.807642], [116.350569, 39.81346], [116.36231, 39.811396], [116.363526, 39.806492], [116.373788, 39.805579], [116.373981, 39.790829], [116.385112, 39.791699], [116.385589, 39.784822], [116.397113, 39.787789], [116.398612, 39.771406], [116.404908, 39.772039], [116.402776, 39.793023], [116.426144, 39.793452], [116.428264, 39.798983], [116.435831, 39.800279], [116.435096, 39.80971], [116.430595, 39.80969], [116.42899, 39.815918], [116.424621, 39.81538], [116.421719, 39.818672], [116.416209, 39.817351], [116.416286, 39.8225], [116.425879, 39.821073], [116.424287, 39.828389], [116.420636, 39.830117], [116.422414, 39.835591], [116.426128, 39.832878], [116.431615, 39.838691], [116.437902, 39.83852], [116.442984, 39.847021], [116.447524, 39.845285], [116.453684, 39.847044], [116.453186, 39.854005], [116.46466, 39.856262], [116.467119, 39.854165], [116.471752, 39.856764], [116.472532, 39.861387], [116.45754, 39.868812], [116.451866, 39.868396], [116.450089, 39.878013], [116.419873, 39.878168], [116.423156, 39.873252], [116.420505, 39.865369], [116.402273, 39.865175], [116.397662, 39.871581], [116.387944, 39.87347], [116.3877, 39.877337], [116.358673, 39.87466], [116.356864, 39.879846], [116.350725, 39.879437], [116.349776, 39.881578], [116.327912, 39.880918], [116.332493, 39.902619], [116.319901, 39.902635], [116.310609, 39.898681], [116.313912, 39.896884], [116.305624, 39.895923], [116.302701, 39.892937], [116.301619, 39.90306], [116.256504, 39.901832]],"5":[[116.646319, 40.006356], [116.641899, 40.010457], [116.637789, 40.008115], [116.631801, 40.010677], [116.634344, 40.014032], [116.625897, 40.018101], [116.605573, 40.020894], [116.583423, 40.03384], [116.585263, 40.038949], [116.580879, 40.038842], [116.583812, 40.035202], [116.572502, 40.044509], [116.557532, 40.051337], [116.552346, 40.056249], [116.558534, 40.059865], [116.554677, 40.068609], [116.550099, 40.065421], [116.53681, 40.076275], [116.518432, 40.077255], [116.506144, 40.086251], [116.489979, 40.087645], [116.479918, 40.091193], [116.47609, 40.095797], [116.473365, 40.095842], [116.472852, 40.087579], [116.468351, 40.08629], [116.466889, 40.067011], [116.455298, 40.064534], [116.431355, 40.070731], [116.431517, 40.066402], [116.415819, 40.06182], [116.412625, 40.05574], [116.415001, 40.049137], [116.410542, 40.044775], [116.401717, 40.042858], [116.397325, 40.047524], [116.396604, 40.04379], [116.401464, 40.039194], [116.357718, 40.032531], [116.363069, 40.02954], [116.362761, 40.026109], [116.387287, 39.993956], [116.387785, 39.978807], [116.400581, 39.979365], [116.393903, 39.967204], [116.396364, 39.969351], [116.414482, 39.96835], [116.415299, 39.979667], [116.420495, 39.968249], [116.431673, 39.968272], [116.431655, 39.96543], [116.437014, 39.965433], [116.43663, 39.956121], [116.446594, 39.957907], [116.44497, 39.952238], [116.454134, 39.950601], [116.45024, 39.93446], [116.440535, 39.934234], [116.442707, 39.908962], [116.455132, 39.908642], [116.453665, 39.900457], [116.457497, 39.896305], [116.450797, 39.894688], [116.44943, 39.872028], [116.451866, 39.868396], [116.463979, 39.866301], [116.472854, 39.860089], [116.466214, 39.853856], [116.46466, 39.856262], [116.453186, 39.854005], [116.453684, 39.847044], [116.447524, 39.845285], [116.442984, 39.847021], [116.437902, 39.83852], [116.431615, 39.838691], [116.431617, 39.83626], [116.446775, 39.835831], [116.450671, 39.826127], [116.460356, 39.828481], [116.469959, 39.819999], [116.475494, 39.82014], [116.480899, 39.815293], [116.491975, 39.818782], [116.496314, 39.824938], [116.501637, 39.824196], [116.50154, 39.821867], [116.516491, 39.822714], [116.515981, 39.829544], [116.520718, 39.835153], [116.532584, 39.83575], [116.532967, 39.832723], [116.541175, 39.83037], [116.544843, 39.834524], [116.540075, 39.838702], [116.549021, 39.835757], [116.552721, 39.84116], [116.584308, 39.836326], [116.589616, 39.829271], [116.606644, 39.831094], [116.608073, 39.846815], [116.613401, 39.851335], [116.611039, 39.855961], [116.619228, 39.856115], [116.633199, 39.866868], [116.626724, 39.874698], [116.63635, 39.891266], [116.634324, 39.896696], [116.622549, 39.895733], [116.620905, 39.902434], [116.628445, 39.908134], [116.627765, 39.926694], [116.637114, 39.9281], [116.631738, 39.936723], [116.635922, 39.938225], [116.639874, 39.946202], [116.636731, 39.95343], [116.639218, 39.956666], [116.651643, 39.95228], [116.647209, 39.987213], [116.638861, 39.990305], [116.646185, 39.996931], [116.650368, 39.996265], [116.646319, 40.006356]],"9":[[116.25948, 39.923721], [116.259497, 39.927929], [116.238498, 39.922], [116.213391, 39.923814], [116.213491, 39.930676], [116.222384, 39.933733], [116.220405, 39.939699], [116.225593, 39.94995], [116.209915, 39.962145], [116.208046, 39.967038], [116.192751, 39.976711], [116.191454, 39.992044], [116.185431, 39.994544], [116.185043, 39.988499], [116.175724, 39.983666], [116.174553, 39.993657], [116.16467, 39.990209], [116.157626, 39.999989], [116.150944, 39.995682], [116.125963, 39.992095], [116.120457, 39.987295], [116.123488, 39.977956], [116.129973, 39.973315], [116.127774, 39.967015], [116.121463, 39.963716], [116.126675, 39.956231], [116.120227, 39.954072], [116.118878, 39.948913], [116.123569, 39.941159], [116.126733, 39.938261], [116.131339, 39.940888], [116.135277, 39.93273], [116.14728, 39.928622], [116.162003, 39.903971], [116.190577, 39.886765], [116.206242, 39.889109], [116.214799, 39.880066], [116.218901, 39.880592], [116.217259, 39.884172], [116.224868, 39.882421], [116.226217, 39.887366], [116.234483, 39.889278], [116.234411, 39.89479], [116.240775, 39.895463], [116.244157, 39.899681], [116.264751, 39.901361], [116.265713, 39.903332], [116.25952, 39.903235], [116.259455, 39.921458], [116.25575, 39.921998], [116.25948, 39.923721]]}')
    temp_dict = {}
    temp_dict["15"] = [bdrs["8"]]
    temp_dict["8"] = [bdrs["9"]]
    for k,v in bdrs.items():
        bdrs[k] = [v]
    bdrs["15"] = temp_dict["15"]
    bdrs["8"] = temp_dict["8"]
    del bdrs["9"]
    js_bdrs = 'var data=' + json.dumps(bdrs) +';\n'
    geo_centers = json.loads('{"1": [116.42096883783782, 39.92411481081083], "2": [116.37384433333334, 39.93029340000001], "5": [116.51148292622948, 39.94519316393441], "6": [116.24484343478261, 40.04065593913044], "7": [116.25623491875001, 39.83092004375], "8": [116.4712738082901, 39.696117253886], "9": [116.19095746000002, 39.938460639999995]}')
    temp_dict = {}
    temp_dict["15"] = [geo_centers["8"]]
    temp_dict["8"] = [geo_centers["9"]]
    for k,v in geo_centers.items():
        geo_centers[k] = [v]
    geo_centers["15"] = temp_dict["15"]
    geo_centers["8"] = temp_dict["8"]
    del geo_centers["9"]
    js_geo_centers = 'var geocenter = ' + json.dumps(geo_centers) +';'
    out_file.write(js_bdrs)
    out_file.write(js_geo_centers)
    out_file.close()
if __name__ == "__main__":

    input_call_incidence_file = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2017/shuju/122_17-01.xls"

    import_call_incidence_data(input_call_incidence_file=input_call_incidence_file)

    input_app_incidence_file = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2017/shuju/app_incidence_2017_1_2.xls"

    import_app_incidence_data(input_app_incidence_file=input_app_incidence_file)

    input_violation_file = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2017/shuju/violation_2017_1_2.xlsx"

    import_violation_data(input_violation_file=input_violation_file)

    input_crowd_file_path = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2017/shuju/crowd_2017_1_2.xlsx"

    import_crowd_data(input_crowd_file_path=input_crowd_file_path)

    input_police_file_path = "/Users/Ren/PycharmProjects/PoliceIndex/beijing_data/2017/police/201702.xls"

    import_police_data(input_police_file_path=input_police_file_path,year=2017,month=2,date_start_day=1)
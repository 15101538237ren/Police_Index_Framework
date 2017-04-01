# -*- coding: utf-8 -*-
import xlrd,os,datetime,pytz,pickle,csv,calendar
from process.models import *
from process.helpers import pinyin_hash,check_point,region_hash2
from process.baidumap import BaiduMap

district_row_no = {"dongcheng":3, "xicheng":4, "chaoyang":5, "haidian":6,"fengtai":7,"shijingshan":8,"daxing":19}
sheet_idx = {2:"dongcheng",3:"xicheng",4:"haidian",5:"chaoyang",6:"daxing",7:"shijingshan",8:"fengtai"}
dadui_hash = {u"中关村(西苑)队":u"海淀",u"樱桃园大队":u"西城",u"亚运村队":u"朝阳",u"西外队":u"西城",u"西四队":u"西城",u"西单队":u"西城",u"温泉队":u"海淀",u"天坛大队":u"东城",u"双桥队":u"朝阳",u"清河队":u"海淀",u"前门大队":u"东城",u"劲松(东三环)队":u"朝阳",u"机场队":u"朝阳",u"黄庄(西三环)队":u"海淀",u"呼家楼队":u"朝阳",u"和平里队":u"东城",u"广安门大队":u"西城",u"公主坟队":u"海淀",u"府右街队":u"西城",u"东外队":u"朝阳",u"东四队":u"东城",u"东单队":u"东城",u"大红门队":u"丰台",u"方庄队":u"丰台",u"丰北队":u"丰台",u"卢沟桥队":u"丰台",u"西站队":u"丰台",}
excel_dict = {}
MAXINT = 999999999
LNG_INDEX = 0
LAT_INDEX = 1
EPS = 0.000001

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
def import_police_data(input_file_path , year , month, date_start_day=1):
    file = xlrd.open_workbook(input_file_path)
    file_sheet = file.sheets()

    #日期记录编号
    day_num = date_start_day

    for sheet in file_sheet:
        ncols = sheet.ncols
        for disstrict_name , i in district_row_no.items():
            for j in range(2, ncols):
                if sheet.cell(i,j).value != '':
                    pass
 #                   police = Police(region = pinyin_hash[disstrict_name],people_cnt=int(sheet.cell(i,j).value),create_time=datetime.datetime(year=year,month=month,day=day_num,hour=j-2,minute=0 ,second=0))
  #                  police.save()
        day_num += 1
    # print("import police data to database seccessfully!")

#导入拥堵延时指数数据
#input_file_path: 输入文件xls的路径(不含中文)
def import_crowd_data(input_file_path):
    get_excel_index()

    file = xlrd.open_workbook(input_file_path)
    file_sheets = file.sheets()
    for idx in range(1,len(file_sheets)):

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
            region_value = file_sheet.cell(i, excel_dict[REGION_INDEX]).value
            region = region_hash2[region_value]
            create_time_str = file_sheet.cell(i, excel_dict[TIME_INDEX]).value
            avg_car_speed = file_sheet.cell(i, excel_dict[AVE_SPEED_INDEX]).value
            crowd_index = file_sheet.cell(i, excel_dict[CROWD_INDEX]).value
            if idx == 1:
                BUSINESS_AREA_INDEX = 'B'
                business_area = file_sheet.cell(i, excel_dict[BUSINESS_AREA_INDEX]).value
                create_time = datetime.datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S")
                crowd_index = Crowd_Index(region=region,bussiness_area=business_area,avg_car_speed=avg_car_speed,crowd_index=crowd_index,create_time=create_time)
                crowd_index.save()
            else:
                create_time = datetime.datetime.strptime(create_time_str, "%Y-%m-%d %H:%M")
                crowd_index = Crowd_Index(region=region,bussiness_area=None,avg_car_speed=avg_car_speed,crowd_index=crowd_index,create_time=create_time)
                crowd_index.save()
    #print "import crowd data_successful"
#导入违法数据
def import_violation_data(input_violation_file,path_pkl_path):
    get_excel_index()
    path_pkl_file = open(path_pkl_path,"rb")
    roadset = pickle.load(path_pkl_file)

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
                        violation = Violation(breach_type=breach_type,region=region,longitude=lon,latitude=lat,create_time=create_time)
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
            app_incidence = App_Incidence(longitude=longitude,latitude=latitude,place=place,create_time=create_time,region=region)
            app_incidence.save()
    print("load app incidence data successful!")

#导入122电话事故举报数据
def import_call_incidence_data(input_call_incidence_file,path_pkl_path):
    get_excel_index()
    TIME_INDEX = 'O'
    LON_INDEX = 'H'  #数据中存在经纬度都是0的情况，表示经纬度不存在
    LAT_INDEX = 'I'
    CONTENT_INDEX = 'M'
    PLACE_INDEX = 'T'

    path_pkl_file = open(path_pkl_path, "rb")
    roadset = pickle.load(path_pkl_file)

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
                        call_incidence = Call_Incidence(region=region,create_time=create_time,longitude=longitude,latitude=latitude,event_content=event_content)
                        call_incidence.save()
                        break
    print("import call 122 finished!")

def preprocess_whole_122(input_dir,month_list):
    for month in month_list:
        input_file_path = input_dir + os.sep + str(month) + ".csv"

        reader = unicode_csv_reader(open(input_file_path))
        for i,row in enumerate(reader):
            dadui_name = row[1]
            if dadui_name in dadui_hash.keys():
                district_no = str(region_hash[dadui_hash[dadui_name]])
                date_time = datetime.datetime.strptime(row[0],"%Y/%m/%d %H:%M:%S")
                date_time_str = date_time.strftime("%Y-%m-%d %H:%M:%S")
        duration_minute = 10
        tz=pytz.timezone('Asia/Shanghai')
        year = 2016
        from_date = datetime.datetime(year,month,1,0,0,0,0,tzinfo=tz)
        firstDayWeekDay, monthRange = calendar.monthrange(year, month)
        to_date = datetime.datetime(year,month,monthRange,23,59,59,0,tzinfo=tz)
        preprocess_inmediate_file_to_standard(out_file_path,out_dir,from_date,to_date,duration_minute)
        print "%d month write successfully!" % month
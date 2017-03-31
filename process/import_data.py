# -*- coding: utf-8 -*-

import xlrd,os,datetime,pytz,pickle,math
import convert
from baidumap import BaiduMap
#from models import Police
#from helpers import pinyin_hash

region_hash = {u"东城区" : 1, u"西城区": 2, u"朝阳区": 5, u"海淀区": 6,u"丰台区":7,u"大兴区":8,u"石景山区":9}
pinyin_hash = {"dongcheng" : 1, "xicheng" : 2, "chaoyang":5, "haidian":6,"fengtai":7,"daxing":8,"shijingshan":9}

district_row_no = {"dongcheng":3, "xicheng":4, "chaoyang":5, "haidian":6,"fengtai":7,"shijingshan":8,"daxing":19}

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

#导入警力数据(输入文件xls的路径(不含中文),输出文件的文件夹,
def import_police_data(input_file_path , year , month, date_start_day=1):
    tz=pytz.timezone('Asia/Shanghai')
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
    print("import police data to database seccessfully!")
    
#导入拥堵延时指数数据
#input_file_path: 输入文件xls的路径(不含中文)
def import_crowd_data(input_file_path):
    REGION_INDEX = 'A'
    BUSINESS_AREA_INDEX = 'B'
    TIME_INDEX = 'C'
    CROWD_INDEX = 'D'
    AVE_SPEED_INDEX = 'E'

    file = xlrd.open_workbook(input_file_path)
    file_sheet = file.sheets()[1]
    nrows = file_sheet.nrows
    ncols = file_sheet.ncols
    for i in range(1, nrows):
        region_value = file_sheet.cell(i, excel_dict[REGION_INDEX]).value
        region = region_hash[region_value]
        business_area = file_sheet.cell(i, excel_dict[BUSINESS_AREA_INDEX]).value
        avg_car_speed = file_sheet.cell(i, excel_dict[AVE_SPEED_INDEX]).value
        crowd_index = file_sheet.cell(i, excel_dict[CROWD_INDEX]).value
        create_time_str = file_sheet.cell(i, excel_dict[TIME_INDEX]).value
        create_time = datetime.datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S")

        output_str = str(region) + "," + business_area + "," + str(avg_car_speed) + "," + str(crowd_index) + "," + create_time_str
        print(output_str)


# 检查一个点是否在道路的多边形区域内
# 如果在多边形内，返回值为1
# 如果在多边形外，而且离多边形很远，返回值为0

def check_point(dataset, lng, lat):
    flag, minDis, x0, y0, count, length, j = 0, MAXINT, MAXINT, lat, 0, len(dataset), len(dataset) - 1
    for i in range(0, length):
        # 数据点正好和多边形路段边界点重合
        if (math.fabs(dataset[i][LNG_INDEX] - lng) < EPS and math.fabs(dataset[i][LAT_INDEX] - lat) < EPS):
            flag = 1
            break
        # 下面计算射线与线段的交点个数，判断点是否在多边形内
        # 经度相同时，相当于线段竖直
        if (math.fabs(dataset[i][LNG_INDEX] - dataset[j][LNG_INDEX]) < EPS):
            minY = min(dataset[i][LAT_INDEX], dataset[j][LAT_INDEX])
            maxY = max(dataset[i][LAT_INDEX], dataset[j][LAT_INDEX])
            if (minY <= lat and lat <= maxY):
                dis = math.fabs(lng - dataset[i][LNG_INDEX])
                minDis = min(minDis, dis)
                if (dataset[i][LNG_INDEX] >= lng):  # 保证射线是向右的，所以这里求交点的时候，交点不能在数据点左侧
                    count += 1
        else:
            # 线段平行
            if (math.fabs(dataset[i][LAT_INDEX] - dataset[j][LAT_INDEX]) < EPS):
                minX = min(dataset[i][LNG_INDEX], dataset[j][LNG_INDEX])
                maxX = max(dataset[i][LNG_INDEX], dataset[j][LNG_INDEX])
                if (minX <= lng and lng <= maxX):
                    dis = math.fabs(lat - dataset[i][LAT_INDEX])
                    minDis = min(minDis, dis)
                    continue
            else:
                kij = (dataset[j][LAT_INDEX] - dataset[i][LAT_INDEX]) / (
                dataset[j][LNG_INDEX] - dataset[i][LNG_INDEX])
                # yij = k(x - xi) + yi与y = lat相交求点引出的射线与多边形边的交点
                # k不会为0

                # 求点到直线的距离
                # yij= kij*(x-dataset[i][0])+dataset[i][1]
                # ypj=-1/kij*(x-lng)+lat
                x0 = (kij * dataset[i][LNG_INDEX] - dataset[i][LAT_INDEX] + lng / kij + lat) / (kij + 1 / kij)
                y0 = -1 / kij * (x0 - lng) + lat
                xPos = (lat - dataset[i][LAT_INDEX]) / kij + dataset[i][LNG_INDEX]
                minX = min(dataset[i][LNG_INDEX], dataset[j][LNG_INDEX])
                maxX = max(dataset[i][LNG_INDEX], dataset[j][LNG_INDEX])
                minY = min(dataset[i][LAT_INDEX], dataset[j][LAT_INDEX])
                maxY = max(dataset[i][LAT_INDEX], dataset[j][LAT_INDEX])
                if (minX <= x0 and x0 <= maxX and minY <= y0 and y0 <= maxY):
                    # 向量a = (lng-xj, lat-yj)
                    # 向量b = (xi-xj, yi-yj)
                    cross = (lng - dataset[j][LNG_INDEX]) * (dataset[i][LAT_INDEX] - dataset[j][LAT_INDEX]) - (dataset[i][LNG_INDEX] -
                        dataset[j][LNG_INDEX]) * (lat - dataset[j][LAT_INDEX])
                    dis = math.fabs(cross / math.sqrt(
                        math.pow(dataset[i][LNG_INDEX] - dataset[j][LNG_INDEX], 2) + math.pow(
                            dataset[i][LAT_INDEX] - dataset[j][LAT_INDEX], 2)))
                    minDis = min(minDis, dis)

                if (max(minX, lng) <= xPos and xPos <= maxX and minY <= lat and lat <= maxY):
                    count += 1
        j = i

    if (count % 2 == 1):
        flag = 1

    return flag


#导入违法数据
def import_violation_data(input_violation_file,path_pkl_path):
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
            #print("lon="+str(lon)+",lat="+str(lat))

            for j in range(len(roadset)):
                #print("roadset="+roadset[j]["name"]+", minX="+str(roadset[j]['minX'])+",maxX=" +str(roadset[j]['maxX'])+",minY="+str(roadset[j]['minY'])+',maxY='+str(roadset[j]['maxY']))
                if roadset[j]["name"] in pinyin_hash.keys():
                    if (not (roadset[j]['minX'] <= lon and lon <= roadset[j]['maxX'] and roadset[j]['minY'] <=lat and lat <= roadset[j]['maxY'])):
                        continue
                    #print("YES")
                    data_set = roadset[j]["data"]
                    flag = check_point(data_set,lon,lat)
                    if flag:
                        #print("in")
                        num += 1
                        region = pinyin_hash[roadset[j]["name"]]
                        output_str = str(breach_type) + "," + str(region) + "," + str(lon) + "," + str(lat) + "," + create_time_str
                        print(output_str)
                        #violation = Violation(breach_type=breach_type,region=district,longitude=lon,latitude=lat,create_time=create_time)
                        #violation.save()
                        break
    print("num="+str(num)+",nrows="+str(nrows))
    #csvfile.close()
    print("load successful!")

#导入122电话事故举报数据
def import_call_incidence_data(input_call_incidence_file, path_pkl_path):
    TIME_INDEX = 'O'
    LON_INDEX = 'H'  #数据中存在经纬度都是0的情况，表示经纬度不存在
    LAT_INDEX = 'I'
    CONTENT_INDEX = 'M'
    PLACE_INDEX = 'T'

    path_pkl_file = open(path_pkl_path, "rb")
    roadset = pickle.load(path_pkl_file)

    file = xlrd.open_workbook(input_call_incidence_file)
    file_sheets = file.sheets()
    bdmap = BaiduMap("北京市")
    for table in file_sheets:
        nrows = table.nrows
        ncols = table.ncols
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
                        region = pinyin_hash[roadset[j]["name"]]
                        output_str = str(region) + "," + create_time_str + "," + str(longitude) + "," + str(latitude) + "," + event_content + "," + place
                        print(output_str)
                        break




#导入APP事故举报数据
def import_app_incidence_data(input_app_incidence_file):
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
        create_time_str = create_time.strftime("%Y-%m-%d %H:%M:%S")
        region_text = table.cell(i, excel_dict[AREA_NAME_INDEX]).value
        region = region_hash[region_text]
        output_str = str(longitude) + "," + str(latitude) + "," + place + "," + create_time_str + "," + str(region)
        print(output_str)


if __name__ == '__main__':
    crowd_file_path = '../shuju/crowd_index.xlsx'
    input_violation_file = '../shuju/violation.xlsx'
    input_call_incidence_file1 = '../shuju/call_incidence1.xls'
    input_call_incidence_file2 = '../shuju/call_incidence2.xls'
    input_app_incidence_file = '../shuju/app_incidence.xls'
    path_pkl_path = '../shuju/boundary.pkl'
    #import_crowd_data(crowd_file_path)
    get_excel_index()
    #import_violation_data(input_violation_file, path_pkl_path)
    #import_app_incidence_data(input_app_incidence_file)
    import_call_incidence_data(input_call_incidence_file1, path_pkl_path)

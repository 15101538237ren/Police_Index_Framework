# -*- coding: utf-8 -*-

import xlrd,os,datetime,pytz,pickle,csv
from models import *
from helpers import pinyin_hash,check_point,region_hash2

district_row_no = {"dongcheng":3, "xicheng":4, "chaoyang":5, "haidian":6,"fengtai":7,"shijingshan":8,"daxing":19}
sheet_idx = {2:"dongcheng",3:"xicheng",4:"haidian",5:"chaoyang",6:"daxing",7:"shijingshan",8:"fengtai"}
excel_dict = {}
MAXINT = 999999999
LNG_INDEX = 0
LAT_INDEX = 1
EPS = 0.000001

def get_excel_index():
    excel_index_list = [chr(i) for i in range(65,91)]
    global excel_dict
    excel_dict = {ch:i for i,ch in enumerate(excel_index_list)}
    #print(excel_dict)

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
                    police = Police(region = pinyin_hash[disstrict_name],people_cnt=int(sheet.cell(i,j).value),create_time=datetime.datetime(year=year,month=month,day=day_num,hour=j-2,minute=0 ,second=0))
                    police.save()
        day_num += 1
    print "import police data to database seccessfully!"

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
    print "import crowd data_successful"
    
    

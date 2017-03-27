# -*- coding: utf-8 -*-

import xlrd,os,datetime,pytz
from models import Police
from helpers import pinyin_hash

district_row_no = {"dongcheng":3, "xicheng":4, "chaoyang":5, "haidian":6,"fengtai":7,"shijingshan":8,"daxing":19}

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
#导入122事故数据,输入xls路径
def import_122_incidence_data(input_file_path):
    pass
    
    
    
    
    

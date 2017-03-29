#coding: utf-8

from models import *
from helpers import pinyin_hash
import datetime

# 输入分钟,按几分钟切割,按duration取整
def partition_time(minute, duration=10):
    half_duration = duration / 2
    quotient = minute / duration
    residue = minute % duration
    if residue >= half_duration:
        partition_minute = duration * ( quotient + 1 )
    else:
        partition_minute = duration * quotient
    return partition_minute

def format_time(idt, format):
    incidence_minute = partition_time(idt.minute,10)
    if idt.hour ==23 and incidence_minute == 60:
        incidence_minute = 50
        incidence_dt = datetime.datetime(idt.year,idt.month,idt.day,idt.hour,incidence_minute,0,0)
    elif incidence_minute == 60:
        incidence_dt = datetime.datetime(idt.year,idt.month,idt.day,idt.hour + 1,0,0,0)
    else:
        incidence_dt = datetime.datetime(idt.year,idt.month,idt.day,idt.hour,incidence_minute,0,0)
    ct_time_str = incidence_dt.strftime(format)
    return ct_time_str


#给定起始时间,终止时间,间隔,生成time
def generate_str_arr_from_date_to_date(from_date,to_date,duration_minute):

    dt_now = from_date

    result_arr = []
    time_delta=datetime.timedelta(minutes=duration_minute)
    while (dt_now < to_date):
        dt_str = dt_now.strftime("%Y-%m-%d %H:%M:%S")
        result_arr.append(dt_str)
        dt_now = dt_now + time_delta
    return result_arr


def generate_str_arr_from_time_to_time(from_time,to_time,duration_minute,second=1):

    t_now = from_time

    result_arr = []
    time_delta=datetime.timedelta(minutes=duration_minute)
    while (t_now < to_time):
        if second:
            dt_str = t_now.strftime("%H:%M:%S")
        else:
            dt_str = t_now.strftime("%H:%M")
        result_arr.append(dt_str)
        t_now = t_now + time_delta
    return result_arr

# 处理app举报数据
#
#region:0——综合区,1~7:区县编号
#is_week:0——不按周聚合,1——按周聚合
def preprocess_app_incidence(start_time, end_time, duration, region, is_week):
    app_incidence = App_Incidence.objects.filter(create_time__range=[start_time, end_time])
    if region != 0:
        app_incidence = app_incidence.filter(region=region)
    #print type(app_incidence)

    datetime_list = generate_str_arr_from_date_to_date(start_time, end_time, duration)
    if region!=0:
        result_dict = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)
    else:
        result_dict = {}
        #每个区域一个dict
        for item in pinyin_hash.values():
            result_dict[item] = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)
    #循环遍历
    for item in app_incidence:
        idt = item.create_time
        ct_time_str = format_time(idt, "%Y-%m-%d %H:%M:%S")
        if region != 0:
            result_dict[ct_time_str] += 1
        else:
            result_dict[item.region][ct_time_str] += 1

    #key 1 weekday
    #for weekday in range(7):
        #key2 time
       #for time_i in time_list:

    return result_dict


#处理违章数据
def preprocess_vialation(start_time, end_time, duration, region, is_week):
    vialation = Violation.objects.filter(create_time__range = [start_time, end_time])
    if region != 0:
        vialation = vialation.filter(region=region)

    datetime_list = generate_str_arr_from_date_to_date(start_time, end_time, duration)

    if region!=0:
        result_dict = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)
    else:
        result_dict = {}
        #每个区域一个dict
        for item in pinyin_hash.values():
            result_dict[item] = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)

    #循环遍历
    for item in vialation:
        idt = item.create_time
        ct_time_str = format_time(idt, "%Y-%m-%d %H:%M:%S")
        if region != 0:
            result_dict[ct_time_str] += 1
        else:
            result_dict[item.region][ct_time_str] += 1

    return result_dict

#处理122报警数据
def preprocess_call_incidence(start_time, end_time, duration, region, is_week):
    call_incidences = Call_Incidence.objects.filter(create_time__range = [start_time, end_time])
    if region != 0:
        call_incidences = call_incidences.filter(region=region)

    datetime_list = generate_str_arr_from_date_to_date(start_time, end_time, duration)
    if region!=0:
        result_dict = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)
    else:
        result_dict = {}
        #每个区域一个dict
        for item in pinyin_hash.values():
            result_dict[item] = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)

    #循环遍历
    for item in call_incidences:
        idt = item.create_time
        ct_time_str = format_time(idt, "%Y-%m-%d %H:%M:%S")
        if region != 0:
            result_dict[ct_time_str] += 1
        else:
            result_dict[item.region][ct_time_str] += 1

    return result_dict


#处理拥堵指数数据
def preprocess_crowd_index(start_time, end_time, duration, region, is_week):
    crowd_index = Crowd_Index.objects.filter(create_time__range = [start_time, end_time]).filter(bussiness_area=None)
    if region != 0:
        crowd_index = crowd_index.filter(region=region)

    datetime_list = generate_str_arr_from_date_to_date(start_time, end_time, duration)
    if region!=0:
        result_dict = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)
    else:
        result_dict = {}
        #每个区域一个dict
        for item in pinyin_hash.values():
            result_dict[item] = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)

    #循环遍历
    for item in crowd_index:
        idt = item.create_time
        ct_time_str = format_time(idt, "%Y-%m-%d %H:%M:%S")
        if region != 0:
            result_dict[ct_time_str] = item.crowd_index
        else:
            result_dict[item.region][ct_time_str] = item.crowd_index
    return result_dict


#处理警力数据
def preprocess_police(start_time, end_time, duration, region, is_week):
    polices = Police.objects.filter(create_time__range = [start_time, end_time])
    if region != 0:
        polices = polices.filter(region=region).order_by("create_time")

    datetime_list = generate_str_arr_from_date_to_date(start_time, end_time, duration)
    if region!=0:
        result_dict = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)
    else:
        result_dict = {}
        #每个区域一个dict
        for item in pinyin_hash.values():
            result_dict[item] = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)
    last_dt = None
    last_val = None
    partitions = (60 / duration)

    #循环遍历
    for idx,item in enumerate(polices):
        if idx == 0:
            last_dt = item.create_time
            last_val = item.people_cnt
        else:
            now_dt = item.create_time
            now_val = item.people_cnt
            part_val = (now_val-last_val)/partitions
            for j in range(1 , partitions):
                time_delta=datetime.timedelta(minutes=j*duration)
                dt = last_dt + time_delta
                val = last_val + j * part_val
                ct_time_str = format_time(dt, "%Y-%m-%d %H:%M:%S")
                if region != 0:
                    result_dict[ct_time_str] =  val
                else:
                    result_dict[item.region][ct_time_str] =  val
            last_dt = now_dt
            last_val = now_val
    return result_dict

#训练函数
#start_time: 起始时间
#end_time: 结束时间
#duration: 时间间隔
def train(start_time, end_time, region, is_week, duration=10):
    app_incidence_result = preprocess_app_incidence(start_time, end_time, duration, region, is_week)
    # crowd_index = preprocess_crowd_index(start_time,end_time,duration,region,is_week)
    print "123"
    return

if __name__ == "__main__":
    train()
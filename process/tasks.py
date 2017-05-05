# -*- coding: utf-8 -*-

from celery import task
import datetime
import json
from djcelery import models as celery_models
from django.utils import timezone
from celery.utils.log import get_task_logger
from crontab_jobs import get_app_incidence,get_call_incidence,get_violation,get_crowd_index,save_prediction_info

#这个文件用来后台执行保存实时指挥指数的任务

gaode_index_url_str = "https://tp-restapi.amap.com/gate?sid=30010&reqData={%22city%22:%22110000%22,%22dateType%22:0,%22userdefined%22:%22true%22}&serviceKey=2F77255FF77D948DF3FED20E0C19B14F"

@task()
def scheduled_jobs():
    logger = get_task_logger(__name__)

    # file_path = "/Users/Ren/PycharmProjects/Police_Index_Framework/data/test.txt"
    # output_file = open(file_path, "a")
    # print "writing file!"
    # output_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")+"\n")
    # output_file.close()
    ##
    # python mysql 122
    return
@task()
def get_peroidic_data():
    dt = datetime.datetime.now()
    now_minute = int(dt.minute / 10) * 10
    dt_end = datetime.datetime(dt.year,dt.month,dt.day,dt.hour,now_minute,0,0)
    dt_start = dt_end - datetime.timedelta(minutes=10)
    # output_file = open("/Users/Ren/PycharmProjects/Police_Index_Framework/data/tasks.txt", "a")
    # output_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + "\n")
    # output_file.close()
    get_app_incidence(dt_start, dt_end)
    get_call_incidence(dt_start, dt_end)
    get_violation(dt_start, dt_end)
    get_crowd_index()
    save_prediction_info()
    return

def create_task(name, task, task_args, crontab_time):
    '''
    创建任务
    name       # 任务名字
    task       # 执行的任务 "myapp.tasks.add"
    task_args  # 任务参数  {"x":1, "Y":1}
    crontab_time # 定时任务时间 格式：
	    {
	      'month_of_year': 9  # 月份
	      'day_of_month': 5   # 日期
	      'hour': 01         # 小时
	      'minute':05  # 分钟
	    }

    '''
    # task任务， created是否定时创建
    task, created = celery_models.PeriodicTask.objects.get_or_create(
        name=name,
        task=task)
   # 获取 crontab
    crontab = celery_models.CrontabSchedule.objects.filter(
        **crontab_time).first()
    if crontab is None: # 如果没有就创建，有的话就继续复用之前的crontab
        crontab = celery_models.CrontabSchedule.objects.create(
            **crontab_time)
    task.crontab = crontab # 设置crontab
    task.enabled = True # 开启task
    task.kwargs = json.dumps(task_args) # 传入task参数
    expiration = timezone.now() + datetime.timedelta(day=1)
    task.expires = expiration # 设置任务过期时间为现在时间的一天以后
    task.save()
    return True

def disable_task(name):
    '''
    关闭任务
    '''
    try:
        task = celery_models.PeriodicTask.objects.get(name=name)
        task.enabled = False # 设置关闭
        task.save()
        return True
    except celery_models.PeriodicTask.DoesNotExist:
        return True
if __name__ == "__main__":
    sid = 30010
    #reqData = {"city":"110000", "dataType":"0", "userdefined":"true"}
    #gaode_index = Gaode_Traffic_Index(sid, **reqData)
    #result = gaode_index.sendAndRec()

    scheduled_jobs()
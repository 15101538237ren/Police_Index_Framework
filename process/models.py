# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from django_permanent.models import PermanentModel
from .helpers import region_hash
# Create your models here.

#App违法举报对应的数据库表
class Violation(PermanentModel):
    breach_type = models.IntegerField('违法类型',default=-1)
    region = models.SmallIntegerField('区县编号',default=0)
    longitude = models.DecimalField('经度',max_digits=10,decimal_places=7)
    latitude = models.DecimalField('纬度',max_digits=10,decimal_places=7)
    create_time = models.DateTimeField('举报时间')
    def __unicode__(self):
        return u'区县:' + region_hash[self.region]+ u', 经度:'+str(self.longitude) + u', 纬度:' + str(self.latitude) + u', 举报时间:' + str(self.create_time) +u'\n'

#122电话事故举报对应的数据库表
class Call_Incidence(PermanentModel):
    region = models.SmallIntegerField('区县编号',default=0)
    create_time = models.DateTimeField('122报警时间')
    longitude = models.DecimalField('经度',max_digits=10,decimal_places=7)
    latitude = models.DecimalField('纬度',max_digits=10,decimal_places=7)
    event_content = models.TextField('事件描述')
    place = models.TextField('地点')
    def __unicode__(self):
        return  u'区县:' + region_hash[self.region]+ u', 地点:' + str(self.place) +u', 举报时间:' + str(self.create_time) +u', 内容:'+ self.event_content +u'\n'

#App事故举报对应的数据库表
class App_Incidence(PermanentModel):
    longitude = models.DecimalField('经度',max_digits=10,decimal_places=7)
    latitude = models.DecimalField('纬度',max_digits=10,decimal_places=7)
    place = models.TextField('地点')
    create_time = models.DateTimeField('举报时间')
    region = models.SmallIntegerField('区县编号',default=0)
    def __unicode__(self):
        return u'区县:' + region_hash[self.region]+ u', 经度:'+str(self.longitude) + u', 纬度:' + str(self.latitude) + u', 举报时间:' + str(self.create_time) +u'\n'

#拥堵指数对应的数据库表
class Crowd_Index(PermanentModel):
    region = models.SmallIntegerField('区县编号',default=0)
    bussiness_area = models.TextField('商圈名称',default=None,null=True)
    avg_car_speed = models.DecimalField('平均车速',max_digits=5,decimal_places=2)
    crowd_index = models.DecimalField('拥堵延时指数',max_digits=5,decimal_places=2)
    create_time = models.DateTimeField('时间')
    def __unicode__(self):
        return  u'区县:' + region_hash[self.region]+u', 商圈:' + str(self.bussiness_area)+ u', 拥堵指数:'+str(self.crowd_index) + u', 平均车速:' + str(self.avg_car_speed) + u', 时间:' + str(self.create_time) +u'\n'

class Police(PermanentModel):
    region = models.SmallIntegerField('区县编号',default=0)
    people_cnt = models.IntegerField('人数')
    create_time = models.DateTimeField('时间')
    def __unicode__(self):
        return  u'区县:' + region_hash[self.region]+ u', 在线人数:' + str(self.people_cnt)+ u', 时间:' + str(self.create_time) + u'\n'

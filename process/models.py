# -*- coding: utf-8 -*-

from django.db import models
from django.utils import timezone
from django_permanent.models import PermanentModel
from process.helpers import region_hash
# Create your models here.


#App违法举报对应的数据库表
class Violation(PermanentModel):
    breach_type = models.IntegerField('违法类型',default=-1)
    region = models.SmallIntegerField('区县编号',default=-1)
    group = models.IntegerField('大队编号', default=-1)
    longitude = models.DecimalField('经度',max_digits=10,decimal_places=7)
    latitude = models.DecimalField('纬度',max_digits=10,decimal_places=7)
    create_time = models.DateTimeField('举报时间')
    def __unicode__(self):
        return u'区县:' + region_hash[self.region]+ u', 经度:'+str(self.longitude) + u', 纬度:' + str(self.latitude) + u', 举报时间:' + str(self.create_time) +u'\n'

#122电话事故举报对应的数据库表
class Call_Incidence(PermanentModel):
    region = models.SmallIntegerField('区县编号',default=-1)
    group = models.IntegerField('大队编号', default=-1)
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
    region = models.SmallIntegerField('区县编号',default=-1)
    group = models.IntegerField('大队编号', default=-1)
    def __unicode__(self):
        return u'区县:' + region_hash[self.region]+ u', 经度:'+str(self.longitude) + u', 纬度:' + str(self.latitude) + u', 举报时间:' + str(self.create_time) +u'\n'

#拥堵指数对应的数据库表
class Crowd_Index(PermanentModel):
    region = models.SmallIntegerField('区县编号',default=-1)
    group = models.IntegerField('大队编号', default=-1) ##高德系统里大队的ID编号
    group_name = models.TextField('大队名称', default=None)  ##高德系统中大队名称
    number = models.IntegerField('拥堵排名', default=None)  ##当前批次的拥堵排名
    bussiness_area = models.TextField('商圈名称',default=None,null=True)
    avg_car_speed = models.DecimalField('平均车速',max_digits=5,decimal_places=2,default=None)   ##实际的平均速度
    freespeed = models.DecimalField('自由流速度', max_digits=5,decimal_places=2,default=None)  ##自由流速度
    crowd_index = models.DecimalField('拥堵延时指数',max_digits=5,decimal_places=2)
    create_time = models.DateTimeField('时间')
    def __unicode__(self):
        return  u'区县:' + region_hash[self.region]+u', 商圈:' + str(self.bussiness_area)+ u', 拥堵指数:'+str(self.crowd_index) + u', 平均车速:' + str(self.avg_car_speed) + u', 时间:' + str(self.create_time) +u'\n'

class Police(PermanentModel):
    region = models.SmallIntegerField('区县编号',default=-1)
    group = models.IntegerField('大队编号', default=-1)
    people_cnt = models.IntegerField('人数')
    create_time = models.DateTimeField('时间')
    def __unicode__(self):
        return  u'区县:' + region_hash[self.region]+ u', 在线人数:' + str(self.people_cnt)+ u', 时间:' + str(self.create_time) + u'\n'

class Train_Parameter(PermanentModel):
    xmin = models.DecimalField('最小延迟指数', max_digits=10, decimal_places=4, default=None)
    xmax = models.DecimalField('最大延迟指数', max_digits=10, decimal_places=4, default=None)
    ymin = models.IntegerField('最小APP举报数', default=None)
    ymax = models.IntegerField('最大APP举报数', default=None)
    zmin = models.IntegerField('最小APP事故数', default=None)
    zmax = models.IntegerField('最大APP事故数', default=None)
    wmin = models.IntegerField('最小122事故数', default=None)
    wmax = models.IntegerField('最大122事故数', default=None)
    cx = models.DecimalField('c1', max_digits=10, decimal_places=4, default=None)
    cy = models.DecimalField('c2', max_digits=10, decimal_places=4, default=None)
    cz = models.DecimalField('c3', max_digits=10, decimal_places=4, default=None)
    cw = models.DecimalField('c4', max_digits=10, decimal_places=4, default=None)
    a = models.DecimalField('a', max_digits=10, decimal_places=4, default=None)
    b = models.DecimalField('b', max_digits=10, decimal_places=4, default=None)
    create_time = models.DateTimeField('时间')
    region = models.SmallIntegerField('区县编号',default=-1)
    group = models.IntegerField('大队编号', default=-1)
    comment = models.TextField('备注', default='train')
    def __unicode__(self):
        return u'时间:'+ str(self.create_time) + u',备注:'+ str(self.comment) + u',最小延迟指数:' + str(self.xmin) + u',最大延迟指数:' + str(self.xmax) + u',最小APP举报数:' + str(self.ymin) + u'最大APP举报数:'\
               + str(self.ymax) + u',最小APP事故数:' + str(self.zmin) + u'最大APP事故数:' + str(self.zmax) + u'最小122事故数:' + str(self.wmin) \
               + u',最大122事故数:' + str(self.wmax) + ',cx:' + str(self.cx) + ',cy:' + str(self.cy) + ',cz:' + str(self.cz) + ',cw:' + str(self.cw) \
               + ',a:' + str(self.a) + ',b:' + str(self.b) + '\n'

class Prediction_Info(PermanentModel):
    region = models.SmallIntegerField('区县编号', default=-1)
    group = models.IntegerField('大队编号', default=-1)
    index = models.DecimalField('指挥指数', max_digits=8, decimal_places=4, default=None)
    PCAx = models.DecimalField('延迟指数PCA', max_digits=10, decimal_places=4, default=None)
    PCAy = models.DecimalField('APP举报PCA', max_digits=10, decimal_places=4, default=None)
    PCAz = models.DecimalField('APP事故PCA', max_digits=10, decimal_places=4, default=None)
    PCAw = models.DecimalField('122事故PCA', max_digits=10, decimal_places=4, default=None)
    expect_police = models.IntegerField('预估警力', default=None)
    real_police = models.IntegerField('实际警力', default=None)
    create_time = models.DateTimeField('时间')

    def __unicode(self):
        return 'PCAx:' + str(self.PCAx) + ',PCAy:' + str(self.PCAy) + 'PCAz:' + str(self.PCAz) + 'PCAw:' + str(self.PCAw) + 'u预估警力:'+ \
               str(self.expect_police) + u',实际警力:' + str(self.real_police) + u',时间:' + str(self.create_time) + '\n'
#大队的区域边界
class Region_Boundary(PermanentModel):
    region = models.SmallIntegerField('区县编号', default=-1)
    group = models.IntegerField('大队编号', default = -1)
    group_name = models.TextField('名称',default=u'无名')
    geo_boundary = models.TextField('边界')
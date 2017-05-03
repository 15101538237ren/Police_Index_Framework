# -*- coding: utf-8 -*-
import os,datetime
from process.models import *
import urllib,urllib2

def get_crowd_index():
    real_index_url = 'https://tp-restapi.amap.com/gate?sid=30010&reqData={%22city%22:%22110000%22,%22dateType%22:0,%22userdefined%22:%22true%22}&serviceKey=2F77255FF77D948DF3FED20E0C19B14F'
    req = urllib2.Request(real_index_url)
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    print res
#获取指定区域的id
def get_boundary_of(rid):
    boundary_url = 'https://tp-restapi.amap.com/gate?sid=30005&reqData={%22city%22:%22110000%22,%22linksType%22:22,%22ids%22:%22'+str(rid)+'%22}&serviceKey=2F77255FF77D948DF3FED20E0C19B14F'

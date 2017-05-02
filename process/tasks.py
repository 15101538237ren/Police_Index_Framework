# -*- coding: utf-8 -*-

import os
import urllib, urllib.request ##python2 对应urllib2
import urllib.parse
import json,helpers
from celery import shared_task

#这个文件用来后台执行保存实时指挥指数的任务

gaode_index_url_str = "https://tp-restapi.amap.com/gate?sid=30010&reqData={%22city%22:%22110000%22,%22dateType%22:0,%22userdefined%22:%22true%22}&serviceKey=2F77255FF77D948DF3FED20E0C19B14F"

class Gaode_Traffic_Index:
    host = 'https://tp-restapi.amap.com'
    path = '/gate?'
    param = {
        'sid': None,
        'serviceKey': '2F77255FF77D948DF3FED20E0C19B14F',
    }
    reqData = {}
    def __init__(self, sid, **reqData):
        self.setSid(sid)
        self.setReqData(**reqData)

    def setSid(self, sid):
        if sid != None:
            self.param['sid'] = sid

    def setReqData(self, **data):
        if data != None and isinstance(data, dict):
            if "city" in data.keys():
                self.reqData["city"] = data["city"]
            if "dataType" in data.keys():
                self.reqData["dataType"] = data["dataType"]
            if "userdefined" in data.keys():
                self.reqData["userdefined"] = data["userdefined"]
            print("YES")
            print(self.reqData)
    #发送请求
    def sendAndRec(self):
        print(self.reqData)
        url = self.host + self.path + 'reqData='+ json.dumps(self.reqData) + "&" + urllib.parse.urlencode(self.param)  ##在Python2中为urllib.urlencode
        print(url)
        data = urllib.request.urlopen(url).read()   ##Python2中为urllib.urlopen
        #print(type(r.decode("utf-8")))
        result = json.loads(data.decode("utf-8"))
        return result

@shared_task
def scheduled_jobs():
    data = urllib.request.urlopen(gaode_index_url_str).read()
    result = json.loads(data.decode("utf-8"))
    ##
    # python mysql 122



    #print(result)


    return

if __name__ == "__main__":
    sid = 30010
    #reqData = {"city":"110000", "dataType":"0", "userdefined":"true"}
    #gaode_index = Gaode_Traffic_Index(sid, **reqData)
    #result = gaode_index.sendAndRec()

    scheduled_jobs()
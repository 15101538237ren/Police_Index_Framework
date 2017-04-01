#coding=utf-8

# import urllib,urllib.request ##python2 对应urllib2
# import http.client  ##python2 对应为httplib
#########
##Python2
import urllib,urllib2
import httplib  ##pyton2 对应为httplib
#########
import json


class BaiduMap:
    precision = None
    host = 'http://api.map.baidu.com'
    path = '/geocoder/v2/?'
    param = {
              'address' : None,
              'output' : 'json',
              'ak' : 'rBHgzWXGwp7M0w0E8MSUUzrr',
              'location' : None,
              'city' : None
            }


    def __init__(self):
        self.setPercision(50)
    
    def __init__(self, city, precision=50):
        self.setCity(city)
        self.setPrecision(precision)

    #设置城市
    def setCity(self, city):
        if city != None:
            self.param['city'] = city

    #设置精度
    def setPrecision(self, precision):
        if precision > 0 and precision <= 100:
            self.precision = precision


    #根据地址得到经纬度
    def getLocation(self, address, city=None):
        self.setParam("address", address, city)
        result = self.sendAndRec()
        #for key in sorted(result):
            #print(key, '=======>', result[key])
        error = None
        if result is None:
            error = "json result is null"
        else:
            error = self.checkStatus(result['status'])
            if error is not None:
                pass
            else:
                info = result['result']
                if info['confidence'] < self.precision and False:
                    error = "low confidence:" + str(info['confidence'])
                else:
                    return (info['location']['lng'], info['location']['lat'], info['confidence'])
        #print("address="+ address)
        #print("error=" + error)
        #print("%s %s" % (address, error))
        return None


    #设置字典参数param
    def setParam(self, key, value, city):
        #根据所传地址设置内容参数
        if key == "address":
            if 'location' in self.param:
                del self.param['location']
            if city == None and 'city' in self.param and self.param['city'] == None:
                del self.param['city']
            else:
                self.param['city'] = city
        #根据所传经纬度设置内容参数
        elif key == "location":
            if 'city' in self.param:
                del self.param['city']
            if 'address' in self.param:
                del self.param['address']
        
        self.param[key] = value
 
   
    #发送请求
    def sendAndRec(self):
        url = self.host + self.path + urllib.parse.urlencode(self.param)  ##在Python2中为urllib.urlencode
        r = urllib.request.urlopen(url).read()   ##Python2中为urllib.urlopen
        #print(type(r.decode("utf-8")))
        result = json.loads(r.decode("utf-8"))
        return result


    #对返回结果的状态进行判断
    def checkStatus(self, status):
        #正确
        if status == 0:
            return None

        #对错误结果分情况判断
        error = None
        if status == 1:
            error = "server internal error"
        elif status == 2:
            error = "request parameter illegal"
        elif status == 3:
            error = "authorization check failed"
        elif status == 4:
            error = "quota check failed"
        elif status == 5:
            error = "ak not exist or illegal"
        elif status == 101:
            error = "service forbidden"
        elif status == 102:
            error = "not through white list or wrong security code"
        else:
            error = "other error"
        return error

# coding: utf-8
import math,pickle,csv
region_hash = {u"东城" : 1, u"西城": 2, u"朝阳": 5, u"海淀": 6,u"丰台":7,u"大兴":8,u"石景山":9}
region_hash2 = {u"东城区" : 1, u"西城区": 2, u"朝阳区": 5, u"海淀区": 6,u"丰台区":7,u"大兴区":8,u"石景山区":9}
pinyin_hash = {"dongcheng" : 1, "xicheng" : 2, "chaoyang":5, "haidian":6,"fengtai":7,"daxing":8,"shijingshan":9}
MAXINT = 999999999
LNG_INDEX = 0
LAT_INDEX = 1
EPS = 0.000001
#检查一个点是否在道路的多边形区域内
#如果在多边形内，返回值为1
#如果在多边形外，而且离多边形很远，返回值为0


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


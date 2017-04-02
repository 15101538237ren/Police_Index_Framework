#coding: utf-8

from process.models import *
from process.helpers import pinyin_hash
import datetime,math,plotly
import numpy as np
import plotly.graph_objs as go
from scipy.optimize import leastsq

PCA_NO = 0

###需要拟合的函数func及误差error###
def func(p,x):
    k,b=p
    return k*x+b

def error(p,x,y):
    return func(p,x)-y #x、y都是列表，故返回值也是个列表

# 输入分钟,按几分钟切割,按duration取整
def partition_time(minute, duration=10):
    quotient = int(int(minute / duration) * duration)
    return quotient

def format_time(idt, format):
    incidence_minute = partition_time(idt.minute,10)
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

#生成一天内的duration_minute为间隔的时间字符串序列
def generate_str_arr_from_time_to_time(from_time,duration_minute,second=1):
    time_delta=datetime.timedelta(days=1)
    to_time = from_time +time_delta
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

#根据起始结束时间,以及duration,isweek获取datetime_list
def get_date_time_list(start_time,end_time,duration,is_week):
    if not is_week:
        datetime_list = generate_str_arr_from_date_to_date(start_time, end_time, duration)
    else:
        time_list = generate_str_arr_from_time_to_time(start_time,duration,second=1)
        datetime_list = []
        #key 1 weekday
        for weekday in range(7):
            #key2 time
           for time_i in time_list:
                dt_str = str(weekday) + " " + time_i
                datetime_list.append(dt_str)
    return datetime_list

#根据datetime_list和是否是综合区构建region_dict
def get_region_dict(region,datetime_list):
    if region!=0:
        result_dict = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)
    else:
        result_dict = {}
        #每个区域一个dict
        for item in pinyin_hash.values():
            result_dict[str(item)] = {time:0 for time in datetime_list}   #存储key为datetime,value为举报次数(暂定为所有区域的总次数)
        result_dict['0'] = {time:0 for time in datetime_list}
    return result_dict
def get_region_avg_result(region,datetime_list,**result_dict):
    #综合区,对所有区县的数据对应时间点取平均
    if region == 0:
        for dt in datetime_list:
            len_pinyin_hash = len(pinyin_hash.values())
            sum_val = 0.0
            for item in pinyin_hash.values():
                sum_val =  sum_val + float(result_dict[str(item)][dt])
            result_dict['0'][dt] = sum_val/len_pinyin_hash
    return result_dict
#获得星期聚合结果
def get_week_agg_result(start_time,end_time,duration,region,datetime_list,**result_dict):
    week_datetime_list = get_date_time_list(start_time,end_time,duration,1)
    #记录星期聚合结果的数据dict
    week_result_dict = {time:0 for time in week_datetime_list}

    #记录星期聚合过程中每个时间点被加了几次,最后算平均时除的每个时间点size大小
    size_result_dict = {time:0 for time in week_datetime_list}
    if region != 0:
        result_dict_to_handle = result_dict
    else:
        #综合区只取综合结果
        result_dict_to_handle = result_dict['0']
    for dt_str in datetime_list:
        #格式化datetime_list 中的字符串为datetime类型
        dt_now = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        time_now = dt_str.split(" ")[1]
        weekday = dt_now.weekday()
        query_str = str(weekday) + " " + time_now
        week_result_dict[query_str] += result_dict_to_handle[dt_str]
        size_result_dict[query_str] +=1
    week_real_result = {}
    #迭代一个星期的所有时间
    for week_datetime in week_datetime_list:
        week_real_result[week_datetime] = float(week_result_dict[week_datetime])/float(size_result_dict[week_datetime])
    return week_real_result
# 处理app举报数据
#
#region:0——综合区,1~7:区县编号
#is_week:0——不按周聚合,1——按周聚合
def preprocess_app_incidence(start_time, end_time, duration, region, is_week):
    app_incidence = App_Incidence.objects.filter(create_time__range=[start_time, end_time])
    if region != 0:
        app_incidence = app_incidence.filter(region=region)
    datetime_list = get_date_time_list(start_time,end_time,duration,0)
    result_dict = get_region_dict(region,datetime_list)

    #循环遍历
    for item in app_incidence:
        idt = item.create_time
        ct_time_str = format_time(idt, "%Y-%m-%d %H:%M:%S")
        if region != 0:
            result_dict[ct_time_str] += 1
        else:
            result_dict[str(item.region)][ct_time_str] += 1

    result_dict = get_region_avg_result(region,datetime_list,**result_dict)
    if is_week:
        week_real_result = get_week_agg_result(start_time,end_time,duration,region,datetime_list,**result_dict)
        return week_real_result
    if region != 0:
        return result_dict
    else:
        return result_dict['0']


#处理违章数据
def preprocess_violation(start_time, end_time, duration, region, is_week):
    violation = Violation.objects.filter(create_time__range = [start_time, end_time])
    if region != 0:
        violation = violation.filter(region=region)

    datetime_list = get_date_time_list(start_time,end_time,duration,0)
    result_dict = get_region_dict(region,datetime_list)

    #循环遍历
    for item in violation:
        idt = item.create_time
        ct_time_str = format_time(idt, "%Y-%m-%d %H:%M:%S")
        if region != 0:
            result_dict[ct_time_str] += 1
        else:
            result_dict[str(item.region)][ct_time_str] += 1

    result_dict = get_region_avg_result(region,datetime_list,**result_dict)
    if is_week:
        week_real_result = get_week_agg_result(start_time,end_time,duration,region,datetime_list,**result_dict)
        return week_real_result
    if region != 0:
        return result_dict
    else:
        return result_dict['0']

#处理122报警数据
def preprocess_call_incidence(start_time, end_time, duration, region, is_week):
    call_incidences = Call_Incidence.objects.filter(create_time__range = [start_time, end_time])
    if region != 0:
        call_incidences = call_incidences.filter(region=region)

    datetime_list = get_date_time_list(start_time,end_time,duration,0)
    result_dict = get_region_dict(region,datetime_list)

    #循环遍历
    for item in call_incidences:
        idt = item.create_time
        ct_time_str = format_time(idt, "%Y-%m-%d %H:%M:%S")
        if region != 0:
            result_dict[ct_time_str] += 1
        else:
            result_dict[str(item.region)][ct_time_str] += 1

    result_dict = get_region_avg_result(region,datetime_list,**result_dict)
    if is_week:
        week_real_result = get_week_agg_result(start_time,end_time,duration,region,datetime_list,**result_dict)
        return week_real_result
    if region != 0:
        return result_dict
    else:
        return result_dict['0']


#处理拥堵指数数据
def preprocess_crowd_index(start_time, end_time, duration, region, is_week):
    crowd_index = Crowd_Index.objects.filter(create_time__range = [start_time, end_time]).filter(bussiness_area=None)
    if region != 0:
        crowd_index = crowd_index.filter(region=region)

    datetime_list = get_date_time_list(start_time,end_time,duration,0)
    result_dict = get_region_dict(region,datetime_list)

    #循环遍历
    for item in crowd_index:
        idt = item.create_time
        ct_time_str = format_time(idt, "%Y-%m-%d %H:%M:%S")
        if region != 0:
            result_dict[ct_time_str] = item.crowd_index
        else:
            result_dict[str(item.region)][ct_time_str] = item.crowd_index
    result_dict = get_region_avg_result(region,datetime_list,**result_dict)
    if is_week:
        week_real_result = get_week_agg_result(start_time,end_time,duration,region,datetime_list,**result_dict)
        return week_real_result
    if region != 0:
        return result_dict
    else:
        return result_dict['0']


#处理警力数据
def preprocess_police(start_time, end_time, duration, region, is_week):
    polices = Police.objects.filter(create_time__range = [start_time, end_time])
    if region != 0:
        polices = polices.filter(region=region).order_by("create_time")

    datetime_list = get_date_time_list(start_time,end_time,duration,0)
    result_dict = get_region_dict(region,datetime_list)

    last_dt = None
    last_val = None
    partitions = int(60 / duration)

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
                    result_dict[str(item.region)][ct_time_str] =  val
            last_dt = now_dt
            last_val = now_val

    result_dict = get_region_avg_result(region,datetime_list,**result_dict)
    if is_week:
        week_real_result = get_week_agg_result(start_time,end_time,duration,region,datetime_list,**result_dict)
        return week_real_result
    if region != 0:
        return result_dict
    else:
        return result_dict['0']
#求乘积之和
#a,b:输入的两个序列
#输出:两序列a,b的乘积之和
def multipl(a,b):
    sumofab=0.0
    for i in range(len(a)):
        temp=a[i]*b[i]
        sumofab+=temp
    return sumofab

#计算两个序列的Pearson相关系数
#x,y :输入的浮点数序列
#输出: pearson相关系数
def corrcoef(x,y):
    n=len(x)
    #求和
    sum1=sum(x)
    sum2=sum(y)
    #求乘积之和
    sumofxy=multipl(x,y)
    #求平方和
    sumofx2 = sum([pow(i,2) for i in x])
    sumofy2 = sum([pow(j,2) for j in y])
    num=sumofxy-(float(sum1)*float(sum2)/n)
    #计算皮尔逊相关系数
    den=math.sqrt((sumofx2-float(sum1**2)/n)*(sumofy2-float(sum2**2)/n))
    return num/den

# pca 函数
# data : 输入矩阵数据
# nRedDim:目标主成分个数
# normalise:是否标准化
# 输出: x:产生新的数据矩阵,y:重新计算的原数据,evals:特征值,evecs:特征向量
def pca(data,nRedDim=0,normalise=0):
    # 数据标准化
    m = np.mean(data,axis=0)
    data -= m
    # 协方差矩阵
    C = np.cov(np.transpose(data))
    # 计算特征值特征向量，按降序排序
    evals,evecs = np.linalg.eig(C)
    indices = np.argsort(evals)
    indices = indices[::-1]
    evecs = evecs[:,indices]
    evals = evals[indices]
    if nRedDim>0:
        evecs = evecs[:,:nRedDim]

    if normalise:
        for i in range(np.shape(evecs)[1]):
            evecs[:,i] / np.linalg.norm(evecs[:,i]) * np.sqrt(evals[i])
    # 产生新的数据矩阵
    x = np.dot(np.transpose(evecs),np.transpose(data))
    # 重新计算原数据
    y = np.transpose(np.dot(evecs,x)) + m
    return x,y,evals,evecs
#获取4中类型数据的矩阵,包括预处理,Normalize
def get_data_array(start_time, end_time, region, is_week, duration=10, is_calc_police = False, is_normalize=1):
    #以下每个数据都是一个dict,键为datetime
    app_incidence = preprocess_app_incidence(start_time, end_time, duration, region, is_week)
    print("finished get app_incidence data!")
    violation = preprocess_violation(start_time, end_time, duration, region, is_week)
    print("finished get violation data!")
    call_incidence = preprocess_call_incidence(start_time, end_time, duration, region, is_week)
    print("finished get call_incidence data!")
    crowd_index = preprocess_crowd_index(start_time,end_time,duration,region,is_week)
    print("finished get crowd_index data!")
    datetime_list = get_date_time_list(start_time,end_time,duration,is_week)
    data_arr = [[] for i in range(4)]
    if(is_calc_police == True):
        police_data_arr = []
        polices = preprocess_police(start_time, end_time, duration, region, is_week)
        print("finished get polices data!")
    for datetime_str in datetime_list:
        if(is_calc_police == True):
            if polices[datetime_str] != 0:
                police_data_arr.append(polices[datetime_str])
                data_arr[0].append(float(app_incidence[datetime_str]))
                data_arr[1].append(float(violation[datetime_str]))
                data_arr[2].append(float(call_incidence[datetime_str]))
                data_arr[3].append(float(crowd_index[datetime_str]))
        else:
            data_arr[0].append(float(app_incidence[datetime_str]))
            data_arr[1].append(float(violation[datetime_str]))
            data_arr[2].append(float(call_incidence[datetime_str]))
            data_arr[3].append(float(crowd_index[datetime_str]))

    np_data_array = np.array(data_arr)

    (rows,cols) = np_data_array.shape

    if(is_normalize == 1):
        row_mins = np_data_array.min(axis=1)
        row_mins_tmp = np.repeat(row_mins, cols).reshape((rows, cols))
        row_maxs = np_data_array.max(axis=1)
        row_maxs_tmp = np.repeat(row_maxs, cols).reshape((rows, cols))
        row_range = row_maxs_tmp - row_mins_tmp
        normed_data_array = (np_data_array - row_mins_tmp)/row_range
    else:
        row_mins = 0  ##这个步骤row_mins和row_maxs没有用到
        row_maxs = 0
        normed_data_array = np_data_array
    print("normalized data successfully!")
    if(is_calc_police == True):
        police_data_arr = np.array(police_data_arr)
        polices_max = float(police_data_arr.max())
        normed_polices = police_data_arr / polices_max
        return [normed_data_array, normed_polices, row_mins, row_maxs]
    return [normed_data_array, row_mins, row_maxs]
#训练函数
#start_time: 起始时间
#end_time: 结束时间
#duration: 时间间隔
def train(start_time, end_time, region, is_week, duration=10):
    #获取4种类型数据的矩阵
    [normed_data_array, row_mins, row_maxs] = get_data_array(start_time, end_time, region, is_week, duration)
    x,y,evals,evecs = pca(np.transpose(normed_data_array),nRedDim=4,normalise=0)
    pca_no = 0
    if all( evecs[:,pca_no] < np.zeros(len(evecs[:,pca_no]))):
        evecs = evecs * -1
    return [evecs, row_mins, row_maxs]


def test_region(evecs, pca_no,start_time, end_time, region, is_week, duration=10):
    #获取4种类型数据的矩阵

    #以下每个数据都是一个dict,键为datetime
    app_incidence = preprocess_app_incidence(start_time, end_time, duration, region, is_week)
    print("finished get app_incidence data!")
    violation = preprocess_violation(start_time, end_time, duration, region, is_week)
    print("finished get violation data!")
    call_incidence = preprocess_call_incidence(start_time, end_time, duration, region, is_week)
    print("finished get call_incidence data!")
    crowd_index = preprocess_crowd_index(start_time,end_time,duration,region,is_week)
    print("finished get crowd_index data!")
    datetime_list = get_date_time_list(start_time,end_time,duration,is_week)
    data_arr = [[] for i in range(4)]
    police_data_arr = []
    polices = preprocess_police(start_time, end_time, duration, region, is_week)
    print("finished get polices data!")
    for datetime_str in datetime_list:
        if polices[datetime_str] != 0:
            police_data_arr.append(polices[datetime_str])
            data_arr[0].append(float(app_incidence[datetime_str]))
            data_arr[1].append(float(violation[datetime_str]))
            data_arr[2].append(float(call_incidence[datetime_str]))
            data_arr[3].append(float(crowd_index[datetime_str]))
    police_data_arr = np.array(police_data_arr)
    np_data_array = np.array(data_arr)

    polices_max = float(police_data_arr.max())
    normed_polices = police_data_arr / polices_max

    (rows,cols) = np_data_array.shape
    row_mins = np_data_array.min(axis=1)
    row_mins = np.repeat(row_mins,cols).reshape((rows,cols))

    row_maxs = np_data_array.max(axis=1)
    row_maxs = np.repeat(row_maxs,cols).reshape((rows,cols))

    row_range = row_maxs - row_mins
    normed_data_array = (np_data_array - row_mins)/row_range
    print("normalized data successfully!")
    if all( evecs[:,pca_no] < np.zeros(len(evecs[:,pca_no]))):
        evecs = evecs * -1

    evecs_arr = np.array(evecs[:,pca_no])
    transformed_arr = np.array(np.matrix(np.transpose(normed_data_array)) * np.transpose(np.matrix(evecs_arr.real)))

    trace = go.Scatter(
        x = transformed_arr[:,0],
        y = list(normed_polices),
        mode = 'markers',
        name = 'pca1-警力',
        marker=dict(
            # size=3,
            color = normed_polices,
            colorscale =
            # [
            # [0.0, "#87CEFA"], [1.0,"rgb(255,0,0)"]
            # ],
            [
            [0.0, "rgb(0,255,0)"], [0.111111111111, "rgb(215,48,39)"], [0.222222222222, "rgb(244,109,67)"], [0.333333333333, "rgb(253,174,97)"], [0.444444444444, "rgb(254,224,144)"], [0.555555555556, "rgb(224,243,248)"], [0.666666666667, "rgb(171,217,233)"], [0.777777777778, "rgb(116,173,209)"], [0.888888888889, "rgb(69,117,180)"], [1.0, "rgb(49,54,149)"]
            ],
            showscale=True
        )
    )
    data = [trace]
    layout = go.Layout(
                    xaxis=dict(
                        autotick=False,
                        tick0=0,
                        ticks='outside',
                        dtick=0.2,
                        ticklen=1.3,
                        tickwidth=4,
                        # ticks='',
                        # showticklabels=False,
                        tickcolor='#000',
                        title='PCA1',
                        titlefont=dict(
                            family='Arial, sans-serif',
                            size=24,
                            color='black'
                        ),
                        tickfont=dict(
                        family='Arial, sans-serif',
                        size=20,
                        color='black'
                        ),
                        zerolinecolor='#000000',
                        zerolinewidth=3,
                    ),
                    yaxis=dict(
                        autotick=False,
                        ticks='outside',
                        tick0=-1.0,
                        dtick=0.1,
                        ticklen=0.8,
                        tickwidth=4,
                        tickcolor='#000',
                        title=u'警力水平',
                        titlefont=dict(
                            family='Arial, sans-serif',
                            size=24,
                            color='black'
                        ),
                        tickfont=dict(
                        family='Arial, sans-serif',
                        size=20,
                        color='black'
                        ),
                        zerolinecolor='#000000',
                        zerolinewidth=3,
                    ))
    plotly.offline.plot({"data" : data , "layout" : layout})
###
# evecs: 表示特征向量
# pca_no: 表示主成分的编号
# start_time: 开始时间
# end_time: 结束时间
# duration: 时间间隔
# region: 区域编号
# is_week: 表示是否按照星期聚合
###
def getNormedDataArray(evecs, pca_no, start_time, end_time, duration, region, is_week):
    [normed_data_array, normed_polices, row_mins, row_maxs] = get_data_array(start_time, end_time, region, is_week, duration=10, is_calc_police=True)
    if all(evecs[:, pca_no] < np.zeros(len(evecs[:, pca_no]))):
        evecs = evecs * -1

    evecs_arr = np.array(evecs[:, pca_no])
    transformed_arr = np.array(np.matrix(np.transpose(normed_data_array)) * np.transpose(np.matrix(evecs_arr.real)))
    #返回第一个主成分的值
    return [transformed_arr[:, 0], normed_polices]

def saveTarinParameter(evecs, row_mins, row_maxs, start_time, end_time, duration, region_id, is_week, create_time):
    PCA_NO = 0
    [PCA_x, Police_y] = getNormedDataArray(evecs, PCA_NO, start_time, end_time, duration, region_id, is_week)
    # 下面的二维array第二个0表示PCA_num
    app_incidence = evecs[0, PCA_NO]
    violation = evecs[1, PCA_NO]
    call_incidence = evecs[2, PCA_NO]
    crowd_index = evecs[3, PCA_NO]
    p0 = [0.6, 0.12]
    Para = leastsq(error, p0, args=(PCA_x, Police_y))  # 把error函数中除了p以外的参数打包到args中k2,b2=Para[0]
    train_parameter = Train_Parameter(xmin=row_mins[0], xmax=row_maxs[0], ymin=row_mins[1], ymax=row_maxs[1],
                                      zmin=row_mins[2], zmax=row_maxs[2], wmin=row_mins[3], wmax=row_maxs[3],
                                      cx=crowd_index, cy=violation, cz=app_incidence, cw=call_incidence,
                                      a=p0[0], b=p0[1], create_time=create_time, region=region_id)
    train_parameter.save()

def trainRegion(start_time, end_time, is_region, is_week, duration=10):
    create_time = datetime.datetime.now()
    if(is_region == 0):
        region_id = 0
        [evecs, row_mins, row_maxs] = train(start_time, end_time, region_id, is_week, duration)
        for key in pinyin_hash.keys():
            region_id_tmp = pinyin_hash[key]
            saveTarinParameter(evecs, row_mins, row_maxs, start_time, end_time, duration, region_id_tmp, is_week, create_time)
    else:
        for key in pinyin_hash.keys():
            region_id = pinyin_hash[key]
            [evecs, row_mins, row_maxs] = train(start_time, end_time, region_id, is_week, duration)
            saveTarinParameter(evecs, row_mins, row_maxs, start_time, end_time, duration, region_id, is_week,
                               create_time)
##
#按照时间点来查询
#query_time: 驶入的查询时间点，datetime类型
##
def getDataFromeTime(query_time, region, duration=10):
    time_delta = datetime.timedelta(minutes=duration)
    end_time = query_time + time_delta
    return [query_time, end_time, get_data_array(query_time, end_time, region, is_week=0, duration=duration, is_calc_police=False, is_normalize=0)]

def OutputRegionIndex(query_time, duration=10):
    train_parameter = Train_Parameter.objects.order_by('-create_time')[0]  #获取最新的Train_Parameter
    Index_range = 3
    region_pca = {}
    for key in pinyin_hash.keys():
        region_id = pinyin_hash[key]
        ##这里调用数据的时候不做normalize
        [start_time, end_time, result_data] = getDataFromeTime(query_time, region_id, duration=duration)
        data_array = result_data[0]  ##表示原始4种数据, 4*1的矩阵
        normed_data_min_list = [float(train_parameter.xmin), float(train_parameter.ymin), float(train_parameter.zmin), float(train_parameter.wmin)]
        normed_data_list = [float(train_parameter.xmax - train_parameter.xmin), float(train_parameter.ymax - train_parameter.ymin),
                            float(train_parameter.zmax - train_parameter.zmin), float(train_parameter.wmax - train_parameter.wmin)]
        normed_data_min = np.transpose(np.matrix(normed_data_min_list))  ##利用转置变成4*1的矩阵
        normed_data_range = np.transpose(np.matrix(normed_data_list))
        normed_data_array = (data_array - normed_data_min)/normed_data_range
        PCA_NO = 0
        evecs = [float(train_parameter.cx), float(train_parameter.cy), float(train_parameter.cz), float(train_parameter.cw)]
        if all(evecs < np.zeros(len(evecs))):
            evecs = evecs * -1
        evecs_arr = np.array(evecs)
        #print("region_id: " + str(region_id) + ", evecs = ")
        #print(evecs_arr)
        #print(normed_data_array)
        transformed_arr = np.matrix(np.transpose(normed_data_array)) * np.transpose(np.matrix(evecs_arr.real))
        PCA_x = transformed_arr[0, 0]  #取第一个主成分的值
        #print(PCA_x)
        region_pca[str(region_id)] = int(round(Index_range * PCA_x,2)*100)
    print(region_pca)
    return region_pca


if __name__ == "__main__":
    pass
import time
import Tools as tl
import pandas as pd


def instance_preprocess(a, parameters, name):
    ######### 读取算离乘客、司机编号信息
    r_instance = []
    d_instance = []
    instance_df = pd.read_csv(name)
    for i in range(instance_df.shape[0]):
        if instance_df['rider'][i] == 1:
            r_instance.append(instance_df['id'][i])
        if instance_df['driver'][i] == 1:
            d_instance.append(instance_df['id'][i])
    print('算例{}包含乘客{}名、司机{}名'.format(a, len(r_instance), len(d_instance)))
    ########### 读取乘客、司机、站点、道路网络相关的数据
    s1 = time.time()
    rider = tl.DataReader().rider_reader('Data/rider.csv', r_instance)
    driver = tl.DataReader().driver_reader('Data/driver.csv', d_instance)
    station = tl.DataReader().station_reader('Data/station.xls')
    sta_sta = tl.DataReader().stasta_reader('Data/station-station.xls')
    dri_sta = tl.DataReader().driver_station_reader('Data/driver_station.csv', d_instance)
    rid_sta = tl.DataReader().rider_station_reader('Data/rider_station.csv', r_instance)
    rid_dri = tl.DataReader().rider_driver_reader('Data/rider_driver.csv', r_instance, d_instance)
    '''提前处理相关相关数据'''
    ###### 乘客分类，集合存
    type_SR, type_RT, type_TR = tl.type_rider(rider, parameters.W_max)
    print('类型1：乘客{}名，类型2：{}名，类型3：{}名，类型4：{}名'.format(0, len(type_RT), len(type_TR), len(type_SR)))
    ###### 预处理每个乘客的可选乘客和司机，确定每个站点的可行匹配时可利用这个缩减搜索范围
    for s in station.keys():
        station[s].pick_rider(rid_sta, r_instance)
        station[s].pick_driver(dri_sta, d_instance)
    ###### 预处理每个司机可匹配的乘客，针对每个司机只选择预处理范围内的乘客进行可行匹配判定，缩减搜索范围
    for d in driver.keys():
        driver[d].pick_rider(rid_dri)
    e1 = time.time()
    print('读取数据和预处理总共需要{}秒（{}分钟）'.format(round(e1 - s1, 4), round((e1 - s1)/60, 4)))
    # 将所有的信息存储在信息对象中
    information = tl.Information(
        rider, driver, dri_sta, rid_sta, rid_dri, sta_sta, type_SR, type_RT, type_TR, station, parameters
    )
    return information, r_instance, d_instance



############ 参数类：算法涉及的变量及相应的信息
class Information:
    def __init__(self, rider, driver, dri_sta, rid_sta, rid_dri, sta_sta, type_SR, type_RT, type_TR,
                 station, parameters):
        self.rider = rider
        self.driver = driver
        self.station = station
        self.dri_sta = dri_sta
        self.rid_sta = rid_sta
        self.rid_dri = rid_dri
        self.sta_sta = sta_sta
        self.type_SR = type_SR
        self.type_RT = type_RT
        self.type_TR = type_TR
        self.parameters = parameters          # 参数对象
    '''参数计算：初始广义成本'''
    def compute_gencost(self, alpha):
        # 根据灵活性指标参数更新对应的初始广义成本（时间成本系数变化导致的）
        for i in self.rider.keys():
            self.rider[i].update_gencost(alpha)
        for j in self.driver.keys():
            self.driver[j].update_gencost(alpha)
    '''参数计算：乘客和司机的时间参数'''
    def compute_time(self, flex_pick, flex_trip_max, flex_trip_r, flex_trip_d):
        # 更新对应的时间约束相关参数
        for i in self.rider.keys():
            self.rider[i].update_time(flex_pick, flex_trip_r, flex_trip_max)
        for j in self.driver.keys():
            self.driver[j].update_time(flex_pick, flex_trip_d, flex_trip_max)



























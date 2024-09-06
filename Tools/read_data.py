import pandas as pd
import Tools as tl

'''读取Data需求信息和网络信息类：'''
class DataReader:
    def __init__(self):
        pass
    ###### 读取并记录地铁站的信息，包括站点0
    def station_reader(self, file):
        df = pd.read_excel(file, sheet_name='Sheet1')
        dic = {}
        row = tl.Station(0, 0, 0)
        dic[0] = row
        for i in range(df.shape[0]):
            row = tl.Station(df.ID[i], df.lon[i], df.lat[i])
            dic[df.ID[i]] = row
        return dic
    ####### 读取并记录地铁网络的信息
    def stasta_reader(self, file):
        df = pd.read_excel(file, sheet_name='Sheet1')
        dic = {}
        for i in range(df.shape[0]):
            # 每个站点--站点之间的具体信息
            row = tl.StaSta(df.trans_cost[i], df.trans_duration[i])
            dic[df.org_num[i], df.des_num[i]] = row
        return dic
    ####### 读取并记录乘客的所有信息，存储再字典dic中
    def rider_reader(self, file, r_ins):
        df = pd.read_csv(file)     # 读取rider.csv的信息
        df = df[df['id'].isin(r_ins)]    # 提取部分乘客
        df = df.reset_index(drop=True)
        dic = {}
        for i in range(df.shape[0]):
            # 每个乘客的具体信息
            row = tl.Rider(df.id[i], df.org_lon[i], df.org_lat[i], df.des_lon[i], df.des_lat[i], df.pickup_time[i],
                           df.distance[i], df.drive_time[i], df.org_sta[i], df.org_dis[i], df.org_time[i],
                           df.des_sta[i], df.des_dis[i], df.des_time[i], df.alone_cost[i], df.alone_time[i],
                           df.departure[i], df.Tmax[i], df.arrival[i])
            dic[df.id[i]] = row
        return dic
    ####### 读取并记录司机的所有信息，存储再字典dic中
    def driver_reader(self, file, d_ins):
        df = pd.read_csv(file)
        df = df[df['id'].isin(d_ins)]
        df = df.reset_index(drop=True)
        dic = {}
        for i in range(df.shape[0]):
            # 每个司机的具体信息
            row = tl.Driver(df.id[i], df.org_lon[i], df.org_lat[i], df.des_lon[i], df.des_lat[i], df.pickup_time[i],
                            df.distance[i], df.drive_time[i], df.alone_cost[i], df.alone_time[i],
                            df.departure[i], df.Tmax[i], df.arrival[i])
            dic[df.id[i]] = row
        return dic
    ####### 读取司机和站点的网络
    def driver_station_reader(self, file, d_ins):
        df = pd.read_csv(file)
        df = df[df['driver_id'].isin(d_ins)]
        df = df.reset_index(drop=True)
        dic = {}
        for i in range(df.shape[0]):
            row = tl.DriverStation(df.o_v[i], df.v_d[i])
            dic[df.driver_id[i], df.station_id[i]] = row
        return dic
    ####### 读取乘客和站点的网络
    def rider_station_reader(self, file, r_ins):
        df = pd.read_csv(file)
        df = df[df['rider_id'].isin(r_ins)]
        df = df.reset_index(drop=True)
        dic = {}
        for i in range(df.shape[0]):
            row = tl.RiderStation(df.o_v[i], df.v_d[i])
            dic[df.rider_id[i], df.station_id[i]] = row
        return dic
    ####### 读取乘客和司机的网络
    def rider_driver_reader(self, file, r_ins, d_ins):
        df = pd.read_csv(file)
        df = df[df['rider_id'].isin(r_ins)]
        df = df[df['driver_id'].isin(d_ins)]
        df = df.reset_index(drop=True)
        dic = {}
        for i in range(df.shape[0]):
            row = tl.RiderDriver(df.o_o[i], df.d_d[i])
            dic[df.rider_id[i], df.driver_id[i]] = row
        return dic


'''站点、乘客、司机、地铁网络、以及路网等信息类'''

############ 站点类
class Station:
    def __init__(self, ID, lon, lat):
        self.ID = ID              # 编号
        self.lon = lon            # 经度
        self.lat = lat            # 纬度
        self.rider = set()        # 能够经过该站点的乘客集合
        self.driver = set()       # 能够经过该站点的司机集合
    def pick_rider(self, rider_station: dict, r_list):
        # 可以在该站点换乘的乘客
        if self.ID != 0:
            self.rider = set()
            for (r, s) in rider_station.keys():
                if s == self.ID:
                    self.rider.add(r)
        else:
            self.rider = set(r_list)    # 所有乘客均可经过站点0
    def pick_driver(self, driver_station: dict, d_list):
        # 可以在该站点换乘的司机
        if self.ID != 0:
            self.driver = set()
            for (d, s) in driver_station.keys():
                if s == self.ID:
                    self.driver.add(d)
        else:
            self.driver = set(d_list)    # 所有司机均可经过站点0


########### 地铁网络类
class StaSta:
    def __init__(self, trans_cost, trans_duration):
        self.trans_cost = trans_cost                    # 任意两个站点之间的成本
        self.trans_duration = trans_duration            # 任意两个站点之间的时间


########### 乘客类
class Rider:
    def __init__(self, id, org_lon, org_lat, des_lon, des_lat, pickup_time, distance, drive_time, org_sta,
                 org_dis, org_time, des_sta, des_dis, des_time, alone_cost, alone_time, departure, Tmax,
                 arrival):
        self.id = id                        # 编号
        self.org_lon = org_lon              # 起点经度
        self.org_lat = org_lat              # 起点纬度
        self.des_lon = des_lon              # 终点经度
        self.des_lat = des_lat              # 终点纬度
        self.pickup_time = pickup_time      # 接上乘客的时间
        self.distance = distance            # 开车出行的距离
        self.drive_time = drive_time        # 开车出行的时间
        self.org_sta = org_sta              # 离起点最近的站点编号
        self.org_dis = org_dis              # 离起点最近站点到起点的距离
        self.org_time = org_time            # 离起点最近站点到起点的步行时间
        self.des_sta = des_sta              # 离终点最近的站点编号
        self.des_dis = des_dis              # 离终点最近站点到起点的距离
        self.des_time = des_time            # 离终点最近站点到起点的步行时间
        self.alone_cost = alone_cost        # 单独出行的成本，类型1乘客为公交出行成本，其他类型乘客为出租车出行成本
        # self.transit_time = transit_time    # 公交出行的时间（非类型1乘客此项为0）
        self.alone_time = alone_time        # 单独出行的时间
        self.gencost = 0                    # 初始广义成本
        self.departure = departure          # 最早出发时间
        self.Tmax = Tmax                    # 最大行程时间
        self.arrival = arrival              # 最晚到达时间
        self.station = {0}                  # 包括站点0
        self.driver = set()
    def update_gencost(self, alpha):
        # 计算单独出行的广义成本
        self.gencost = self.alone_cost + self.alone_time * alpha
    def update_time(self, flex_pick, flex_trip_r, flex_trip_max):
        # 计算乘客出行时间约束对应的参数
        self.departure = self.pickup_time - flex_pick
        self.Tmax = min(self.drive_time * (1 + flex_trip_r), self.drive_time + flex_trip_max)
        self.arrival = self.departure + flex_pick + self.Tmax
    def pick_station(self, rider_station: dict, valid_sta: set):
        # 提前预处理出该乘客可以使用的站点
        # 包括站点0
        self.station = {0}
        for (r, s) in rider_station.keys():
            if r == self.id and s in valid_sta:
                self.station.add(s)
    def pick_driver(self, rider_driver: dict):
        # 提前预处理出该乘客可以匹配的司机
        self.driver = set()
        for (r, d) in rider_driver.keys():
            if r == self.id:
                self.driver.add(d)


########### 司机类
class Driver:
    def __init__(self, id, org_lon, org_lat, des_lon, des_lat, pickup_time,
                 distance, drive_time, alone_cost, alone_time, departure, Tmax, arrival):
        self.id = id                       # 编号
        self.org_lon = org_lon             # 起点经度
        self.org_lat = org_lat             # 起点纬度
        self.des_lon = des_lon             # 终点经度
        self.des_lat = des_lat             # 终点纬度
        self.pickup_time = pickup_time     # 该订单被接上的时间
        self.distance = distance           # 开车的距离
        self.drive_time = drive_time       # 开车的时间
        self.alone_cost = alone_cost       # 单独出行的成本
        self.alone_time = alone_time       # 单独出行的时间
        self.gencost = 0                   # 初始广义成本
        self.departure = departure         # 最早出发时间
        self.Tmax = Tmax                   # 最大行程时间
        self.arrival = arrival             # 最晚到达时间
        self.station = {0}  # 包括站点0
        self.rider = set()
    def update_gencost(self, alpha):
        # 计算单独出行的广义成本
        self.gencost = self.alone_cost + self.alone_time * alpha
    def update_time(self, flex_pick, flex_trip_d, flex_trip_max):
        # 计算司机出行时间约束对应的参数
        self.departure = self.pickup_time - flex_pick
        self.Tmax = min(self.drive_time * (1 + flex_trip_d), self.drive_time + flex_trip_max)
        self.arrival = self.departure + flex_pick + self.Tmax
    def pick_station(self, driver_station: dict, valid_sta: set):
        # 提前预处理出每个司机可以换乘的站点
        self.station = {0}
        for (d, s) in driver_station.keys():
            if d == self.id and s in valid_sta:
                self.station.add(s)
    def pick_rider(self, rider_driver: dict):
        # 每个司机可以匹配的乘客
        self.rider = set()
        for (r, d) in rider_driver.keys():
            if d == self.id:
                self.rider.add(r)


########### driver-station网络
class DriverStation:
    def __init__(self, o_v, v_d):
        self.o_v = o_v              # 司机起点到站点v的开车时间
        self.v_d = v_d              # 站点v到司机终点的开车时间


########### rider-station网络
class RiderStation:
    def __init__(self, o_v, v_d):
        self.o_v = o_v              # 乘客起点到站点v的开车时间
        self.v_d = v_d              # 站点v到乘客终点的开车时间


########### rider-driver网络
class RiderDriver:
    def __init__(self, o_o, d_d):
        self.o_o = o_o              # 乘客起点到司机起点的开车时间
        self.d_d = d_d              # 乘客终点到司机终点的开车时间




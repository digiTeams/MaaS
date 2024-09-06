import pandas as pd
import numpy as np
import random
import datetime
import Tools as tl
import copy

def compute_time(df, type):
    # 计算单独出行的成本、时间
    if type == 'driver':
        df['alone_cost'] = df['distance'] * parameters.cost_car
        df['alone_time'] = df['drive_time']
    else:
        for i in range(df.shape[0]):
            if df['distance'][i] <= 2 * 1000:
                df.loc[i, 'alone_cost'] = parameters.taxi_start
            else:
                df.loc[i, 'alone_cost'] = parameters.taxi_start + (df['distance'][i] - 2*1000) * parameters.taxi_cost
            df.loc[i, 'alone_time'] = df['drive_time'][i]
    # 根据灵活性参数构造三个时间窗限制
    df['departure'] = df['pickup_time'] - parameters.flex_pick
    if type == 'driver':
        for i in range(df.shape[0]):
            df.loc[i, 'Tmax'] = min(df['drive_time'][i] * (1 + parameters.flex_trip_d),
                                    df['drive_time'][i] + parameters.flex_trip_max)
    else:
        for i in range(df.shape[0]):
            df.loc[i, 'Tmax'] = min(df['drive_time'][i] * (1 + parameters.flex_trip_r),
                                    df['drive_time'][i] + parameters.flex_trip_max)
    df['arrival'] = df['departure'] + parameters.flex_pick + df['Tmax']



def select_driver(df, num):
    '''
    首先选择合适的司机
    :param df: OD对表格
    :param num: 司机数量
    :return: 存储司机信息driver.csv，司机编号列表
    '''
    # 挑选出距离大于7000的OD对，从中随机挑选作为司机
    df_driver = df[df['distance'] >= 7000]
    # 取出挑选后的id num列表
    list1 = list(np.array(df_driver['id num']))
    # 随机挑选司机，并从小到达排序
    driver_list = random.sample(list1, num)
    driver_list.sort()
    print('提取司机编号', len(driver_list), driver_list)
    # 提取司机列表中对应的OD对，并更新index
    df_driver = df_driver[df_driver['id num'].isin(driver_list)]
    df_driver = df_driver.reset_index(drop=True)
    # 去掉多余的信息
    df_driver = df_driver.drop(['id', 'time1', 'time2', 'newt2', 'org_sta', 'org_dis',
                                'org_time', 'des_sta', 'des_dis', 'des_time'], axis=1)
    # 给id num, newt1 重新命名
    new_name = {'id num': 'od_num', 'newt1': 'pickup_time', 'drive time': 'drive_time'}
    df_driver = df_driver.rename(columns=new_name)
    # 计算单独开车成本、三个时间窗参数
    compute_time(df_driver, 'driver')
    # 加入新的司机编号索引列
    df_driver.insert(0, 'id', [i for i in range(1, len(driver_list)+1)])
    df_driver.to_csv('driver.csv', index=False)
    return driver_list



def select_rider(df, driver, num):
    '''
    选择合适的乘客
    :param df: OD对表格
    :param driver: 已经挑选的司机
    :param num: 乘客数量
    :return: 存储乘客信息rider.csv，乘客编号列表
    '''
    # 挑选出剩余的OD对
    all = list(np.array(df['id num']))  # 全部OD编号
    rest = list(set(all) - set(driver))
    # 筛选出无法使用公共交通出行的乘客
    rest_copy = copy.deepcopy(rest)
    for i in rest_copy:
        if df['org_dis'][i - 1] <= W_max and df['des_dis'][i - 1] <= W_max and df['org_sta'][i] != df['des_sta'][i]:
            rest.remove(i)
    # 从剩余OD对中随机生成乘客
    rider_list = random.sample(rest, num)
    print('提取乘客编号', len(rider_list), rider_list)
    # 提取出乘客对应的OD对
    df_rider = df[df['id num'].isin(rider_list)]
    df_rider = df_rider.reset_index(drop=True)
    # 去掉多余的信息
    df_rider = df_rider.drop(['id', 'time1', 'time2', 'newt2'], axis=1)
    # 给id num, newt1 重新命名
    new_name = {'id num': 'od_num', 'newt1': 'pickup_time', 'drive time': 'drive_time'}
    df_rider = df_rider.rename(columns=new_name)
    # 计算单独开车（乘坐公共交通）的成本、三个时间窗参数
    compute_time(df_rider, 'rider')
    # 增加乘客的编号索引列
    df_rider.insert(0, 'id', [i for i in range(1, len(rider_list)+1)])
    df_rider.to_csv('rider.csv', index=False)
    return rider_list



if __name__ == "__main__":
    # 参数
    parameters = tl.Parameters()
    print('时间灵活性参数flex_pick: {}, flex_trip_r: {}, flex_trip_d: {}'.format(
        parameters.flex_pick, parameters.flex_trip_r, parameters.flex_trip_d)
    )
    num_drivers = parameters.total_drivers
    num_riders = parameters.total_riders
    W_max = parameters.W_max      # 最大可接受步行距离
    sta_sta = tl.DataReader().stasta_reader('station-station.xls')
    df_od = pd.read_csv('AllODpairs.csv')
    # 选定司机和乘客，这里需要按照最宽松的灵活时间参数计算时间窗约束，方便进行数据预处理
    start = datetime.datetime.now()
    driver_list = select_driver(df_od, num_drivers)
    rider_list = select_rider(df_od, driver_list, num_riders)
    end = datetime.datetime.now()
    print(num_drivers, '个司机', num_riders, '个乘客', '生成乘客司机信息需要时间', (end-start).total_seconds()/60)
    # 0.144min




import pandas as pd
import time
import os
import Tools as tl



def select_od(df):
    '''
    按距离时间位置等筛选OD对
    :param df: 筛选前存储OD对的表
    :return: 筛选后存储OD对的表
    '''
    # 挑选出距离大于5000米的OD订单
    df = df[df.distance > 5000]
    # 挑选出早高峰内符合时间条件的OD订单
    df = df[df.newt1 < df.newt2]
    df = df[(df.newt1 >= peak_start) & (df.newt1 <= peak_end)]
    df = df[(df.newt2 >= peak_start) & (df.newt2 <= peak_end)]
    # 挑选出成都四环范围内的OD订单
    df = df[(df.org_lat > lat_low) & (df.org_lat < lat_high)]
    df = df[(df.org_lon > lon_low) & (df.org_lon < lon_high)]
    df = df[(df.des_lat > lat_low) & (df.des_lat < lat_high)]
    df = df[(df.des_lon > lon_low) & (df.des_lon < lon_high)]
    # 注意返回df，否则可能返回为筛选钱前的
    return df



def neareast_station(df):
    '''
    计算每个OD对离其起点和终点最近的站点，以及之间的距离、步行时间
    :param df: 筛选后OD对表格
    :return: 增加6列信息后输出表格
    '''
    print('筛选后的数据')
    print(df)
    # 读取站点的数据
    station = pd.read_excel('station.xls', sheet_name='Sheet1')
    for i in range(df.shape[0]):
        org_lon = df['org_lon'][i]
        org_lat = df['org_lat'][i]
        des_lon = df['des_lon'][i]
        des_lat = df['des_lat'][i]
        org_list = []   # 存储起点到站点的距离
        des_list = []   # 存储终点到站点的距离
        for s in range(station.shape[0]):
            sta_lon = station['lon'][s]
            sta_lat = station['lat'][s]
            # 起点到站点的距离，仍采用开车计算的距离
            org_sta = tl.dist(org_lat, org_lon, sta_lat, sta_lon)
            org_list.append(org_sta)
            # 终点到站点的距离
            des_sta = tl.dist(des_lat, des_lon, sta_lat, sta_lon)
            des_list.append(des_sta)
        # 起点——站点信息
        df.loc[i, 'org_sta'] = org_list.index(min(org_list)) + 1    # 距离最近站点所对应的index
        df.loc[i, 'org_dis'] = min(org_list)
        df.loc[i, 'org_time'] = int(min(org_list)/v_w)
        # 终点——站点信息
        df.loc[i, 'des_sta'] = des_list.index(min(des_list)) + 1
        df.loc[i, 'des_dis'] = min(des_list)
        df.loc[i, 'des_time'] = int(min(des_list) / v_w)



def add_csv(day_num):
    '''
    合并并筛选多个CSV文件中的OD数据
    :param day_num: 选取CSV文件的个数
    :return: 存储筛选后OD对的原始信息+处理的信息
    '''
    # 读取文件列表的全部名称
    csv_name_list = os.listdir('OD information')
    print('文件名称列表', csv_name_list)
    # 存储选中OD对信息的总表的表头
    col_names = ['id', 'time1', 'time2', 'org_lon', 'org_lat', 'des_lon', 'des_lat', 'newt1', 'newt2',
                 'distance', 'drive time', 'org_sta', 'org_dis', 'org_time', 'des_sta', 'des_dis', 'des_time']
    df = pd.DataFrame(columns=col_names)
    df.to_csv('AllODpairs.csv', index=False)
    # 循环遍历列表中各个CSV文件名，并完成文件拼接
    for i in range(0, day_num):
        df = pd.read_csv('OD information/' + csv_name_list[i], header=None)
        # 去掉原始信息最后一列
        df = df.drop([7], axis=1)
        df.columns = col_names[:7]    # 增加列名
        df['newt1'] = [0 for i in range(df.shape[0])]
        df['newt2'] = [0 for i in range(df.shape[0])]
        df['distance'] = [0 for i in range(df.shape[0])]
        # 将time1和time2 处理为一天内以秒为单位的时间格式，计算任意OD对起点和终点的之间距离
        for i in range(df.shape[0]):
            time1 = time.localtime(df['time1'][i])
            time2 = time.localtime(df['time2'][i])
            df.loc[i, 'newt1'] = int(time1.tm_hour) * 3600 + int(time1.tm_min) * 60 + int(time1.tm_sec)
            df.loc[i, 'newt2'] = int(time2.tm_hour) * 3600 + int(time2.tm_min) * 60 + int(time2.tm_sec)
            # 计算开车的距离，单位为米
            df.loc[i, 'distance'] = tl.dist(
                df['org_lat'][i], df['org_lon'][i], df['des_lat'][i], df['des_lon'][i]
            )
        # 根据一系列条件筛选合适的OD pairs
        print('初始OD数量', df.shape[0])
        new_df = select_od(df)     # 返回筛选后数据
        new_df = new_df.reset_index(drop=True)    # 重置index，否则索引会出错（保留了原始索引导致不连续）
        print('筛选后的OD数量', new_df.shape[0])
        # 计算开车所需的时间
        new_df['drive time'] = new_df['distance'] / v_c           # 开车时间，单位秒
        new_df['drive time'] = new_df['drive time'].astype(int)   # 保留为整数
        # 计算OD对起点、终点最近地铁站点的信息
        neareast_station(new_df)
        # 将一个文件里筛选符合条件的OD对信息存储在AllODpairs.csv中
        new_df.to_csv("AllODpairs.csv", index=False, header=False, mode='a+')




if __name__=="__main__":
    '''
    从多个CSV文件中筛选出早高峰7：30-9：30成都市内的出行OD对
    '''
    # 实验的全局参数
    peak_start = int(7) * 3600 + int(30) * 60 + int(0)    # 早高峰开始时间,一天内时间均转化为分钟为单位
    peak_end = int(9) * 3600 + int(30) * 60 + int(0)      # 早高峰结束时间
    # 提取成都的出行需求数据    103.781520,30.825130|104.455050,30.311340
    lon_low = 103.781520
    lat_low = 30.311340
    lon_high = 104.455050
    lat_high = 30.825130
    parameters = tl.Parameters()
    v_c = parameters.v_c      # 开车的速度，米/秒
    v_w = parameters.v_w       # 步行的速度，米/秒

    # 针对每天的OD对按照时间、位置进行筛选，并合并多个CSV文件
    day_num = 5      # 提取几天的OD数据
    add_csv(day_num)

    # 读取获取的表，添加新的索引列
    df_1 = pd.read_csv('AllODpairs.csv')
    df_1.insert(0, 'id num', [i for i in range(1, df_1.shape[0]+1)])
    df_1.to_csv("AllODpairs.csv", index=False, header=True)






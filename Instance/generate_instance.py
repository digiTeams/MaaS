import Tools as tl
import pandas as pd
import random
import math
from operator import itemgetter


# 将所有的乘客和司机分区存放
def region(riders_list, drivers_list):
    lon_low = 103.781520
    lat_low = 30.311340
    lon_high = 104.455050
    lat_high = 30.825130
    num_region = 10
    ave_lon = (lon_high - lon_low) / num_region
    ave_lat = (lat_high - lat_low) / num_region
    # 读取乘客和司机的信息
    rider = tl.DataReader().rider_reader('Data/rider.csv', riders_list)
    driver = tl.DataReader().driver_reader('Data/driver.csv', drivers_list)
    # 将所有的乘客和司机进行分区处理
    region_r = {}
    region_d = {}
    # 第一个索引表示经度所在位置，第二个索引表示纬度所在位置
    for i in range(1, num_region + 1):
        for j in range(1, num_region + 1):
            region_r[i, j] = []
            region_d[i, j] = []
    # 根据乘客的起点经纬度判断所在位置分区
    for i in rider.keys():
        lon_region = math.ceil((rider[i].org_lon - lon_low) / ave_lon)
        lat_region = math.ceil((rider[i].org_lat - lat_low) / ave_lat)
        region_r[lon_region, lat_region].append(i)
    # 根据司机的起点经纬度判断所在位置分区
    for j in driver.keys():
        lon_region = math.ceil((driver[j].org_lon - lon_low) / ave_lon)
        lat_region = math.ceil((driver[j].org_lat - lat_low) / ave_lat)
        region_d[lon_region, lat_region].append(j)
    return region_r, region_d

####### 分层抽样
def sample_instance():
    factors_df = pd.read_csv('factors_small.csv')
    # 分层抽取乘客和司机
    for i in range(factors_df.shape[0]):
        num_users = factors_df['num_users'][i]
        if factors_df['ratio'][i] == 'L':
            ratio = 2
        else:
            ratio = 3
        num_d = int(num_users / (1 + ratio))    # 司机的数量
        num_r = num_users - num_d               # 乘客的数量
        print('算例{}的用户数量为{}，乘客数量为{}，司机数量为{}'.format(i, num_users, num_r, num_d))
        print('ratio:', round(num_r/num_d))
        # 乘客分层抽样，从每个区域按比例抽取乘客
        ins_riders = []
        for (m, n) in region_r.keys():
            num = int(len(region_r[m,n]) / num_rider * num_r)
            if num != 0 and len(region_r[m, n]) != 0:
                choose_id = random.sample(region_r[m, n], num)
                ins_riders = ins_riders + choose_id
        remaining_num_r = num_r - len(ins_riders)     # 抽取之后由于取整原因，人数可能少了一点
        remaining_id_r = random.sample(list(set(riders_list) - set(ins_riders)), remaining_num_r)
        ins_riders = ins_riders + remaining_id_r
        # 司机分层抽样
        ins_drivers = []
        for (m, n) in region_d.keys():
            num = int(len(region_d[m, n]) / num_driver * num_d)
            if num != 0 and len(region_d[m, n]) != 0:
                choose_id = random.sample(region_d[m, n], num)
                ins_drivers = ins_drivers + choose_id
        remaining_num_d = num_d - len(ins_drivers)
        remaining_id_d = random.sample(list(set(drivers_list) - set(ins_drivers)), remaining_num_d)
        ins_drivers = ins_drivers + remaining_id_d
        # 构造一个算例数组，存储为csv，每一行为编号，1表示该编号对应的乘客或司机存在此算例中
        all = []
        for j in range(num_rider):
            index = j + 1
            row = [index]
            if index in ins_riders:
                row.append(1)
            else:
                row.append(0)
            if index in ins_drivers:
                row.append(1)
            else:
                row.append(0)
            all.append(row)
        df = pd.DataFrame(all, columns=['id', 'rider', 'driver'])
        df.to_csv('instance_' + str(i + 1) + '.csv', index=False)

'''
def instance(a):
    # 总的乘客数量和司机数量
    parameters = tl.Parameters()
    num_rider = parameters.total_riders
    num_driver = parameters.total_drivers
    riders_list = range(1, num_rider + 1)  # 乘客编号集合
    drivers_list = range(1, num_driver + 1)  # 司机编号集合
    region_r, region_d = region(riders_list, drivers_list)

    factors_df = pd.read_csv('Instance/factors_medium.csv')
    # 分层抽取乘客和司机
    i = a - 1
    num_users = factors_df['num_users'][i]
    if factors_df['ratio'][i] == 'L':
        ratio = 2
    else:
        ratio = 3
    num_d = int(num_users / (1 + ratio))    # 司机的数量
    num_r = num_users - num_d               # 乘客的数量
    print('算例{}的用户数量为{}，乘客数量为{}，司机数量为{}'.format(i, num_users, num_r, num_d))
    print('ratio:', round(num_r/num_d))
    # 乘客分层抽样，从每个区域按比例抽取乘客
    ins_riders = []
    for (m, n) in region_r.keys():
        num = int(len(region_r[m,n]) / num_rider * num_r)
        if num != 0 and len(region_r[m, n]) != 0:
            choose_id = random.sample(region_r[m, n], num)
            ins_riders = ins_riders + choose_id
    remaining_num_r = num_r - len(ins_riders)     # 抽取之后由于取整原因，人数可能少了一点
    remaining_id_r = random.sample(list(set(riders_list) - set(ins_riders)), remaining_num_r)
    ins_riders = ins_riders + remaining_id_r
    # 司机分层抽样
    ins_drivers = []
    for (m, n) in region_d.keys():
        num = int(len(region_d[m, n]) / num_driver * num_d)
        if num != 0 and len(region_d[m, n]) != 0:
            choose_id = random.sample(region_d[m, n], num)
            ins_drivers = ins_drivers + choose_id
    remaining_num_d = num_d - len(ins_drivers)
    remaining_id_d = random.sample(list(set(drivers_list) - set(ins_drivers)), remaining_num_d)
    ins_drivers = ins_drivers + remaining_id_d
    # 构造一个算例数组，存储为csv，每一行为编号，1表示该编号对应的乘客或司机存在此算例中
    all = []
    for j in range(num_rider):
        index = j + 1
        row = [index]
        if index in ins_riders:
            row.append(1)
        else:
            row.append(0)
        if index in ins_drivers:
            row.append(1)
        else:
            row.append(0)
        all.append(row)
    df = pd.DataFrame(all, columns=['id', 'rider', 'driver'])
    df.to_csv('Instance/instance' + str(i + 16) + '.csv', index=False)
'''



def factors(num_instances, instance_list):
    all_ins = list(range(1, num_instances+1))
    ratio_index = random.sample(all_ins, int(num_instances*0.5))
    vot_index = random.sample(all_ins, int(num_instances*0.5))
    pick_index = random.sample(all_ins, int(num_instances*0.5))
    trip_index = random.sample(all_ins, int(num_instances*0.5))
    instance_para = []
    for i in range(1, num_instances+1):
        row = [i, instance_list[i-1]]
        if i in ratio_index:
            row.append('L')
        else:
            row.append('H')
        if i in vot_index:
            row.append('L')
        else:
            row.append('H')
        if i in pick_index:
            row.append('L')
        else:
            row.append('H')
        if i in trip_index:
            row.append('L')
        else:
            row.append('H')
        instance_para.append(row)
    df_para = pd.DataFrame(instance_para, columns=['instance', 'num_users', 'ratio', 'vot', 'pick', 'trip'])
    df_para.to_csv('factors_small.csv', index=False)




if __name__ == "__main__":
    lon_low = 103.781520
    lat_low = 30.311340
    lon_high = 104.455050
    lat_high = 30.825130
    num_region = 10
    ave_lon = (lon_high - lon_low) / num_region
    ave_lat = (lat_high - lat_low) / num_region
    # 总的乘客数量和司机数量
    parameters = tl.Parameters()
    num_rider = parameters.total_riders
    num_driver = parameters.total_drivers
    riders_list = range(1, num_rider + 1)  # 乘客编号集合
    drivers_list = range(1, num_driver + 1)  # 司机编号集合

    ##### 第一步，先确定用户数量
    instances_list = []
    for i in range(30):
        num = random.randint(1000, 5000)
        instances_list.append(num)
    instances_list.sort()
    print(instances_list)

    ##### 第二步，确定参数选择
    factors(len(instances_list), instances_list)

    # 将所有乘客和司机根据地理位置进行分区
    region_r, region_d = region(riders_list, drivers_list)
    sample_instance()




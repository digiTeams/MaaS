import pandas as pd
import numpy as np
import Tools as tl
from main import instance_factor


############################# 计算大规模算例相关的结果
'''
table = pd.read_csv('Results/approximate/instance_31sr.csv')
r_instance = []
d_instance = []
instance_df = pd.read_csv('Instance/instance31.csv')
for i in range(instance_df.shape[0]):
    if instance_df['rider'][i] == 1:
        r_instance.append(instance_df['id'][i])
    if instance_df['driver'][i] == 1:
        d_instance.append(instance_df['id'][i])
########### 读取乘客、司机、站点、道路网络相关的数据
rider = tl.DataReader().rider_reader('Data/rider.csv', r_instance)
driver = tl.DataReader().driver_reader('Data/driver.csv', d_instance)

d_detour, r_detour = [], []
d_cost, r_cost = [], []
d_utility, r_utility = [], []

for a in range(table.shape[0]):
    j = table['driver'][a]
    d_detour.append(table['detour_d'][a]/driver[j].alone_time*100)
    d_cost.append((1 - table['cost_d'][a]/driver[j].alone_cost)*100)
    d_utility.append(table['save_d'][a])
    for i_index in [1, 2, 3]:
        r = table['rider' + str(i_index)][a]
        if r != 0:
            r_time = table['detour_r'+str(i_index)][a]/rider[r].alone_time*100
            if table['type'][a] == 'SR':
                if r_time > 0:
                    r_detour.append(r_time)
                else:
                    r_detour.append(0)
            else:
                r_detour.append(r_time)
            r_cost.append((1 - table['cost_r'+str(i_index)][a]/rider[r].alone_cost)*100)
            r_utility.append(table['save_r'+str(i_index)][a])
print(d_detour)
print(d_cost)
print(d_utility)
print(r_detour)
print(r_cost)
print(r_utility)

print(round(np.average(np.array(r_detour)), 2))
print(round(np.average((np.array(r_cost))), 2))
print(round(np.average(np.array(r_utility)), 2))
print(round(np.average(np.array(d_detour)), 2))
print(round(np.average(np.array(d_cost)), 2))
print(round(np.average(np.array(d_utility)), 2))
'''



###################### 计算每个算例乘客和司机的广义成本平均值
'''
instance_list = list(range(16, 31))
factors = pd.read_csv('Instance/factors_small.csv')
parameters = tl.Parameters()
rider_gencost, driver_gencost = [], []
for a in instance_list:
    information, r_ins, d_ins = tl.instance_preprocess(a, parameters, 'Instance/instance' + str(a) + '.csv')
    alpha, flex_pick, flex_trip_r, flex_trip_d = instance_factor(a, factors)
    # 根据灵敏参数计算对应的广义成本和时间窗约束
    information.compute_gencost(alpha)
    information.compute_time(flex_pick, parameters.flex_trip_max, flex_trip_r, flex_trip_d)
    r_l, d_l = [], []
    for i in information.rider.keys():
        r_l.append(information.rider[i].gencost)
    for j in information.driver.keys():
        d_l.append(information.driver[j].gencost)
    # print(r_l)
    # print(d_l)
    rider_gencost.append(round(np.average(np.array(r_l)), 2))
    driver_gencost.append(round(np.average(np.array(d_l)), 2))
print(rider_gencost)
print(driver_gencost)
row_r = 'rider: '
for r in rider_gencost:
    row_r += str(r) + ' & '
row_d = 'driver: '
for d in driver_gencost:
    row_d +=  str(d) + ' & '
print(row_r)
print(row_d)
'''



######################## 生成大规模算例的用户数据表users.csv
res = []
r_instance = []
d_instance = []
instance_df = pd.read_csv('Instance/instance' + str(31) + '.csv')
for i in range(instance_df.shape[0]):
    if instance_df['rider'][i] == 1:
        r_instance.append(instance_df['id'][i])
    if instance_df['driver'][i] == 1:
        d_instance.append(instance_df['id'][i])
########### 读取乘客、司机、站点、道路网络相关的数据
rider = tl.DataReader().rider_reader('Data/rider.csv', r_instance)
driver = tl.DataReader().driver_reader('Data/driver.csv', d_instance)
id = 0
for i in rider.keys():
    id += 1
    type_SR, type_RT, type_TR = tl.type_rider(rider, 1000)
    if i in type_RT:
        r_type = 2
    elif i in type_TR:
        r_type = 3
    elif i in type_SR:
        r_type = 4
    else:
        r_type = 1
    row = [id, i, 'R', rider[i].org_lon, rider[i].org_lat, rider[i].des_lon, rider[i].des_lat, r_type,
           rider[i].alone_time/60, rider[i].alone_cost]
    res.append(row)
for j in driver.keys():
    id += 1
    row = [id, j, 'D', driver[j].org_lon, driver[j].org_lat, driver[j].des_lon, driver[j].des_lat, 0,
           driver[j].alone_time/60, driver[j].alone_cost]
    res.append(row)
res_df = pd.DataFrame(res, columns=['num', 'ID', 'role', 'org_lon',	'org_lat', 'des_lon',
                                    'des_lat', 'rider_type', 'duration', 'cost'])
res_df.to_csv('users.csv', index=False)



######################## 比较近似稳定匹配结果和集中式匹配的时间、成本差异
'''
instances_list = list(range(1, 31))
res_np =  []
for a in instances_list:
    r_instance = []
    d_instance = []
    instance_df = pd.read_csv('Instance/instance' + str(a) + '.csv')
    for i in range(instance_df.shape[0]):
        if instance_df['rider'][i] == 1:
            r_instance.append(instance_df['id'][i])
        if instance_df['driver'][i] == 1:
            d_instance.append(instance_df['id'][i])
    ########### 读取乘客、司机、站点、道路网络相关的数据
    rider = tl.DataReader().rider_reader('Data/rider.csv', r_instance)
    driver = tl.DataReader().driver_reader('Data/driver.csv', d_instance)

    row = [a]
    for method in ['approximate', 'centralized']:
        df_match =pd.read_csv('Results/' + method + '/instance_' + str(a) + '.csv')
        d_time, d_trip, d_detour, d_alone, d_cost, d_savings, d_vmt = [], [], [], [], [], [], []
        r_time, r_trip, r_detour, r_alone, r_cost, r_savings, r_vmt = [], [], [], [], [], [], []
        for k in range(df_match.shape[0]):
            d_time.append(driver[df_match.driver[k]].alone_time)
            d_trip.append(df_match.T_d[k])
            d_detour.append(df_match.detour_d[k])
            d_alone.append(driver[df_match.driver[k]].alone_cost)
            d_cost.append(df_match.cost_d[k])
            d_savings.append(driver[df_match.driver[k]].alone_cost - df_match.cost_d[k])
            d_vmt.append(df_match.save_d[k])
            for i in [1, 2, 3]:      # 对于每个乘客而言
                r = df_match['rider'+str(i)][k]
                if r != 0:
                    r_time.append(rider[r].alone_time)
                    r_trip.append(df_match['T_r'+str(i)][k])
                    r_detour.append(df_match['detour_r'+str(i)][k])
                    r_alone.append(rider[r].alone_cost)
                    r_cost.append(df_match['cost_r'+str(i)][k])
                    r_savings.append(rider[r].alone_cost - df_match['cost_r'+str(i)][k])
                    r_vmt.append(df_match['save_r'+str(i)][k])
        res = [np.average(np.array(d_time)), np.average(np.array(d_trip)), np.average(np.array(d_detour)), np.average(np.array(d_alone)),
               np.average(np.array(d_cost)), np.average(np.array(d_savings)), np.average(np.array(d_vmt)),
               np.average(np.array(r_time)), np.average(np.array(r_trip)), np.average(np.array(r_detour)), np.average(np.array(r_alone)),
               np.average(np.array(r_cost)), np.average(np.array(r_savings)), np.average(np.array(r_vmt))]
        row += res
    res_np.append(row)
res_df = pd.DataFrame(res_np, columns=['ID', 'appr_d_time', 'appr_d_trip', 'appr_d_detour', 'appr_d_alone', 'appr_d_cost', 'appr_d_savings', 'appr_d_vmt',
                                       'appr_r_time', 'appr_r_trip', 'appr_r_detour', 'appr_r_alone', 'appr_r_cost', 'appr_r_savings', 'appr_r_vmt',
                                       'cen_d_time', 'cen_d_trip', 'cen_d_detour', 'cen_d_alone', 'cen_d_cost', 'cen_d_savings', 'cen_d_vmt',
                                       'cen_r_time', 'cen_r_trip', 'cen_r_detour', 'cen_r_aolne', 'cen_r_cost', 'cen_r_savings', 'cen_r_vmt'])
res_df.to_csv('compare_welfare.csv', index=False)
'''
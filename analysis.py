import pandas as pd
import numpy as np
import Tools as tl



############################# 计算大规模算例相关的结果
### 计算乘客和司机的绕路、广义成本节约情况

parameters = tl.Parameters()
factors = pd.read_csv('Instance/factors_large.csv')
instance_index = 31
information, r_ins, d_ins = tl.instance_preprocess(instance_index, parameters, 'Instance/instance' + str(instance_index) + '.csv')
alpha, flex_pick, flex_trip_r, flex_trip_d = tl.instance_factor(instance_index-30, factors)
# 根据灵敏参数计算对应的广义成本和时间窗约束
information.compute_gencost(alpha)
information.compute_time(flex_pick, parameters.flex_trip_max, flex_trip_r, flex_trip_d)

#['31sr', '31maas', '31maas_60', '31maas_80', '31maas_120', '31maas_140']
for file in ['31sr_50', '31sr_150', '31sr_200']:
    # 读取匹配结果
    table = pd.read_csv('Results/approximate/instance_' + file + '.csv')
    d_detour, r_detour = [], []
    d_cost, r_cost = [], []
    d_utility, r_utility = [], []
    num_2, num_3, num_4 = 0, 0, 0
    for a in range(table.shape[0]):
        j = table['driver'][a]
        d_detour.append(table['detour_d'][a]/information.driver[j].alone_time*100)
        d_cost.append((1 - table['cost_d'][a]/information.driver[j].alone_cost)*100)
        d_utility.append(table['save_d'][a]/information.driver[j].gencost*100)
        for i_index in [1, 2, 3]:
            r = table['rider' + str(i_index)][a]
            if r != 0:
                r_time = table['detour_r'+str(i_index)][a]/information.rider[r].alone_time*100
                if table['type'][a] == 'SR':
                    if r_time > 0:
                        r_detour.append(r_time)
                    else:
                        r_detour.append(0)
                else:
                    r_detour.append(r_time)
                r_cost.append((1 - table['cost_r'+str(i_index)][a]/information.rider[r].alone_cost)*100)
                r_utility.append(table['save_r'+str(i_index)][a]/information.rider[r].gencost*100)
                if r in information.type_RT:
                    num_2 +=1
                elif r in information.type_TR:
                    num_3 += 1
                elif r in information.type_SR:
                    num_4 += 1
    print(file + ': ', round(np.average(np.array(r_detour)), 2), round(np.std(np.array(r_detour)), 2),
          round(np.average(np.array(r_utility)), 2), round(np.std(np.array(r_utility)), 2),
          round(np.average(np.array(d_detour)), 2), round(np.std(np.array(d_detour)), 2),
          round(np.average(np.array(d_utility)), 2), round(np.std(np.array(d_utility)), 2),
          num_2, num_3, num_4)








######################## 计算每个算例匹配乘客、司机的平均绕路和平均光义成本节约
'''
parameters = tl.Parameters()
factors = pd.read_csv('Instance/factors_small.csv')
instance_list = list(range(1, 31))     # {5, 9, 11, 14, 15, 16, 21, 22, 24, 26, 29}
rss_list = [5, 9, 11, 14, 15, 16, 21, 22, 24, 26, 29]
res = []
for aa in instance_list:
    information, r_ins, d_ins = tl.instance_preprocess(aa, parameters, 'Instance/instance' + str(aa) + '.csv')
    alpha, flex_pick, flex_trip_r, flex_trip_d = tl.instance_factor(aa, factors)
    # 根据灵敏参数计算对应的广义成本和时间窗约束
    information.compute_gencost(alpha)
    information.compute_time(flex_pick, parameters.flex_trip_max, flex_trip_r, flex_trip_d)

    # 读取匹配结果
    if aa in rss_list:
        table = pd.read_csv('Results/approximate/instance_' + str(aa) + '.csv')
    else:
        table = pd.read_csv('Results/exact/instance_' + str(aa) + '.csv')
    d_detour, r_detour = [], []
    d_utility, r_utility = [], []
    for a in range(table.shape[0]):
        j = table['driver'][a]
        d_detour.append(table['detour_d'][a]/information.driver[j].alone_time*100)
        d_utility.append(table['save_d'][a]/information.driver[j].gencost*100)
        for i_index in [1, 2, 3]:
            r = table['rider' + str(i_index)][a]
            if r != 0:
                r_time = table['detour_r'+str(i_index)][a]/information.rider[r].alone_time*100
                if table['type'][a] == 'SR':
                    if r_time > 0:
                        r_detour.append(r_time)
                    else:
                        r_detour.append(0)
                else:
                    r_detour.append(r_time)
                r_utility.append(table['save_r'+str(i_index)][a]/information.rider[r].gencost*100)
    res.append([aa, round(np.average(np.array(r_detour)), 2), round(np.average(np.array(d_detour)), 2),
                round(np.average(np.array(r_utility)), 2), round(np.average(np.array(d_utility)), 2)])
for i in res:
    print(i)
res_df = pd.DataFrame(res, columns=['instance', 'r_detour', 'd_detour', 'r_saves', 'd_saves'])
res_df.to_csv('detour_welfare.csv', index=False)
'''






#################### 计算SR匹配和XT匹配中的乘客数量
'''
table = pd.read_csv('Results/approximate/instance_31maas.csv')
num_xt = 0
num_riders_xt = 0
num_sr = 0
for a in range(table.shape[0]):
    if table['type'][a] != 'SR':
        num_xt += 1
        for i_index in [1, 2, 3]:
            r = table['rider' + str(i_index)][a]
            if r != 0:
                num_riders_xt += 1
    else:
        for i_index in [1, 2, 3]:
            r = table['rider' + str(i_index)][a]
            if r != 0:
                num_sr += 1
print(num_xt, num_riders_xt, num_sr)
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


#################### 输出各个算例的灵敏性参数选择
'''
factors = pd.read_csv('Instance/factors_small.csv')
epsilon_pick, epsilon_driver, epsilon_rider, alpha = [], [], [], []
for i in list(range(16, 31)):
    vot = factors['vot'][i-1]
    pick = factors['pick'][i-1]
    trip = factors['trip'][i-1]
    if vot == 'H':
        alpha.append(30)
    else:
        alpha.append(15)
    if pick == 'H':
        epsilon_pick.append(20)
    else:
        epsilon_pick.append(10)
    if trip == 'H':
        epsilon_driver.append(30)
        epsilon_rider.append(60)
    else:
        epsilon_driver.append(20)
        epsilon_rider.append(40)
l = [epsilon_pick, epsilon_driver, epsilon_rider, alpha]
for index in l:
    str_print = str(index) + ':'
    for aa in index:
        str_print += str(aa) + ' & '
    print(str_print)
'''






######################## 生成大规模算例的用户数据表users.csv
'''
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
'''





######################## 比较近似稳定匹配结果和集中式匹配的时间、成本差异
'''
instances_list = list(range(1, 31))
res_np = []
factors = pd.read_csv('Instance/factors_small.csv')
parameters = tl.Parameters()
for a in instances_list:
    information, r_ins, d_ins = tl.instance_preprocess(a, parameters, 'Instance/instance' + str(a) + '.csv')
    alpha, flex_pick, flex_trip_r, flex_trip_d = tl.instance_factor(a, factors)
    # 根据灵敏参数计算对应的广义成本和时间窗约束
    information.compute_gencost(alpha)
    information.compute_time(flex_pick, parameters.flex_trip_max, flex_trip_r, flex_trip_d)

    ########### 读取乘客、司机、站点、道路网络相关的数据
    rider = information.rider
    driver = information.driver

    row = [a]
    for method in ['approximate', 'centralized', 'exact']:
        df_match =pd.read_csv('Results/' + method + '/instance_' + str(a) + '.csv')
        d_time, d_trip, d_detour, d_alone, d_cost, d_savings, d_vmt, d_gencost0, d_bnf = [], [], [], [], [], [], [], [], []
        r_time, r_trip, r_detour, r_alone, r_cost, r_savings, r_vmt, r_gencost0, r_bnf = [], [], [], [], [], [], [], [], []
        for k in range(df_match.shape[0]):
            d_time.append(driver[df_match.driver[k]].alone_time)
            d_trip.append(df_match.T_d[k])
            d_detour.append(df_match.detour_d[k]/driver[df_match.driver[k]].alone_time)
            d_alone.append(driver[df_match.driver[k]].alone_cost)
            d_cost.append(df_match.cost_d[k])
            d_savings.append(driver[df_match.driver[k]].alone_cost - df_match.cost_d[k])
            d_vmt.append(df_match.save_d[k])
            d_gencost0.append(driver[df_match.driver[k]].gencost)
            d_bnf.append(df_match.save_d[k] / driver[df_match.driver[k]].gencost)
            for i in [1, 2, 3]:      # 对于每个乘客而言
                r = df_match['rider'+str(i)][k]
                if r != 0:
                    r_time.append(rider[r].alone_time)
                    r_trip.append(df_match['T_r'+str(i)][k])
                    r_detour.append(df_match['detour_r'+str(i)][k]/rider[r].alone_time)
                    r_alone.append(rider[r].alone_cost)
                    r_cost.append(df_match['cost_r'+str(i)][k])
                    r_savings.append(rider[r].alone_cost - df_match['cost_r'+str(i)][k])
                    r_vmt.append(df_match['save_r'+str(i)][k])
                    r_gencost0.append(rider[r].gencost)
                    r_bnf.append(df_match['save_r'+str(i)][k] / rider[r].gencost)
        if len(d_time) > 0:
            res = [np.average(np.array(d_time)), np.average(np.array(d_trip)), np.average(np.array(d_detour)), np.average(np.array(d_alone)),
                   np.average(np.array(d_cost)), np.average(np.array(d_savings)), np.average(np.array(d_vmt)), np.average(np.array(d_gencost0)), np.average(np.array(d_bnf)),
                   np.average(np.array(r_time)), np.average(np.array(r_trip)), np.average(np.array(r_detour)), np.average(np.array(r_alone)),
                   np.average(np.array(r_cost)), np.average(np.array(r_savings)), np.average(np.array(r_vmt)), np.average(np.array(r_gencost0)), np.average(np.array(r_bnf))]

        else:
            res = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        row += res
    res_np.append(row)
res_df = pd.DataFrame(res_np, columns=['ID', 'appr_d_time', 'appr_d_trip', 'appr_d_detour', 'appr_d_alone', 'appr_d_cost', 'appr_d_savings', 'appr_d_vmt', 'appr_d_gencost0', 'appr_d_bnf',
                                       'appr_r_time', 'appr_r_trip', 'appr_r_detour', 'appr_r_alone', 'appr_r_cost', 'appr_r_savings', 'appr_r_vmt', 'appr_r_gencost0', 'appr_r_bnf',
                                       'cen_d_time', 'cen_d_trip', 'cen_d_detour', 'cen_d_alone', 'cen_d_cost', 'cen_d_savings', 'cen_d_vmt', 'cen_d_gencost0', 'cen_d_bnf',
                                       'cen_r_time', 'cen_r_trip', 'cen_r_detour', 'cen_r_aolne', 'cen_r_cost', 'cen_r_savings', 'cen_r_vmt', 'cen_r_gencost0', 'cen_r_bnf',
                                       'exa_d_time', 'exa_d_trip', 'exa_d_detour', 'exa_d_alone', 'exa_d_cost', 'exa_d_savings', 'exa_d_vmt', 'exa_d_gencost0', 'exa_d_bnf',
                                       'exa_r_time', 'exa_r_trip', 'exa_r_detour', 'exar_aolne', 'exa_r_cost', 'exa_r_savings', 'exa_r_vmt', 'exa_r_gencost0', 'exa_r_bnf'])
res_df.to_csv('compare_welfare.csv', index=False)
'''



################ Significance of stability部分总结两个情境下的结果
'''
appr_np = []
dyn_np = []

col_name = []
instance_list = list(range(1, 16))
for a in instance_list:
    dynamic_pd = pd.read_csv('Results/dynamic/instance'+str(a)+'.csv')
    appr_np.append(dynamic_pd['prt_appr'])
    dyn_np.append(dynamic_pd['prt_dyn'])
    col_name.append('instance'+str(a))
appr_array = np.transpose(np.array(appr_np))
dyn_array = np.transpose(np.array(dyn_np))
appr_df = pd.DataFrame(appr_array, columns=col_name)
appr_df.to_csv('dynamic_appr.csv', index=False)
dyn_df = pd.DataFrame(dyn_array, columns=col_name)
dyn_df.to_csv('dynamic_dyn.csv', index=False)
'''




################## 计算RSS matchings对应的平台收入
'''
result_np = []
instance_list = list(range(1, 31))
for a in instance_list:
    res_df = pd.read_csv('Results/exact/instance_' + str(a) + '.csv')
    res_df['revenue'] = res_df.VMT - res_df.save_d - res_df.save_r1 - res_df.save_r2 - res_df.save_r3
    total_revenue = res_df['revenue'].sum()
    total_vmt = res_df['VMT'].sum()
    result_np.append([a, round(total_revenue, 2), total_vmt])
result_df = pd.DataFrame(result_np, columns=['instance', 'revenue', 'obj'])
result_df.to_csv('revenue.csv', index=False)
'''



# 计算BFS算法确定的approximate stable matching 需要的补贴值
# 读取每个算例得到匹配结果，然后重新获取全部可行匹配，判断阻塞匹配，然后计算补贴值
'''
import Matching as mtg

instance_list = [31]
factors = pd.read_csv('Instance/factors_large.csv')
parameters = tl.Parameters()
price_scaling = 1.0
subsidy_np = []
for a in instance_list:
    print('------------------算例{}的实验结果-------------------'.format(a))
    # 读取算例a中的相应的信息，并进行预处理，返回信息参数对象、乘客列表、司机列表
    information, r_ins, d_ins = tl.instance_preprocess(a, parameters, 'Instance/instance' + str(a) + '.csv')
    alpha, flex_pick, flex_trip_r, flex_trip_d = tl.instance_factor(a-30, factors)
    # 根据灵敏参数计算对应的广义成本和时间窗约束
    information.compute_gencost(alpha)
    information.compute_time(flex_pick, parameters.flex_trip_max, flex_trip_r, flex_trip_d)

    ################ 首先找到所有的可行匹配并对所有的可行匹配进行预处理
    Feasible_match = mtg.Find_All_Matches(information, r_ins, d_ins, price_scaling)
    matchings, mat_list = Feasible_match.find_all_matches()
    pre_r, pre_d, rins_new, dins_new = Feasible_match.preference_sort(matchings, mat_list)
    print('可行匹配数量为{}'.format(len(mat_list)))

    res_df = pd.read_csv('Results/approximate/instance_' + str(a) + 'maas.csv')
    pi_r = {i: 0 for i in r_ins}
    pi_d = {j: 0 for j in d_ins}
    for index in range(res_df.shape[0]):
        pi_d[res_df.driver[index]] = res_df.save_d[index]
        for i in [1, 2, 3]:
            if res_df['rider'+str(i)][index] > 0:
                pi_r[res_df['rider'+str(i)][index]] = res_df['save_r'+str(i)][index]

    # 确定阻塞对
    block_pair, block_r, block_d = [], [], []
    for (s, j, i1, i2, i3) in mat_list:
        isunstable = False
        if pre_d[j]['mat'][s, j, i1, i2, i3] > pi_d[j]:
            isunstable = True
            for i in ({i1, i2, i3} - {0}):
                if pre_r[i]['mat'][s, j, i1, i2, i3] <= pi_r[i]:
                    isunstable = False
                    break
        if isunstable:
            block_pair.append((s, j, i1, i2, i3))
            block_d.append(j)
            for i in {i1, i2, i3} - {0}:
                block_r.append(i)
    print('算例{}：阻塞对{}个，阻塞乘客{}个，阻塞司机{}个'.format(a, len(block_pair), len(block_r), len(block_d)))

    # 计算补贴值
    subsidy_r = {i: 0 for i in block_r}
    subsidy_d = {j: 0 for j in block_d}
    for (s, j, i1, i2, i3) in block_pair:
        gap_d = pre_d[j]['mat'][s, j, i1, i2, i3] - pi_d[j]
        if gap_d > subsidy_d[j]:
            subsidy_d[j] = gap_d
        for i in {i1, i2, i3} - {0}:
            gap_r = pre_r[i]['mat'][s, j, i1, i2, i3] - pi_r[i]
            if gap_r > subsidy_r[i]:
                subsidy_r[i] = gap_r
    total_subsidy = 0
    for i in subsidy_r.keys():
        total_subsidy += subsidy_r[i]
    for j in subsidy_d.keys():
        total_subsidy += subsidy_d[j]
    print('总的补贴值为{}元'.format(total_subsidy))
    subsidy_np.append([a, len(block_pair), len(block_r), len(block_d), total_subsidy])
    print(subsidy_r)
    print(subsidy_d)
subsidy_df = pd.DataFrame(subsidy_np, columns=['istance', 'broken',	'broken_r',	'broken_d', 'subsidy'])
subsidy_df.to_csv('subsidy_large.csv', index=False)
'''


'''
##############################
#### 计算动态实验中，每一天所有算例结果的平均值和标准差
import math
df = pd.read_csv('Results/dynamic.csv')
res = []
for tt in range(1, 31):
    set_df = df[df['day']==tt].copy()

    appr_ave = np.average(set_df['prt_appr'])
    appr_std = np.std(set_df['prt_appr'])
    appr_upper = appr_ave + 1.96 * appr_std / math.sqrt(15)
    appr_lower = appr_ave - 1.96 * appr_std / math.sqrt(15)

    dyn_ave = np.average(set_df['prt_dyn'])
    dyn_std = np.std(set_df['prt_dyn'])
    dyn_upper = dyn_ave + 1.96 * dyn_std / math.sqrt(15)
    dyn_lower = dyn_ave - 1.96 * dyn_std / math.sqrt(15)

    set_df['remain_appr'] = (set_df['appr_remain_r'] + set_df['appr_remain_d'])/(set_df['num_r'] + set_df['num_d'])*100
    set_df['remain_dyn'] = (set_df['cen_remain_r'] + set_df['cen_remain_d']) / (set_df['num_r'] + set_df['num_d']) * 100

    appr_remain_ave = np.average(set_df['remain_appr'])
    appr_remain_std = np.std(set_df['remain_appr'])
    appr_remain_upper = appr_remain_ave + 1.96 * appr_remain_std / math.sqrt(15)
    appr_remain_lower = appr_remain_ave - 1.96 * appr_remain_std / math.sqrt(15)

    dyn_remain_ave = np.average(set_df['remain_dyn'])
    dyn_remain_std = np.std(set_df['remain_dyn'])
    dyn_remain_upper = dyn_remain_ave + 1.96 * dyn_remain_std / math.sqrt(15)
    dyn_remain_lower = dyn_remain_ave - 1.96 * dyn_remain_std / math.sqrt(15)

    res.append([tt, appr_ave, appr_std, appr_upper, appr_lower,
                dyn_ave, dyn_std, dyn_upper, dyn_lower,
                appr_remain_ave, appr_remain_std, appr_remain_upper, appr_remain_lower,
                dyn_remain_ave, dyn_remain_std, dyn_remain_upper, dyn_remain_lower])

    col_name = ['day', 'appr_ave', 'appr_std', 'appr_upper', 'appr_lower',
                'dyn_ave', 'dyn_std', 'dyn_upper', 'dyn_lower',
                'appr_remain_ave', 'appr_remain_std', 'appr_remain_upper', 'appr_remain_lower',
                'dyn_remain_ave', 'dyn_remain_std', 'dyn_remain_upper', 'dyn_remain_lower']
    res_df = pd.DataFrame(res, columns=col_name)
    res_df.to_csv('dynamic_summary.csv', index=False)
'''








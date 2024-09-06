import math
import time
from gurobipy import *


'''======求解最优稳定性匹配结果======'''
def optimal_stable(matchings, mat_list, r_ins, d_ins, pre_r, pre_d):
    s_1 = time.time()
    # 建立自变量索引
    xindex = {}
    for (s, j, i1, i2, i3) in mat_list:
        xindex[s, j, i1, i2, i3] = matchings[s][s, j, i1, i2, i3]['wel']
    # 建立模型
    model = Model('optimal stable matching problem')
    # 设置不显示求解的log日志信息
    model.setParam('OutputFlag', 0)
    x = model.addVars(xindex.keys(), vtype=GRB.BINARY, name='x')  # 自变量
    model.setObjective(x.prod(xindex), GRB.MAXIMIZE)  # 目标函数
    ###### 约束条件
    # 对于每个司机而言，只能选择一个匹配
    for j in d_ins:
        model.addConstr(x.sum('*', j, '*', '*', '*') <= 1, name='driver_{}'.format(j))
    # 对于每个乘客而言，只能选择一个匹配
    for i in r_ins:
        model.addConstr(
            x.sum('*', '*', i, '*', '*') + x.sum('*', '*', '*', i, '*') + x.sum('*', '*', '*', '*', i) <= 1,
            name='rider_{}'.format(i)
        )
    # 稳定匹配约束
    for (s, j, i1, i2, i3) in xindex.keys():
        left = 0
        pre_l = set()     # 首先找到比该匹配更偏好的其他匹配，数据形式设为集合可以减少去重的时间
        for (key, save) in pre_d[j]['sort']:
            if save >= pre_d[j]['mat'][s, j, i1, i2, i3]:
                pre_l.add(key)
            else:
                break
        for i in ({i1, i2, i3} - {0}):
            for (key, save) in pre_r[i]['sort']:
                if save >= pre_r[i]['mat'][s, j, i1, i2, i3]:
                    pre_l.add(key)
                else:
                    break
        for key in pre_l:
            left += x[key]
        # 构建约束
        model.addConstr(left >= 1, name='match({},{},{},{},{})'.format(s, j, i1, i2, i3))
    e_1 = time.time()
    # 模型求解及解的输出处理
    s_2 = time.time()
    model.setParam('TimeLimit', 3600*4)     # 设置运行时间上限，单位为秒，总共4个小时
    model.optimize()
    e_2 = time.time()
    time_model = round((e_1 - s_1)/60, 4)
    time_optimize = round((e_2 - s_2) / 60, 4)
    # print('构造稳定性模型的时间为{}秒，求解稳定匹配问题的时间为{}秒'.format(round(e_1 - s_1, 2), round(e_2 - s_2, 2)))
    print('构造稳定性模型的时间为{}分钟，求解稳定匹配问题的时间为{}分钟'.format(time_model, time_optimize))
    optimal_result = []
    optimal_obj = 0
    gap = -1
    if model.status == 3:      # 说明原问题无解
        print('-----------------------该模型无稳定匹配结果-----------------------')
    else:
        opt_gap = model.MIPGap
        print('当前解的gap为{}'.format(opt_gap))
        if math.isinf(opt_gap):             # 说明规定时间内没找到一个可行解
            print('gap is infinite')
            gap = -2
        else:
            optimal_obj = model.ObjVal
            for key in xindex.keys():
                if x[key].x > 0:
                    optimal_result.append(key)
            gap = opt_gap
            print('稳定匹配结果为：目标函数值为{}，选中{}个匹配'.format(optimal_obj, len(optimal_result)))
    # 返回目标值
    return round(optimal_obj, 2), optimal_result, gap, time_model

def centralized_matching(matchings, mat_list, r_ins, d_ins):
    # 建立自变量索引
    xindex = {}
    for (s, j, i1, i2, i3) in mat_list:
        xindex[s, j, i1, i2, i3] = matchings[s][s, j, i1, i2, i3]['wel']
    # 建立模型
    model = Model('optimal centralized matching problem')
    # 设置不显示求解的log日志信息
    model.setParam('OutputFlag', 0)
    x = model.addVars(xindex.keys(), vtype=GRB.BINARY, name='x')  # 自变量
    model.setObjective(x.prod(xindex), GRB.MAXIMIZE)  # 目标函数
    ###### 约束条件
    # 对于每个司机而言，只能选择一个匹配
    for j in d_ins:
        model.addConstr(x.sum('*', j, '*', '*', '*') <= 1, name='driver_{}'.format(j))
    # 对于每个乘客而言，只能选择一个匹配
    for i in r_ins:
        model.addConstr(
            x.sum('*', '*', i, '*', '*') + x.sum('*', '*', '*', i, '*') + x.sum('*', '*', '*', '*', i) <= 1,
            name='rider_{}'.format(i)
        )
    model.optimize()
    cen_obj = model.ObjVal
    cen_result = []
    for key in xindex.keys():
        if x[key].x > 0:
            cen_result.append(key)
    print('稳定匹配结果为：目标函数值为{}，选中{}个匹配'.format(cen_obj, len(cen_result)))
    return round(cen_obj, 2), cen_result


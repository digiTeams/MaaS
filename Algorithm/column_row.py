from gurobipy import *
import time
from operator import itemgetter
import copy

class Column_Row:
    def __init__(self, r_ins, d_ins, matchings, mat_list, pre_r, pre_d):
        self.r_ins = r_ins
        self.d_ins = d_ins
        self.matchings = matchings
        self.mat_list = mat_list
        self.pre_r = pre_r
        self.pre_d = pre_d
    '''确定每个匹配更偏好的匹配集合，包含匹配自身'''
    def preference_list(self, s, j, i1, i2, i3):
        pre_l = set()
        for (key, save) in self.pre_d[j]['sort']:
            if save >= self.pre_d[j]['mat'][s, j, i1, i2, i3]:
                pre_l.add(key)
            else:
                break
        for i in ({i1, i2, i3} - {0}):
            for (key, save) in self.pre_r[i]['sort']:
                if save >= self.pre_r[i]['mat'][s, j, i1, i2, i3]:
                    pre_l.add(key)
                else:
                    break
        return list(pre_l)
    '''确定当前theta中的匹配包含的乘客集合和乘客'''
    def initialize(self, theta, pre_dict, xindex):
        # 找到每个司机最偏好的匹配作为初始集合，初始乘子为匹配对应的福利值
        for j in self.d_ins:
            most_pre = self.pre_d[j]['sort'][0][0]
            theta.append(most_pre)
            pre_dict[most_pre] = self.preference_list(
                most_pre[0], most_pre[1], most_pre[2], most_pre[3], most_pre[4]
            )
            xindex[most_pre] = self.matchings[most_pre[0]][most_pre]['wel']

    '''限制主问题，含有松弛变量'''
    def RMP_relaxed(self, theta, pre_dict, xindex):
        s_t = time.time()
        # 建立模型
        model = Model('RMP problem')
        # 设置不显示求解的log日志信息
        model.setParam('OutputFlag', 0)
        x = model.addVars(xindex.keys(), vtype=GRB.BINARY, name='x')  # 匹配对应的自变量
        alpha = model.addVars(xindex.keys(), vtype=GRB.BINARY, name='alpha')
        ### 不同目标函数
        # # 两层加权地目标函数，最小化阻塞对数量+最大化成本节约值
        # obj = x.prod(xindex)
        # M = -100
        # for key in xindex.keys():
        #     obj += M * alpha[key]
        # model.setObjective(obj, GRB.MAXIMIZE)

        # # 只考虑最小化阻塞对的数量，即M为-inf
        # obj = 0
        # for key in xindex.keys():
        #     obj += alpha[key]
        # model.setObjective(obj, GRB.MINIMIZE)

        # 只考虑最大化成本节约值，即M=0
        obj = x.prod(xindex)
        model.setObjective(obj, GRB.MAXIMIZE)

        ############ 约束条件
        for j in self.d_ins:
            model.addConstr(x.sum('*', j, '*', '*', '*') <= 1, name='driver_{}'.format(j))
        for i in self.r_ins:
            model.addConstr(
                x.sum('*', '*', i, '*', '*') + x.sum('*', '*', '*', i, '*') + x.sum('*', '*', '*', '*', i) <= 1,
                name='rider_{}'.format(i))
        for (s, j, i1, i2, i3) in theta:
            left = alpha[s, j, i1, i2, i3]
            for key in set(pre_dict[s, j, i1, i2, i3]) & set(theta):
                left += x[key]
            model.addConstr(left >= 1, name='match_{}'.format((s, j, i1, i2, i3)))
        ############ 模型求解及解的输出处理
        model.optimize()
        num_broken, mat_broken, result, pi_r, pi_d = 0, [], [], {}, {}
        obj = model.ObjVal
        for i in self.r_ins:
            pi_r[i] = 0
        for j in self.d_ins:
            pi_d[j] = 0
        for (s, j, i1, i2, i3) in xindex.keys():
            if x[s, j, i1, i2, i3].x > 0:
                result.append((s, j, i1, i2, i3))
                pi_d[j] = self.pre_d[j]['mat'][s, j, i1, i2, i3]
                for i in ({i1, i2, i3} - {0}):
                    pi_r[i] = self.pre_r[i]['mat'][s, j, i1, i2, i3]
            if alpha[s, j, i1, i2, i3].x > 0:
                num_broken += 1   # 松弛阻塞匹配的数量
                mat_broken.append((s, j, i1, i2, i3))    # 记录松弛匹配
        e_t = time.time()
        # print('求解限制性主问题需要{}秒, 需要松弛{}个稳定性约束'.format(round(e_t - s_t, 4), num_broken))
        return obj, result, pi_r, pi_d, num_broken, mat_broken

    '''限制主问题'''
    def RMP(self, theta, pre_dict, xindex):
        s_t = time.time()
        # 建立模型
        model = Model('RMP problem')
        # 设置不显示求解的log日志信息
        model.setParam('OutputFlag', 0)
        x = model.addVars(xindex.keys(), vtype=GRB.BINARY, name='x')  # 匹配对应的自变量
        ############ 目标函数值
        model.setObjective(x.prod(xindex), GRB.MAXIMIZE)
        ############ 约束条件
        for j in self.d_ins:
            model.addConstr(x.sum('*', j, '*', '*', '*') <= 1, name='driver_{}'.format(j))
        for i in self.r_ins:
            model.addConstr(
                x.sum('*', '*', i, '*', '*') + x.sum('*', '*', '*', i, '*') + x.sum('*', '*', '*', '*', i) <= 1,
                name='rider_{}'.format(i))
        for (s, j, i1, i2, i3) in theta:
            left = 0
            for key in set(pre_dict[s, j, i1, i2, i3]) & set(theta):
                left += x[key]
            model.addConstr(left >= 1, name='match_{}'.format((s, j, i1, i2, i3)))
        ############ 模型求解及解的输出处理
        model.optimize()
        obj, result, pi_r, pi_d = 0, [], {}, {}
        if model.status == 3:    # 无解
            # print('rmp： no solution')
            flag = False
        else:
            flag = True
            obj = model.ObjVal
            for i in self.r_ins:
                pi_r[i] = 0
            for j in self.d_ins:
                pi_d[j] = 0
            for (s, j, i1, i2, i3) in xindex.keys():
                if x[s, j, i1, i2, i3].x > 0:
                    result.append((s, j, i1, i2, i3))
                    pi_d[j] = self.pre_d[j]['mat'][s, j, i1, i2, i3]
                    for i in ({i1, i2, i3} - {0}):
                        pi_r[i] = self.pre_r[i]['mat'][s, j, i1, i2, i3]
        e_t = time.time()
        # print('求解限制性主问题需要{}秒'.format(round(e_t - s_t, 4)))
        return flag, obj, result, pi_r, pi_d

    '''当RMP问题无解时，求解该子问题确定是否可以加入新的列使得RMP问题有解'''
    def subrow(self, theta, pre_dict):
        s_t = time.time()
        sub_sol = []
        submodel = Model('subrow')
        # 自变量为所有的可行匹配
        z = submodel.addVars(self.mat_list, vtype=GRB.BINARY, name='z')
        # 目标函数为最小化加入新匹配的数量
        submodel.setObjective(
            quicksum(z[s, j, i1, i2, i3] for (s, j, i1, i2, i3) in (set(self.mat_list) - set(theta))),
            GRB.MINIMIZE)
        # 每个乘客只分配到一个匹配
        for i in self.r_ins:
            submodel.addConstr(
                z.sum('*', '*', i, '*', '*') + z.sum('*', '*', '*', i, '*') + z.sum('*', '*', '*', '*', i) <= 1,
                name='R_{}'.format(i))
        # 每个司机只分配一个匹配
        for j in self.d_ins:
            submodel.addConstr(z.sum('*', j, '*', '*', '*') <= 1, name='D_{}'.format(j))
        # theta中的每个匹配所对应的稳定性约束匹配
        for (s, j, i1, i2, i3) in theta:
            submodel.addConstr(
                quicksum(z[s_, j_, i1_, i2_, i3_] for (s_, j_, i1_, i2_, i3_) in pre_dict[s, j, i1, i2, i3]) >= 1,
                name='C_{}-{}-{}-{}-{}'.format(s, j, i1, i2, i3))
        submodel.setParam('OutputFlag', 0)
        s_2 = time.time()
        submodel.optimize()
        e_2 = time.time()
        if submodel.status == 3:
            print('判断稳定解是否存在的子问题无解，说明原MP问题无解')
        else:
            for (s, j, i1, i2, i3) in self.mat_list:
                if z[s, j, i1, i2, i3].x > 0 and (s, j, i1, i2, i3) not in theta:
                    sub_sol.append((s, j, i1, i2, i3))
        e_t = time.time()
        # print('求解subrow子问题总共需要{}秒，其中求解器求解需要{}秒，加入{}个新的匹配后使得RMP问题有解'.format(
        #     round(e_t - s_t, 4), round(e_2 - s_2, 2), len(sub_sol)))
        return sub_sol

    '''根据当前的匹配结果，通过求解器求解子问题寻找阻塞匹配'''
    def subproblem(self, theta, pi_r, pi_d):
        s_t = time.time()
        # 建立自变量索引
        anti_theta = set(self.mat_list) - set(theta)
        zindex = {}
        for (s, j, i1, i2, i3) in anti_theta:
            delta = self.pre_d[j]['mat'][s, j, i1, i2, i3] - pi_d[j]
            for i in ({i1, i2, i3} - {0}):
                delta += self.pre_r[i]['mat'][s, j, i1, i2, i3] - pi_r[i]
            zindex[s, j, i1, i2, i3] = delta
        # 构建子问题模型
        submodel = Model('subproblem for new columns')
        z = submodel.addVars(zindex, vtype=GRB.BINARY, name='z')
        submodel.setObjective(z.prod(zindex), GRB.MAXIMIZE)
        ###### 约束条件
        for j in self.d_ins:
            submodel.addConstr(z.sum('*', j, '*', '*', '*') <= 1, name='driver_{}'.format(j))
        for i in self.r_ins:
            submodel.addConstr(
                z.sum('*', '*', i, '*', '*') + z.sum('*', '*', '*', i, '*') + z.sum('*', '*', '*', '*', i) <= 1,
                name='rider_{}'.format(i)
            )
        alpha = 0.001
        for (s, j, i1, i2, i3) in zindex.keys():
            submodel.addConstr(z[s, j, i1, i2, i3] * (self.pre_d[j]['mat'][s, j, i1, i2, i3] - pi_d[j] - alpha) >= 0,
                               name='match_{}_D_{}'.format((s, j, i1, i2, i3), j))
            for i in ({i1, i2, i3} - {0}):
                submodel.addConstr(
                    z[s, j, i1, i2, i3] * (self.pre_r[i]['mat'][s, j, i1, i2, i3] - pi_r[i] - alpha) >= 0,
                    name='match_{}_R_{}'.format((s, j, i1, i2, i3), i))
        # 设置不显示求解日志
        submodel.setParam('OutputFlag', 0)
        submodel.optimize()
        sub_sol = []
        for (s, j, i1, i2, i3) in zindex.keys():
            if z[s, j, i1, i2, i3].x > 0:
                sub_sol.append((s, j, i1, i2, i3))
        e_t = time.time()
        # print('总共找到{}个新的匹配，求解器求解subproblem子问题需要{}秒'.format(len(sub_sol), round(e_t - s_t, 2)))
        return sub_sol

    '''基于给定匹配，找到所有的阻塞匹配'''
    def find_blocking(self, theta, pi_r, pi_d):
        anti_theta = set(self.mat_list) - set(theta)
        broken_mat, bl_matches = [], []
        # 首先判断那些匹配违反了稳定性约束
        for (s, j, i1, i2, i3) in anti_theta:
            isunstable = False
            if self.pre_d[j]['mat'][s, j, i1, i2, i3] > pi_d[j]:
                isunstable = True
                for i in ({i1, i2, i3} - {0}):
                    if self.pre_r[i]['mat'][s, j, i1, i2, i3] <= pi_r[i]:
                        isunstable = False
                        break
            if isunstable:
                delta = self.pre_d[j]['mat'][s, j, i1, i2, i3] - pi_d[j]
                for i in ({i1, i2, i3} - {0}):
                    delta += self.pre_r[i]['mat'][s, j, i1, i2, i3] - pi_r[i]
                broken_mat.append(((s, j, i1, i2, i3), delta))
                bl_matches.append((s, j, i1, i2, i3))
        return broken_mat, bl_matches

    '''利用贪婪算法求解子问题确定加入的阻塞匹配'''
    def greedy(self, theta, pi_r, pi_d):
        s_t = time.time()
        broken_mat, bl_matches = self.find_blocking(theta, pi_r, pi_d)
        # 然后根据贪婪规则确定加入的阻塞匹配
        broken_mat.sort(key=itemgetter(1), reverse=True)      # 首先按照阻塞匹配的系数从大到小排序
        sub_sol = []
        add_r, add_d = [], []
        for ((s, j, i1, i2, i3), aa) in broken_mat:
            if (j not in add_d) and len({i1, i2, i3} & set(add_r)) == 0:
                sub_sol.append((s, j, i1, i2, i3))
                add_d.append(j)
                for i in ({i1, i2, i3} - {0}):
                    add_r.append(i)
            if len(add_d) == len(self.d_ins) or len(add_r) == len(self.r_ins):    # 如果乘客后者司机都已经安排了一个匹配
                break
        e_t = time.time()
        # print('总共找到{}个新的匹配，贪婪方法求解subproblem子问题需要{}秒'.format(len(sub_sol), round(e_t - s_t, 2)))
        bro_r, bro_d = [], []
        for ((s, j, i1, i2, i3), aa) in broken_mat:
            if j not in bro_d:
                bro_d.append(j)
            for i in ({i1, i2, i3} - {0}):
                if i not in bro_r:
                    bro_r.append(i)
        # print('总共有{}个阻塞对，阻塞{}个乘客，{}个司机'.format(len(broken_mat), len(bro_r), len(bro_d)))
        return sub_sol, len(broken_mat), bl_matches


    '''========Feasible and blocking searching algorithm 主框架======='''
    def exact(self, method):
        s_t = time.time()
        flag = True
        iter, obj, sol, theta = 0, 0, [], []
        xindex = {}        # RMP问题自变量
        pre_dict = {}
        # 首先确定初始的theta集合
        self.initialize(theta, pre_dict, xindex)
        while flag:
            iter += 1
            # print('--------------第{}次迭代--------------'.format(iter))
            # 求解RMP问题
            rmp_flag, obj, sol, pi_r, pi_d = self.RMP(theta, pre_dict, xindex)
            # 如果RMP问题无可行解
            if rmp_flag == False:
                sub_sol = self.subrow(theta, pre_dict)
            else:     # 两种方法找阻塞匹配
                if method == 'exact':
                    sub_sol = self.subproblem(theta, pi_r, pi_d)
                else:
                    sub_sol, num_broken, mat_broken = self.greedy(theta, pi_r, pi_d)
            if len(sub_sol) != 0:
                theta = theta + sub_sol
                for (s, j, i1, i2, i3) in sub_sol:
                    xindex[s, j, i1, i2, i3] = self.matchings[s][s, j, i1, i2, i3]['wel']
                    pre_dict[s, j, i1, i2, i3] = self.preference_list(s, j, i1, i2, i3)
            else:
                flag = False
            e_t = time.time()
            if e_t - s_t >= 3600 * 4:      # 如果运行时间超过4个小时则直接停止运行
                obj, sol = 0, []
                break
        return obj, sol, iter, len(theta)

    '''========the relaxed blocking searching algorithm 主框架========='''
    def approximate(self, method):
        s_start = time.time()
        flag = True
        iter, num_bro, mat_bro = 0, 0, []
        sol = []
        xindex = {}        # RMP问题自变量
        theta = []
        pre_dict = {}
        # 首先确定初始的theta集合
        self.initialize(theta, pre_dict, xindex)
        while flag:
            iter += 1
            # print('--------------第{}次迭代--------------'.format(iter))
            # 求解RMP问题
            obj, sol, pi_r, pi_d, num_bro, mat_bro = self.RMP_relaxed(theta, pre_dict, xindex)
            # num_bro, mat_bro表示Θ内的阻塞匹配
            # 寻找阻塞对
            num_broken, mat_broken = 0, []      # Θ外的阻塞对数量
            if method == 'exact':
                sub_sol = self.subproblem(theta, pi_r, pi_d)
            else:
                sub_sol, num_broken, mat_broken = self.greedy(theta, pi_r, pi_d)
                # print('此时Θ之外还有{}个阻塞匹配'.format(num_broken))
            s_end = time.time()
            # 判断时间是否达到设置的停止时间
            if s_end - s_start < 3600:     # 如果没达到停止时间
                if len(sub_sol) != 0:   # 更新theta，并更新对应的RMP问题的自变量及构造稳定性约束需要的信息
                    theta = theta + sub_sol
                    for (s, j, i1, i2, i3) in sub_sol:
                        xindex[s, j, i1, i2, i3] = self.matchings[s][s, j, i1, i2, i3]['wel']
                        pre_dict[s, j, i1, i2, i3] = self.preference_list(s, j, i1, i2, i3)
                else:
                    print('当前总共有{}个阻塞匹配'.format(num_broken + num_bro))
                    flag = False
            else:     # 输出最后一次的解作为最终解
                num_bro += num_broken    # 此时整个系统内的阻塞对数量
                mat_bro += mat_broken
                print('到达时间限制，提前停止迭代')
                break     # 结束迭代
        obj = 0     # 计算最终匹配结果对应的VMT savings
        for key in sol:
            obj += xindex[key]
        return obj, sol, iter, num_bro, mat_bro, len(theta)



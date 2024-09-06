import itertools
import Matching as mtg
import copy
import Tools as tl
from operator import itemgetter
import time


# 找到所有站点的可行匹配
class Find_All_Matches:
    def __init__(self, inf, r_ins, d_ins):
        self.inf = inf
        self.station = inf.station
        self.rider = inf.rider
        self.driver = inf.driver
        self.r_ins = r_ins
        self.d_ins = d_ins
        self.max_riders = inf.parameters.max_riders       # 最多匹配的人数
        self.judge_feasibility = mtg.Feasible_Condition(inf)  # 判断可行匹配的条件
        self.type_RT = inf.type_RT
        self.type_TR = inf.type_TR
        self.rid_dri = inf.rid_dri
        self.rid_sta = inf.rid_sta
        self.dri_sta = inf.dri_sta
        self.v_c = inf.parameters.v_c
        self.max_stops = inf.parameters.max_stops
        self.dis_near = inf.parameters.dis_near
        self.vehicle_capacity = inf.parameters.vehicle_capacity

    '''#######记录一对一匹配的结果######'''
    def record_one(self, i, j, con_time, con, result_dic, mat_list, matchings, Iset, type, s):
        if con_time == True:
            Iset[j][1][type][i] = 0
        if con == True:
            matchings[s][s, j, i, 0, 0] = result_dic  # 关于该匹配的各项参数构成的字典
            mat_list.append((s, j, i, 0, 0))

    '''#######寻找一对一匹配######'''
    def find_one_match(self, mat_list, matchings, Iset, r_list, d_list, s):
        for j in d_list:
            d = self.driver[j]
            if s == 0:
                # 找到一对一SR匹配
                type = 'SR'
                for i in (set(r_list) & d.rider):
                    r = self.rider[i]
                    con_time, con, result_dic = self.judge_feasibility.feasible_one(i, j, s, r, d, type)
                    self.record_one(i, j, con_time, con, result_dic, mat_list, matchings, Iset, type, s)
            else:
                # 找到一对一RT匹配
                for i in (set(r_list) & d.rider & self.type_RT):
                    r = self.rider[i]
                    type = 'RT'
                    con_time, con, result_dic = self.judge_feasibility.feasible_one(i, j, s, r, d, type)
                    self.record_one(i, j, con_time, con, result_dic, mat_list, matchings, Iset, type, s)
                # 找到一对一TR匹配
                for i in (set(r_list) & d.rider & self.type_TR):
                    r = self.rider[i]
                    type = 'TR'
                    con_time, con, result_dic = self.judge_feasibility.feasible_one(i, j, s, r, d, type)
                    self.record_one(i, j, con_time, con, result_dic, mat_list, matchings, Iset, type, s)

    '''#######判断任意一个乘客子集是否是可行匹配#######'''
    def subfeas(self, I: list, p, j, Iset, type):
        z = True
        # 如果I中只包含一个乘客则无需判断
        if len(I) > 1:
            for i in I:
                new_I = list((set(I) - {i}) | {p})
                new_I.sort(reverse=True)      # 从大到小排序
                if tuple(new_I) not in Iset[j][len(I)][type].keys():
                    z = False
                    break
        return z

    '''#######根据贪婪规则确定一对多匹配的路径#######'''
    def greedy_route(self, I, j, s, type):
        route = []
        route_time = []
        index = 0
        if type == 'SR':
            omega = [i for i in I]  # 起点集合
            node_1 = j
            while len(omega) != 0:
                time_list = []
                for i in omega:
                    if index == 0:
                        time_12 = self.rid_dri[i, node_1].o_o
                    else:
                        if node_1 > 0 and i > 0:
                            time_12 = tl.car_time(self.rider[node_1].org_lat, self.rider[node_1].org_lon, self.rider[i].org_lat, self.rider[i].org_lon)
                        elif node_1 > 0 and i < 0:
                            time_12 = tl.car_time(self.rider[node_1].org_lat, self.rider[node_1].org_lon, self.rider[-i].des_lat, self.rider[-i].des_lon)
                        elif node_1 < 0 and i > 0:
                            time_12 = tl.car_time(self.rider[-node_1].des_lat, self.rider[-node_1].des_lon, self.rider[i].org_lat, self.rider[i].org_lon)
                        else:
                            time_12 = tl.car_time(self.rider[-node_1].des_lat, self.rider[-node_1].des_lon, self.rider[-i].des_lat, self.rider[-i].des_lon)
                    time_list.append((i, time_12))
                time_list.sort(key=itemgetter(1), reverse=False)     # 根据离得距离从近到远排序
                route.append(time_list[0][0])         # 选择最近的点
                route_time.append(time_list[0][1])
                node_1 = route[-1]                    # 更新点以便找下一个离得最近的点
                omega.remove(node_1)
                if node_1 > 0:
                    omega.append(-node_1)             # 确定一个乘客的起点后，才能加入该乘客的终点
                index += 1
        elif type == 'RT':
            omega = [i for i in I]
            node_1 = j
            while len(omega) != 0:
                time_list = []
                for i in omega:
                    if index == 0:
                        time_12 = self.rid_dri[i, node_1].o_o
                    else:
                        time_12 = tl.car_time(self.rider[node_1].org_lat, self.rider[node_1].org_lon, self.rider[i].org_lat, self.rider[i].org_lon)
                    time_list.append((i, time_12))
                time_list.sort(key=itemgetter(1), reverse=False)
                route.append(time_list[0][0])
                route_time.append(time_list[0][1])
                node_1 = route[-1]
                omega.remove(node_1)
                index += 1
        else:
            omega = [-i for i in I]
            node_1 = s
            while len(omega) != 0:
                time_list = []
                for i in omega:
                    if index == 0:
                        time_12 = self.rid_sta[-i, node_1].v_d
                    else:
                        time_12 = tl.car_time(self.rider[-node_1].des_lat, self.rider[-node_1].des_lon, self.rider[-i].des_lat, self.rider[-i].des_lon)
                    time_list.append((i, time_12))
                time_list.sort(key=itemgetter(1), reverse=False)
                route.append(time_list[0][0])
                route_time.append(time_list[0][1])
                node_1 = route[-1]
                omega.remove(node_1)
                index += 1
        # route_time中的第一个时间是司机起点或站点到route[0]的开车时间，需要舍去，new_route_time记录了route中相邻两点的开车时间
        new_route_time = route_time[1: ]
        return route, new_route_time

    '''#######基于当前路径判断是否满足每个司机最多只绕经max_stops个站点#######'''
    def additional_stops(self, route, route_time: list, j, s, type):
        # 首先补充司机起点和终点以及站点的距离信息
        new_route_time = copy.deepcopy(route_time)
        if type == 'SR':
            r1, r2 = route[0], -route[-1]       # 路径route中最开始接的乘客和最后送的乘客
            t_o_o = self.rid_dri[r1, j].o_o     # 司机起点到乘客r1起点的开车时间
            t_d_d = self.rid_dri[r2, j].d_d     # 司机终点到乘客r1终点的开车时间
            new_route_time.insert(0, t_o_o)
            new_route_time.append(t_d_d)
        elif type == 'RT':
            r1, r2 = route[0], route[-1]
            t_o_o = self.rid_dri[r1, j].o_o
            t_o_s = self.rid_sta[r2, s].o_v
            t_s_d = self.dri_sta[j, s].v_d
            new_route_time.insert(0, t_o_o)
            new_route_time.append(t_o_s)
            new_route_time.append(t_s_d)
        else:
            r1, r2 = -route[0], -route[-1]
            t_o_s = self.dri_sta[j, s].o_v
            t_s_d = self.rid_sta[r1, s].v_d
            t_d_d = self.rid_dri[r2, j].d_d
            new_route_time.insert(0, t_o_s)
            new_route_time.insert(1, t_s_d)
            new_route_time.append(t_d_d)
        # 然后根据路径对应的时间判断司机整个过程经过的站点数量
        delete_stops = 0
        for t in new_route_time:
            if t * self.v_c <= self.dis_near:
                delete_stops += 1
        stops = 1 + len(new_route_time) - delete_stops     # 整个路径去除重合点之后的点的数量
        if stops <= self.max_stops:
            flag = True
        else:
            flag = False
        return flag

    '''#######基于乘客集合I给出其对应的记录序列i1,i2,i3#######'''
    def sort_riders(self, I):
        I_ = copy.deepcopy(I)
        for i in range(self.vehicle_capacity - len(I_)):
            I_.append(0)
        new_I = sorted(I_, reverse=True)
        return new_I[0], new_I[1], new_I[2]

    '''#######基于一对一匹配，递归确定一对多匹配#######'''
    def find_many_match(self, j, w, Iset, matchings, mat_list, type, s):
        while w < self.max_riders and len(Iset[j][w][type].keys()) != 0:
            index_dic = {}   # 用于记录已经搜索过的乘客集合I
            w += 1      # 匹配的人数＋1
            for I_tuple in Iset[j][w - 1][type].keys():   # I是一个tuple或者int
                # 将乘客集合转为列表形式
                if w == 2:
                    I = [I_tuple]
                else:
                    I = list(I_tuple)
                for p in Iset[j][1][type].keys():    # 在当前的乘客集合I中加入一个满足一对一匹配约束的乘客p
                    if p not in I:
                        I_new = I + [p]
                        I_new.sort(reverse=True)     # 从大到小排序
                        # 若该匹配之前没有进行可行性判断
                        if tuple(I_new) not in index_dic.keys():
                            index_dic[tuple(I_new)] = 0
                            if self.subfeas(I, p, j, Iset, type):    # 判断该匹配的任一子集是否是可行匹配，如果是，则进行可行性判断
                                route, route_time = self.greedy_route(I_new, j, s, type)
                                # 基于当前路径判断是否满足每个司机最多只绕经两个额外的站点
                                if self.additional_stops(route, route_time, j, s, type):
                                    con_time, con, result_dic = self.judge_feasibility.feasible_many(I_new, j, s, type, route, route_time)
                                    if con_time == True:    # 满足时间可行性即记录，用于寻找满足组时间可行性的一对多匹配（仅时间可行性满足递归性质）
                                        Iset[j][w][type][tuple(I_new)] = 0
                                        if con == True:     # 满足所有可行性条件，则记录可行匹配的的相关信息
                                            i1, i2, i3 = self.sort_riders(I + [p])
                                            matchings[s][s, j, i1, i2, i3] = result_dic
                                            mat_list.append((s, j, i1, i2, i3))

    '''#######寻找站点s的所有可行匹配#######'''
    def station_feas_match(self, r_list, d_list, s):
        # matchings根据站点分类存储每个匹配的具体信息，mat_list存储匹配编号
        matchings = {}
        matchings[s] = {}
        mat_list = []
        Iset = {}  # 记录每个司机对应的匹配乘客组合
        for j in d_list:
            Iset[j] = {}
            for w in range(1, self.max_riders + 1):
                Iset[j][w] = {'RT': {}, 'TR': {}, 'SR': {}}
        # 首先找到所有的一对一可行匹配
        self.find_one_match(mat_list, matchings, Iset, r_list, d_list, s)
        ################## 根据Router函数为一对多匹配确定路径
        # 按顺序寻为每个司机j寻找一对多可行匹配
        for j in d_list:
            w = 1
            if s == 0:
                self.find_many_match(j, w, Iset, matchings, mat_list, 'SR', s)
            else:
                self.find_many_match(j, w, Iset, matchings, mat_list, 'RT', s)
                self.find_many_match(j, w, Iset, matchings, mat_list, 'TR', s)
        return matchings, mat_list

    '''#######主框架：寻找每个站点的可行匹配#######'''
    def find_all_matches(self):
        # 存储可行匹配
        matchings = {}
        mat_list = []
        # 对于每个站点的可行乘客集合和司机集合寻找对应的可行匹配
        for s in self.station.keys():      # 寻找所有类型的匹配
        # for s in [0]:      # 只寻找SR匹配
            r_list = list(set(self.station[s].rider) & set(self.r_ins))
            d_list = list(set(self.station[s].driver) & set(self.d_ins))
            s_matchings, s_mat_list = self.station_feas_match(r_list, d_list, s)   # 站点s的可行匹配
            matchings[s] = s_matchings[s]
            mat_list = mat_list + s_mat_list
        return matchings, mat_list

    def preference_sort(self, matchings: dict, mat_list: list):
        pre_r = {}    # 三层字典，每个乘客相关的可行匹配及该乘客对应获取的成本节约值和偏好排序
        pre_d = {}    # 三层字典，每个司机相关的可行匹配及该司机对应获取的成本节约值和偏好排序
        for i in self.rider.keys():
            pre_r[i] = {'mat': {}, 'sort': []}
        for j in self.driver.keys():
            pre_d[j] = {'mat': {}, 'sort': []}
        ########### 对于每个匹配进行分类存放，方便确定稳定匹配和确定偏好序列
        for (s, j, i1, i2, i3) in mat_list:
            pre_d[j]['mat'][s, j, i1, i2, i3] = matchings[s][s, j, i1, i2, i3]['save_d']
            pre_d[j]['sort'].append(((s, j, i1, i2, i3), matchings[s][s, j, i1, i2, i3]['save_d']))
            I = (i1, i2, i3)
            for i_index in range(len(I)):
                i = I[i_index]
                if i != 0:
                    pre_r[i]['mat'][s, j, i1, i2, i3] = matchings[s][s, j, i1, i2, i3]['save_r'][i_index]
                    pre_r[i]['sort'].append(((s, j, i1, i2, i3), matchings[s][s, j, i1, i2, i3]['save_r'][i_index]))
                else:
                    break
        ########### 进行偏好排序工作
        for j in pre_d.keys():
            pre_d[j]['sort'].sort(key=itemgetter(1), reverse=True)   # 从大到小排序
        for i in pre_r.keys():
            pre_r[i]['sort'].sort(key=itemgetter(1), reverse=True)   # 从大到小排序
        ####### 将不包含任何可行匹配的乘客和司机剔除
        remove_r, remove_d = [], []
        for i in pre_r.keys():
            if len(pre_r[i]['sort']) == 0:
                remove_r.append(i)
        for j in pre_d.keys():
            if len(pre_d[j]['sort']) == 0:
                remove_d.append(j)
        rins_new = list(set(self.r_ins) - set(remove_r))
        dins_new = list(set(self.d_ins) - set(remove_d))
        return pre_r, pre_d, rins_new, dins_new










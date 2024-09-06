import Tools as tl
import copy

class Feasible_Condition:
    def __init__(self, information):
        self.rider = information.rider
        self.driver = information.driver
        self.rid_dri = information.rid_dri
        self.dri_sta = information.dri_sta
        self.rid_sta = information.rid_sta
        self.sta_sta = information.sta_sta
        self.v_c = information.parameters.v_c
        self.rule = information.parameters.rule
        self.alpha = information.parameters.alpha
        self.cost_car = information.parameters.cost_car
        self.vehicle_capacity = information.parameters.vehicle_capacity
    ########## 顺风车计价方式，根据嘀嗒出行成都设置
    def share_price(self, rider_time, type, rule):
        # 输入：rider_time乘车点到下车点的合乘距离，type为整合匹配类型，rule为服务费收取规则
        distance = rider_time * self.v_c / 1000          # 拼车的距离，千米
        detour_dis = 4          # 成都嘀嗒出行平均绕路距离为4公里
        # 如果未拼成
        if type == 'one':
            if distance < 10:
                price = detour_dis * 1.01 + distance * 1.01
            elif 10 <= distance < 30:
                price = detour_dis * 1.01 + 10 * 1.01 + (distance - 10) * 1.12
            elif 30 <= distance < 50:
                price = detour_dis * 1.01 + 10 * 1.01 + 20 * 1.12 + (distance - 30) * 0.57
            elif 50 <= distance < 100:
                price = detour_dis * 1.01 + 10 * 1.01 + 20 * 1.12 + 20 * 0.57 + (distance - 50) * 0.92
            else:
                price = detour_dis * 1.01 + 10 * 1.01 + 20 * 1.12 + 20 * 0.57 + 50 * 0.92 + (distance - 100) * 0.4
        else:
            if distance < 10:
                price = detour_dis * 0.81 + distance * 0.81
            elif 10 <= distance < 30:
                price = detour_dis * 0.81 + 10 * 0.81 + (distance - 10) * 0.90
            elif 30 <= distance < 50:
                price = detour_dis * 0.81 + 10 * 0.81 + 20 * 0.90 + (distance - 30) * 0.57
            elif 50 <= distance < 100:
                price = detour_dis * 0.81 + 10 * 0.81 + 20 * 0.90 + 20 * 0.57 + (distance - 50) * 0.92
            else:
                price = detour_dis * 0.81 + 10 * 0.81 + 20 * 0.90 + 20 * 0.57 + 50 * 0.92 + (distance - 100) * 0.4
        # 对该服务乘客收取的服务费用
        service = price * 0.1  # 按照固定的费率收取服务费用
        return price, service

    ############ 判断一对一匹配的可行性
    def feasible_one(self, i, j, s, r, d, type):
        con = False
        con_time = False
        result_dic = {}
        if type == 'SR':
            t_oo = self.rid_dri[i, j].o_o
            t_dd = self.rid_dri[i, j].d_d
            T_r = r.drive_time
            T_d = t_oo + T_r + t_dd
            if T_d <= d.Tmax and T_r <= r.Tmax:
                pick_d = max(d.departure, r.departure - t_oo)
                pick_r = max(pick_d + t_oo, r.departure)
                if pick_r + T_r <= r.arrival and pick_d + T_d <= d.arrival:
                    con_time = True      # 满足时间可行性
                    detour_d = T_d - d.drive_time
                    price_r1, service_r1 = self.share_price(T_r,'one', self.rule)   # 计算拼车价格和平台服务价格
                    cost_d = T_d * self.v_c * self.cost_car - (price_r1 - service_r1)
                    gen_cost_d = cost_d + T_d * self.alpha
                    cost_r1 = price_r1
                    gen_cost_r1 = cost_r1 + T_r * self.alpha
                    save_d = d.gencost - gen_cost_d
                    save_r1 = r.gencost - gen_cost_r1
                    if save_d > 0 and save_r1 > 0:
                        con = True
                        welfare = save_d + save_r1 + service_r1
                        detour_r1 = T_r - r.alone_time    # 类型1乘客此项不为0
                        result_dic = {'wel': round(welfare, 4), 'save_d': round(save_d, 4),
                                      'save_r': [round(save_r1, 4), 0, 0],
                                      'T_d': round(T_d, 2), 'T_r': [round(T_r, 2), 0, 0],
                                      'cost_d': round(cost_d, 2), 'cost_r': [round(cost_r1, 2), 0, 0],
                                      'detour_d': round(detour_d, 2), 'detour_r': [round(detour_r1, 2), 0, 0],
                                      'size': 'one', 'type': type, 'num_riders': 1}
        elif type == 'RT':
            if s != r.des_sta:
                t_oo = self.rid_dri[i, j].o_o
                t_ov = self.rid_sta[i, s].o_v
                t_vd = self.dri_sta[j, s].v_d
                T_r = t_ov + self.sta_sta[s, r.des_sta].trans_duration + r.des_time
                T_d = t_oo + t_ov + t_vd
                if T_d <= d.Tmax and T_r <= r.Tmax:
                    pick_d = max(d.departure, r.departure - t_oo)
                    pick_r = max(r.departure, pick_d + t_oo)
                    if pick_r + T_r <= r.arrival and pick_d + T_d <= d.arrival:
                        con_time = True
                        detour_d = T_d - d.drive_time
                        price_r1, service_r1 = self.share_price(t_ov,'one', self.rule)
                        cost_d = T_d * self.v_c * self.cost_car - (price_r1 - service_r1)
                        gen_cost_d = cost_d + T_d * self.alpha
                        cost_r1 = price_r1 + self.sta_sta[s, r.des_sta].trans_cost
                        gen_cost_r1 = cost_r1 + T_r * self.alpha
                        save_d = d.gencost - gen_cost_d
                        save_r1 = r.gencost - gen_cost_r1
                        if save_d > 0 and save_r1 > 0:
                            con = True
                            welfare = save_d + save_r1 + service_r1
                            detour_r1 = T_r - r.alone_time
                            result_dic = {'wel': round(welfare, 4), 'save_d': round(save_d, 4),
                                          'save_r': [round(save_r1, 4), 0, 0],
                                          'T_d': round(T_d, 2), 'T_r': [round(T_r, 2), 0, 0],
                                          'cost_d': round(cost_d, 2), 'cost_r': [round(cost_r1, 2), 0, 0],
                                          'detour_d': round(detour_d, 2), 'detour_r': [round(detour_r1, 2), 0, 0],
                                          'size': 'one', 'type': type, 'num_riders': 1}
        else:
            if s != r.org_sta:
                t_ov = self.dri_sta[j, s].o_v
                t_vd = self.rid_sta[i, s].v_d
                t_dd = self.rid_dri[i, j].d_d
                T_r = r.org_time + self.sta_sta[r.org_sta, s].trans_duration + t_vd
                T_d = t_ov + t_vd + t_dd
                if T_d <= d.Tmax and T_r <= r.Tmax:
                    pick_d = max(d.departure, r.departure + r.org_time + self.sta_sta[r.org_sta, s].trans_duration - t_ov)
                    pick_r = max(r.departure, d.departure + t_ov - r.org_time - self.sta_sta[r.org_sta, s].trans_duration)
                    if pick_r + T_r <= r.arrival and pick_d + T_d <= d.arrival:
                        con_time = True
                        detour_d = T_d - d.drive_time
                        price_r1, service_r1 = self.share_price(t_vd, 'one', self.rule)
                        cost_d = T_d * self.v_c * self.cost_car - (price_r1 - service_r1)
                        gen_cost_d = cost_d + T_d * self.alpha
                        cost_r1 = self.sta_sta[r.org_sta, s].trans_cost + price_r1
                        gen_cost_r1 = cost_r1 + T_r * self.alpha
                        save_d = d.gencost - gen_cost_d
                        save_r1 = r.gencost - gen_cost_r1
                        if save_d > 0 and save_r1 > 0:
                            con = True
                            welfare = save_d + save_r1 + service_r1
                            detour_r1 = T_r - r.alone_time
                            result_dic = {'wel': round(welfare, 4), 'save_d': round(save_d, 4),
                                          'save_r': [round(save_r1, 4), 0, 0],
                                          'T_d': round(T_d, 2), 'T_r': [round(T_r, 2), 0, 0],
                                          'cost_d': round(cost_d, 2), 'cost_r': [round(cost_r1, 2), 0, 0],
                                          'detour_d': round(detour_d, 2), 'detour_r': [round(detour_r1, 2), 0, 0],
                                          'size': 'one', 'type': type, 'num_riders': 1}
        return con_time, con, result_dic
    ############# 计算一对多匹配中司机的出发时间
    def calculate_pick_d(self, j, I, s, time_route, rider_result, type, t_ojo1_ojv):
        pick_list = [self.driver[j].departure]
        for i in I:
            if type == 'SR' or type == 'RT':
                pick = self.rider[i].departure - sum(time_route[0:rider_result[i]['o_index']]) - t_ojo1_ojv
            else:
                pick = self.rider[i].departure + self.rider[i].org_time + self.sta_sta[self.rider[i].org_sta, s].trans_duration - t_ojo1_ojv
            pick_list.append(pick)
        pick_max = max(pick_list)
        return pick_max
    ############ 计算一对多匹配的相关结果
    def record_many(self, I, T_d, cost_d, detour_d, save_d, sum_save_r, sum_service, rider_result, type):
        con = True
        welfare = save_d + sum_save_r + sum_service
        save_l, T_l, cost_l, detour_l = [], [], [], []
        for i in I:
            rider_result[i]['detour_r'] = rider_result[i]['T_r'] - self.rider[i].alone_time
            save_l.append(round(rider_result[i]['save_r'], 4))
            T_l.append(round(rider_result[i]['T_r'], 2))
            cost_l.append(round(rider_result[i]['cost_r'], 2))
            detour_l.append(round(rider_result[i]['detour_r'], 2))
        for i in range(self.vehicle_capacity - len(I)):
            save_l.append(0)
            T_l.append(0)
            cost_l.append(0)
            detour_l.append(0)
        result_dic = {'wel': round(welfare, 4), 'save_d': round(save_d, 4), 'save_r': save_l,
                      'T_d': round(T_d, 2), 'T_r': T_l,
                      'cost_d': round(cost_d, 2), 'cost_r': cost_l,
                      'detour_d': round(detour_d, 2), 'detour_r': detour_l,
                      'size': 'many', 'type': type, 'num_riders': len(I)}
        return con, result_dic
    ############ 基于路径判断一对多匹配的时间可行性
    def feasible_many(self, I, j, s, type, route, route_time):
        I.sort(reverse=True)    # 首先把乘客编号从大到小排序
        con = False
        con_time = False
        result_dic = {}
        rider_result = {}    # 记录乘客的相关结果信息
        # 首先判断是否满足站点数量约束
        if type == 'SR':
            for i in I:
                rider_result[i] = {'o_index': route.index(i), 'd_index': route.index(-i), 'share_r': 0, 'save_r': 0,
                                   'T_r': 0, 'cost_r': 0, 'detour_r': 0, 'price_r': 0, 'service_r': 0}
            t_ojo1 = self.rid_dri[route[0], j].o_o
            t_d1dj = self.rid_dri[abs(route[-1]), j].d_d
            T_d = t_ojo1 + sum(route_time) + t_d1dj
            if T_d <= self.driver[j].Tmax:
                flag_tmax = True  # 判断乘客是否满足最大时间约束
                for i in I:
                    rider_result[i]['T_r'] = sum(route_time[rider_result[i]['o_index']: rider_result[i]['d_index']])
                    rider_result[i]['share_r'] = self.rider[i].drive_time
                    if rider_result[i]['T_r'] > self.rider[i].Tmax:
                        flag_tmax = False
                if flag_tmax:
                    pick_d = self.calculate_pick_d(j, I, s, route_time, rider_result, type, t_ojo1)
                    if pick_d + T_d <= self.driver[j].arrival:
                        flag_arrival = True  # 判断乘客是否满足最晚到达时间约束
                        for i in I:
                            pick_r = max(self.rider[i].departure,
                                         pick_d + t_ojo1 + sum(route_time[0: rider_result[i]['o_index']]))
                            if pick_r + rider_result[i]['T_r'] > self.rider[i].arrival:
                                flag_arrival = False
                        if flag_arrival:
                            con_time = True
                            sum_price, sum_service = 0, 0
                            detour_d = T_d - self.driver[j].drive_time
                            for i in I:
                                rider_result[i]['price_r'], rider_result[i]['service_r'] = \
                                    self.share_price(rider_result[i]['share_r'],'many', self.rule)
                                sum_price += rider_result[i]['price_r']
                                sum_service += rider_result[i]['service_r']
                            cost_d = T_d * self.v_c * self.cost_car - (sum_price - sum_service)
                            gen_cost_d = cost_d + T_d * self.alpha
                            save_d = self.driver[j].gencost - gen_cost_d
                            if save_d > 0:
                                flag_save = True
                                sum_save_r = 0
                                for i in I:
                                    rider_result[i]['cost_r'] = rider_result[i]['price_r']
                                    gen_cost_r = rider_result[i]['cost_r'] + rider_result[i]['T_r'] * self.alpha
                                    rider_result[i]['save_r'] = self.rider[i].gencost - gen_cost_r
                                    sum_save_r += rider_result[i]['save_r']
                                    if rider_result[i]['save_r'] <= 0:
                                        flag_save = False
                                if flag_save:
                                    con, result_dic = self.record_many(I, T_d, cost_d, detour_d, save_d, sum_save_r,
                                                                       sum_service, rider_result, type)
        elif type == 'RT':
            for i in I:
                rider_result[i] = {'o_index': route.index(i), 'd_index': 0, 'share_r': 0, 'save_r': 0, 'T_r': 0,
                                   'cost_r': 0, 'detour_r': 0, 'price_r': 0, 'service_r': 0}
            t_ojo1 = self.rid_dri[route[0], j].o_o
            t_ov = self.rid_sta[route[-1], s].o_v
            t_vdj = self.dri_sta[j, s].v_d
            T_d = t_ojo1 + sum(route_time) + t_ov + t_vdj
            if T_d <= self.driver[j].Tmax:
                flag_tmax = True  # 判断乘客是否满足最大时间约束
                for i in I:
                    rider_result[i]['share_r'] = self.rid_sta[i, s].o_v
                    rider_result[i]['T_r'] = sum(route_time[rider_result[i]['o_index']:]) + t_ov + \
                                             self.sta_sta[s, self.rider[i].des_sta].trans_duration + self.rider[
                                                 i].des_time
                    if rider_result[i]['T_r'] > self.rider[i].Tmax:
                        flag_tmax = False
                if flag_tmax:
                    pick_d = self.calculate_pick_d(j, I, s, route_time, rider_result, type, t_ojo1)
                    if pick_d + T_d <= self.driver[j].arrival:
                        flag_arrival = True
                        for i in I:
                            pick_r = max(self.rider[i].departure,
                                         pick_d + t_ojo1 + sum(route_time[0:rider_result[i]['o_index']]))
                            if pick_r + rider_result[i]['T_r'] > self.rider[i].arrival:
                                flag_arrival = False
                        if flag_arrival:
                            con_time = True
                            sum_price, sum_service = 0, 0
                            detour_d = T_d - self.driver[j].drive_time
                            for i in I:
                                rider_result[i]['price_r'], rider_result[i]['service_r'] = \
                                    self.share_price(rider_result[i]['share_r'], 'many', self.rule)
                                sum_price += rider_result[i]['price_r']
                                sum_service += rider_result[i]['service_r']
                            cost_d = T_d * self.v_c * self.cost_car - (sum_price - sum_service)
                            gen_cost_d = cost_d + T_d * self.alpha
                            save_d = self.driver[j].gencost - gen_cost_d
                            if save_d > 0:
                                flag_save = True
                                sum_save_r = 0
                                for i in I:
                                    rider_result[i]['cost_r'] = (rider_result[i]['price_r'] +
                                                                 self.sta_sta[s, self.rider[i].des_sta].trans_cost)
                                    gen_cost_r = rider_result[i]['cost_r'] + rider_result[i]['T_r'] * self.alpha
                                    rider_result[i]['save_r'] = self.rider[i].gencost - gen_cost_r
                                    sum_save_r += rider_result[i]['save_r']
                                    if rider_result[i]['save_r'] <= 0:
                                        flag_save = False
                                if flag_save:
                                    con, result_dic = self.record_many(I, T_d, cost_d, detour_d, save_d, sum_save_r,
                                                                       sum_service, rider_result, type)
        else:
            for i in I:
                rider_result[i] = {'o_index': 0, 'd_index': route.index(-i), 'share_r': 0, 'save_r': 0, 'T_r': 0,
                                   'cost_r': 0, 'detour_r': 0, 'price_r': 0, 'service_r': 0}
            t_ojv = self.dri_sta[j, s].o_v
            t_vd1 = self.rid_sta[abs(route[0]), s].v_d
            t_didj = self.rid_dri[abs(route[-1]), j].d_d
            T_d = t_ojv + t_vd1 + sum(route_time) + t_didj
            if T_d <= self.driver[j].Tmax:
                flag_tmax = True
                for i in I:
                    rider_result[i]['share_r'] = self.rid_sta[i, s].v_d
                    rider_result[i]['T_r'] = self.rider[i].org_time + self.sta_sta[
                        self.rider[i].org_sta, s].trans_duration \
                                             + t_vd1 + sum(route_time[0:rider_result[i]['d_index']])
                    if rider_result[i]['T_r'] > self.rider[i].Tmax:
                        flag_tmax = False
                if flag_tmax:
                    pick_d = self.calculate_pick_d(j, I, s, route_time, rider_result, type, t_ojv)
                    if pick_d + T_d <= self.driver[j].arrival:
                        flag_arrival = True
                        for i in I:
                            pick_r = max(self.rider[i].departure,
                                         pick_d + t_ojv - self.sta_sta[self.rider[i].org_sta, s].trans_duration -
                                         self.rider[i].org_time)
                            if pick_r + rider_result[i]['T_r'] > self.rider[i].arrival:
                                flag_arrival = False
                        if flag_arrival:
                            con_time = True
                            sum_price, sum_service = 0, 0
                            detour_d = T_d - self.driver[j].drive_time
                            for i in I:
                                rider_result[i]['price_r'], rider_result[i]['service_r'] = \
                                    self.share_price(rider_result[i]['share_r'], 'many', self.rule)
                                sum_price += rider_result[i]['price_r']
                                sum_service += rider_result[i]['service_r']
                            cost_d = T_d * self.v_c * self.cost_car - (sum_price - sum_service)
                            gen_cost_d = cost_d + T_d * self.alpha
                            save_d = self.driver[j].gencost - gen_cost_d
                            if save_d > 0:
                                flag_save = True
                                sum_save_r = 0
                                for i in I:
                                    rider_result[i]['cost_r'] = (rider_result[i]['price_r'] +
                                                                 self.sta_sta[self.rider[i].org_sta, s].trans_cost)
                                    gen_cost_r = rider_result[i]['cost_r'] + rider_result[i]['T_r'] * self.alpha
                                    rider_result[i]['save_r'] = self.rider[i].gencost - gen_cost_r
                                    sum_save_r += rider_result[i]['save_r']
                                    if rider_result[i]['save_r'] <= 0:
                                        flag_save = False
                                if flag_save:
                                    con, result_dic = self.record_many(I, T_d, cost_d, detour_d, save_d, sum_save_r,
                                                                       sum_service, rider_result, type)
        return con_time, con, result_dic

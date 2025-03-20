from operator import itemgetter
import copy
import random
import Matching as mtg
import Algorithm as alg
import pandas as pd
import numpy as np

class Behavior_Analysis:
    def __init__(self, a, information, r_ins, d_ins):
        self.instance_num = a
        self.information = information
        self.r_ins = r_ins
        self.d_ins = d_ins
        self.period = information.parameters.period
        self.deviation = information.parameters.deviation
        self.pricing_scaling = 1.0
        self.obj_choice_rss = 'double'
        self.obj_choice_bfs = 'welfare'
        self.omega = -10000
    def find_feasible_matches(self):
        # 每天在原基础上修改用户的出发时间和到达时间
        new_information = copy.deepcopy(self.information)
        for i in self.r_ins:
            bias = np.random.normal(loc=0, scale=self.deviation)    # 生成均值为0，标准差为self.deviation的正态分布，单位分钟
            new_information.rider[i].update_departure(bias * 60)    # 更新departure的时间
        for j in self.d_ins:
            bias = np.random.normal(loc=0, scale=self.deviation)    # 生成均值为0，标准差为self.deviation的正态分布，单位分钟
            new_information.driver[j].update_departure(bias * 60)
        # 确定所有可行匹配
        Feasible_match = mtg.Find_All_Matches(new_information, self.r_ins, self.d_ins, self.pricing_scaling)
        matchings, mat_list = Feasible_match.find_all_matches()
        pre_r, pre_d, rins_new, dins_new = Feasible_match.preference_sort(matchings, mat_list)
        print('可行匹配数量为{}'.format(len(mat_list)))
        return new_information, pre_r, pre_d, rins_new, dins_new, matchings, mat_list
    def users_behavior(self, new_information, matched_rider, matched_driver, pre_r, pre_d, pi_r, pi_d,
                       remain_rider, remain_driver, know_driver, know_rider, know_user):
        # 其次为匹配的用户寻找已知互相知道信息的阻塞对，首先对已经匹配的用户排序
        sort_list = []
        for i in matched_rider:
            sort_list.append((i, new_information.rider[i].departure))
        for j in matched_driver:
            sort_list.append((j + self.information.parameters.total_riders, new_information.driver[j].departure))
        sort_list.sort(key=itemgetter(1), reverse=False)  # 按出发时间从小到大排序
        leave_r, leave_d, block_pair = [], [], []  # 记录符合要求的阻塞匹配，以及会离开系统的用户
        # 按出发时间从小到大，依此提出自己更好的选择
        for (aa, bb) in sort_list:
            if aa <= self.information.parameters.total_riders:  # 由乘客提议
                if aa not in leave_r:  # 提议的乘客在之前没有和其他人形成串谋离开系统
                    for ((s, j, i1, i2, i3), cc) in pre_r[aa]['sort']:
                        if cc <= pi_r[aa]:  # utility更小的匹配不可能是阻塞对
                            break
                        else:
                            # 需要判断这个可行匹配的其他成员是不是还在系统中，当前没有和其他人形成串谋，且全部是已知信息用户，且其他用户的utility也增大
                            nn = {i1, i2, i3} - {0, aa}
                            if (j in remain_driver) and (nn & set(remain_rider)) == nn:
                                if j not in leave_d and len((nn) & set(leave_r)) == 0:
                                    if j in know_driver[aa] and pre_d[j]['mat'][s, j, i1, i2, i3] > pi_d[j]:
                                        flag = True
                                        for i in nn:
                                            if i not in know_rider[aa] or pre_r[i]['mat'][s, j, i1, i2, i3] <= pi_r[i]:
                                                flag = False
                                                break
                                        if flag:  # 三个条件均满足，阻塞对对应的用户退出系统
                                            block_pair.append((s, j, i1, i2, i3))
                                            leave_d.append(j)
                                            for i in ({i1, i2, i3} - {0}):
                                                leave_r.append(i)
                                            break
            else:  # 由司机提议
                new_aa = aa - self.information.parameters.total_riders
                if new_aa not in leave_d:
                    for ((s, j, i1, i2, i3), cc) in pre_d[new_aa]['sort']:
                        if cc <= pi_d[new_aa]:
                            break
                        else:
                            if ({i1, i2, i3} - {0}) & set(remain_rider) == ({i1, i2, i3} - {0}):
                                if len(({i1, i2, i3} - {0}) & set(leave_r)) == 0:
                                    flag = True
                                    for i in ({i1, i2, i3} - {0}):
                                        if i not in know_user[new_aa] or pre_r[i]['mat'][s, j, i1, i2, i3] <= pi_r[i]:
                                            flag = False
                                            break
                                    if flag:
                                        block_pair.append((s, j, i1, i2, i3))
                                        leave_d.append(j)
                                        for i in ({i1, i2, i3} - {0}):
                                            leave_r.append(i)
                                        break
        # 输出某一天离开系统的阻塞匹配
        return leave_r, leave_d, block_pair
    # 确定近似匹配的匹配用户和效用
    def utility(self, solution, remain_rider, remain_driver, pre_r, pre_d):
        matched_r, matched_d = [], []
        pi_r, pi_d = {}, {}
        for i in remain_rider:
            pi_r[i] = 0
        for j in remain_driver:
            pi_d[j] = 0
        for (s, j, i1, i2, i3) in solution:
            matched_d.append(j)
            pi_d[j] = pre_d[j]['mat'][s, j, i1, i2, i3]
            for i in ({i1, i2, i3} - {0}):
                matched_r.append(i)
                pi_r[i] = pre_r[i]['mat'][s, j, i1, i2, i3]
        return matched_r, matched_d, pi_r, pi_d

    def update_obj(self, fix_match, mat_list, matchings):
        obj_fix = 0
        for (s, j, i1, i2, i3) in fix_match:
            if (s, j, i1, i2, i3) in mat_list:
                obj_fix += matchings[s][s, j, i1, i2, i3]['wel']
            else:     # 如果该匹配在第tt天不可行，则可以看是否可以和其中一部分乘客构成可行匹配
                qq = []
                if len({i1, i2, i3} - {0}) == 3:
                    if (s, j, i1, 0, 0) in mat_list:
                        qq.append(((s, j, i1, 0, 0), matchings[s][s, j, i1, 0, 0]['wel']))
                    if (s, j, i2, 0, 0) in mat_list:
                        qq.append(((s, j, i2, 0, 0), matchings[s][s, j, i2, 0, 0]['wel']))
                    if (s, j, i3, 0, 0) in mat_list:
                        qq.append(((s, j, i3, 0, 0), matchings[s][s, j, i3, 0, 0]['wel']))
                    if (s, j, i1, i2, 0) in mat_list:
                        qq.append(((s, j, i1, i2, 0), matchings[s][s, j, i1, i2, 0]['wel']))
                    if (s, j, i1, i3, 0) in mat_list:
                        qq.append(((s, j, i1, i3, 0), matchings[s][s, j, i1, i3, 0]['wel']))
                    if (s, j, i2, i3, 0) in mat_list:
                        qq.append(((s, j, i2, i3, 0), matchings[s][s, j, i2, i3, 0]['wel']))
                elif len({i1, i2, i3} - {0}) == 2:
                    if (s, j, i1, 0, 0) in mat_list:
                        qq.append(((s, j, i1, 0, 0), matchings[s][s, j, i1, 0, 0]['wel']))
                    if (s, j, i2, 0, 0) in mat_list:
                        qq.append(((s, j, i2, 0, 0), matchings[s][s, j, i2, 0, 0]['wel']))
                if len(qq) > 0:
                    qq.sort(key=itemgetter(1), reverse=True)
                    # print(qq)
                    obj_fix += qq[0][1]
                    # print('#################', qq[0])
        return obj_fix

    def appr_scenario(self, new_information, new_r_ins, new_d_ins, new_matchings, new_mat_list, new_pre_r, new_pre_d,
                      empty, remain_r, remain_d, know_user, know_driver, know_rider, fix_match, mat_list, matchings,
                      method):
        col_row = alg.Column_Row(new_r_ins, new_d_ins, new_matchings, new_mat_list, new_pre_r, new_pre_d)
        if method == 'large':
            bfs_obj, bfs_sol, bfs_iter, bfs_theta = 0, [], 0, 0
        else:
            bfs_obj, bfs_sol, bfs_iter, bfs_theta = col_row.exact('greedy', self.obj_choice_bfs, matchings)
        if bfs_obj == 0:
            empty.append(1)
            print('*************** infeasible ************')
            # 继续求解近似匹配结果
            appr_obj, appr_sol, appr_iter, num_bro, mat_bro, appr_theta = col_row.approximate(
                'greedy', self.obj_choice_rss, self.omega, matchings
            )
            # 分析用户行为，找已知阻塞匹配
            matched_r, matched_d, pi_r, pi_d = self.utility(appr_sol, remain_r, remain_d, new_pre_r, new_pre_d)
            leave_r, leave_d, block_pair = self.users_behavior(
                new_information, matched_r, matched_d, new_pre_r, new_pre_d, pi_r, pi_d, remain_r,
                remain_d, know_driver, know_rider, know_user
            )
            # 更新剩余用户、固定匹配、知用户和最终的obj
            for i in leave_r:
                remain_r.remove(i)
            for j in leave_d:
                remain_d.remove(j)
            for (s, j, i1, i2, i3) in block_pair:
                fix_match.append((s, j, i1, i2, i3))
            fix_obj = self.update_obj(fix_match, mat_list, matchings)     # 必须用包含所有可行匹配的验证已经固定匹配是否还可行，new_mat_list中没有
            print('approximate: 此时固定匹配的obj为{}，固定匹配有{}个'.format(fix_obj, len(fix_match)))
            final_obj = fix_obj
            for (s, j, i1, i2, i3) in appr_sol:
                if j not in leave_d and len(({i1, i2, i3} - {0}) & set(leave_r)) == 0:     # 若该匹配得以保留
                    final_obj += new_matchings[s][s, j, i1, i2, i3]['wel']
                    for i in {i1, i2, i3} - {0}:
                        know_user[j].add(i)
                        know_driver[i].add(j)
                        for ii in {i1, i2, i3} - {0, i}:
                            know_rider[i].add(ii)
        else:
            empty.append(0)
            # 更新已知的用户
            for (s, j, i1, i2, i3) in bfs_sol:
                for i in {i1, i2, i3} - {0}:
                    know_user[j].add(i)
                    know_driver[i].add(j)
                    for ii in {i1, i2, i3} - {0, i}:
                        know_rider[i].add(ii)
            # 首先计算之前已经固定匹配的obj
            fix_obj = self.update_obj(fix_match, mat_list, matchings)
            for (s, j, i1, i2, i3) in fix_match:
                if (s, j, i1, i2, i3) in mat_list:
                    print('-----', (s, j, i1, i2, i3), '固定匹配包含在匹配解中')
            print('exact: 此时固定匹配的obj为{}，固定匹配有{}个'.format(fix_obj, len(fix_match)))
            final_obj = bfs_obj + fix_obj     # 当前稳定匹配（剩余用户的稳定匹配结果）+之前固定的匹配（移出用户构成的）
        return final_obj

    def centralized_scenario(self, new_information, matchings, mat_list, pre_r, pre_d, remain_r, remain_d,
                             know_user, know_driver, know_rider, fix_match):
        # 首先计算剩余用户的集中式最优结果
        print('remain riders {}, remain drivers {}'.format(len(remain_r), len(remain_d)))
        # dynamic_centralized 函数利用约束令移出系统用户对应的匹配为0，一定不被选择，即将相当于不考虑这些用户的可行匹配
        obj, sol, matched_r, matched_d, pi_r, pi_d = mtg.dynamic_centralized(
            matchings, mat_list, self.r_ins, self.d_ins, remain_r, remain_d, pre_r, pre_d
        )
        leave_r, leave_d, block_pair = self.users_behavior(
            new_information, matched_r, matched_d, pre_r, pre_d, pi_r, pi_d, remain_r,
            remain_d, know_driver, know_rider, know_user
        )
        # 更新剩余用户、固定匹配、知用户和最终的obj
        for i in leave_r:
            remain_r.remove(i)
        for j in leave_d:
            remain_d.remove(j)
        for (s, j, i1, i2, i3) in block_pair:
            fix_match.append((s, j, i1, i2, i3))
        fix_obj = self.update_obj(fix_match, mat_list, matchings)
        print('centralized: 此时固定匹配的obj为{}，固定匹配有{}个'.format(fix_obj, len(fix_match)))
        final_obj = fix_obj
        for (s, j, i1, i2, i3) in sol:
            if j not in leave_d and len(({i1, i2, i3} - {0}) & set(leave_r)) == 0:  # 若该匹配得以保留
                final_obj += matchings[s][s, j, i1, i2, i3]['wel']
                for i in {i1, i2, i3} - {0}:
                    know_user[j].add(i)
                    know_driver[i].add(j)
                    for ii in {i1, i2, i3} - {0, i}:
                        know_rider[i].add(ii)
        return final_obj

    def update_match(self, new_information, remain_r, remain_d, matchins, mat_list):
        remove_r = set(self.r_ins) - set(remain_r)
        remove_d = set(self.d_ins) - set(remain_d)
        new_matchings = copy.deepcopy(matchins)
        new_mat_list = copy.deepcopy(mat_list)
        # 对于每个匹配判断它包含的每个用户是否还在系统
        for (s, j, i1, i2, i3) in mat_list:
            if j in remove_d or len(remove_r & {i1, i2, i3}) > 0:
                new_mat_list.remove((s, j, i1, i2, i3))
                del new_matchings[s][s, j, i1, i2, i3]
        Feasible_match = mtg.Find_All_Matches(new_information, remain_r, remain_d, self.pricing_scaling)
        new_pre_r, new_pre_d, new_r_ins, new_d_ins = Feasible_match.preference_sort(new_matchings, new_mat_list)
        # new_r_ins, new_d_ins在剩余用户的基础上删除了不任何匹配的用户，这一步处理是为了RSS BFS算法引用不出错
        return new_matchings, new_mat_list, new_pre_r, new_pre_d, new_r_ins, new_d_ins



    # 主框架，计算30天内的最优集中式匹配解和稳定匹配解、以及考虑用户行为的结果，
    def analysis_main(self, res, method):
        # 近似稳定匹配情景：每天先BFS，无解则RSS，且记录无解的天数
        appr_remain_r, appr_remain_d = copy.deepcopy(self.r_ins), copy.deepcopy(self.d_ins)    # 系统中剩下来的用户
        appr_know_user = {j: set() for j in self.d_ins}      # 司机已知乘客的信息
        appr_know_driver = {i: set() for i in self.r_ins}    # 乘客已知司机的信息
        appr_know_rider = {i: set() for i in self.r_ins}     # 乘客已知其他乘客的信息
        appr_fix_match = []
        empty = []     # 记录无解的天数
        # 集中式匹配情景
        cen_remain_r, cen_remain_d = copy.deepcopy(self.r_ins), copy.deepcopy(self.d_ins)
        cen_know_user = {j: set() for j in self.d_ins}
        cen_know_driver = {i: set() for i in self.r_ins}
        cen_know_rider = {i: set() for i in self.r_ins}
        cen_fix_match = []
        # 考察周期
        for tt in range(1, self.period+1):
            print('========第{}天==========='.format(tt))
            ####### 首先更新用户时间窗，并给出所有用户对应的可行匹配
            new_information, pre_r, pre_d, rins_new, dins_new, matchings, mat_list = self.find_feasible_matches()
            ####### 计算集中式最优解
            cen_obj, cen_res = mtg.centralized_matching(matchings, mat_list, rins_new, dins_new)
            ####### 近似稳定匹配情景
            # 首先更新剩余用户对应的匹配，注意不是上面所有的匹配
            new_matchings, new_mat_list, new_pre_r, new_pre_d, new_r_ins, new_d_ins = self.update_match(
                new_information, appr_remain_r, appr_remain_d, matchings, mat_list
            )
            # 由于有一部分用户删除，利用BFS RSS算法求解前应该更新对应的可行匹配、pre_r,pre_d
            appr_final_obj = self.appr_scenario(
                new_information, new_r_ins, new_d_ins, new_matchings, new_mat_list, new_pre_r, new_pre_d,
                empty, appr_remain_r, appr_remain_d, appr_know_user, appr_know_driver, appr_know_rider,
                appr_fix_match, mat_list, matchings, method
            )
            print('此时，近似稳定匹配系统获得的总社会福利为{}'.format(appr_final_obj))
            ####### 集中式匹配情景
            cen_final_obj = self.centralized_scenario(
                new_information, matchings, mat_list, pre_r, pre_d, cen_remain_r, cen_remain_d, cen_know_user,
                cen_know_driver, cen_know_rider, cen_fix_match
            )
            print('此时，考虑用户行为时系统获得的总社会福利为{}'.format(cen_final_obj))
            # 记录每天的三种obj
            res.append([self.instance_num, len(self.r_ins), len(self.d_ins), tt, cen_obj, appr_final_obj, cen_final_obj,
                        appr_final_obj / cen_obj * 100, cen_final_obj / cen_obj * 100, empty[tt-1],
                        len(appr_remain_r), len(appr_remain_d), len(cen_remain_r), len(cen_remain_d),
                        len(appr_fix_match), len(cen_fix_match)])
        for aa in res:
            print(aa)
        print(sum(empty), empty)
















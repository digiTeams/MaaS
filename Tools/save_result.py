import pandas as pd
import numpy as np

class Save_Result:
    def __init__(self):
        pass
    # 保存匹配结果
    def save_match(self, instance_index, res_mat, matchings, name):
        res_np = []
        for (s, j, i1, i2, i3) in res_mat:
            key = (s, j, i1, i2, i3)
            mat = matchings[s][key]
            row = [s, j, i1, i2, i3, mat['wel'],
                   mat['save_d'], mat['save_r'][0], mat['save_r'][1], mat['save_r'][2],
                   mat['T_d'], mat['T_r'][0], mat['T_r'][1], mat['T_r'][2],
                   mat['cost_d'], mat['cost_r'][0], mat['cost_r'][1], mat['cost_r'][2],
                   mat['detour_d'], mat['detour_r'][0], mat['detour_r'][1], mat['detour_r'][2],
                   mat['size'], mat['type'], mat['num_riders']]
            res_np.append(row)
        col_name = ['station', 'driver', 'rider1', 'rider2', 'rider3', 'VMT',
                    'save_d', 'save_r1', 'save_r2', 'save_r3',
                    'T_d', 'T_r1', 'T_r2', 'T_r3',
                    'cost_d', 'cost_r1', 'cost_r2', 'cost_r3',
                    'detour_d', 'detour_r1', 'detour_r2', 'detour_r3',
                    'size', 'type', 'num_riders']
        res_df = pd.DataFrame(res_np, columns=col_name)
        res_df.to_csv('Results/' + name + '/instance_' + str(instance_index) + '.csv', index=False)
    # 保存最优解指标参数
    def compute_optimal(self, instance, information, opt_np, t_feas, matchings, mat_list, obj, res_mat, t_optimal, gap, t_model):
        col_name = ['ID', 'num_users', 'num_riders', 'num_drivers', 'num_SR', 'num_RT', 'num_TR', 'feas_time',
                    'feas_matches', 'feas_SR', 'feas_RT', 'feas_TR', 'feas_1', 'feas_2', 'feas_3',
                    'gap', 'opt_obj', 't_model', 'opt_time', 'opt_matched_r', 'opt_matched_d',
                    'opt_matches', 'opt_SR', 'opt_RT', 'opt_TR', 'opt_1', 'opt_2', 'opt_3']
        row = [instance, len(information.rider.keys())+len(information.driver.keys()), len(information.rider.keys()),
               len(information.driver.keys()), len(information.type_SR), len(information.type_RT),
               len(information.type_TR), t_feas, len(mat_list)]
        feas_sr, feas_rt, feas_tr, feas_1, feas_2, feas_3 = 0, 0, 0, 0, 0, 0
        for (s, j, i1, i2, i3) in mat_list:
            if matchings[s][s, j, i1, i2, i3]['type'] == 'SR':
                feas_sr += 1
            elif matchings[s][s, j, i1, i2, i3]['type'] == 'RT':
                feas_rt += 1
            else:
                feas_tr += 1
            if matchings[s][s, j, i1, i2, i3]['num_riders'] == 1:
                feas_1 += 1
            elif matchings[s][s, j, i1, i2, i3]['num_riders'] == 2:
                feas_2 += 1
            else:
                feas_3 += 1
        row += [feas_sr, feas_rt, feas_tr, feas_1, feas_2, feas_3, gap, obj, t_model, t_optimal]
        matched_r, matched_d = 0, 0
        opt_sr, opt_rt, opt_tr, opt_1, opt_2, opt_3 = 0, 0, 0, 0, 0, 0
        for (s, j, i1, i2, i3) in res_mat:
            matched_d += 1
            matched_r += matchings[s][s, j, i1, i2, i3]['num_riders']
            if matchings[s][s, j, i1, i2, i3]['type'] == 'SR':
                opt_sr += 1
            elif matchings[s][s, j, i1, i2, i3]['type'] == 'RT':
                opt_rt += 1
            else:
                opt_tr += 1
            if matchings[s][s, j, i1, i2, i3]['num_riders'] == 1:
                opt_1 += 1
            elif matchings[s][s, j, i1, i2, i3]['num_riders'] == 2:
                opt_2 += 1
            else:
                opt_3 += 1
        row += [matched_r, matched_d, len(res_mat), opt_sr, opt_rt, opt_tr, opt_1, opt_2, opt_3]
        opt_np.append(row)
        opt_df = pd.DataFrame(opt_np, columns=col_name)
        opt_df.to_csv('Results/optimal_small.csv', index=False)

    # 集中式匹配的指标参数
    def compute_centralized(self, instance, information, cen_np, t_feas, matchings, mat_list, obj, cen_res, t_cen, pre_r, pre_d):
        col_name = ['ID', 'num_users', 'num_riders', 'num_drivers', 'num_SR', 'num_RT', 'num_TR', 'feas_time',
                    'feas_matches', 'feas_SR', 'feas_RT', 'feas_TR', 'feas_1', 'feas_2', 'feas_3',
                    'cen_obj', 'cen_time', 'cen_matched_r', 'cen_matched_d',
                    'cen_matches', 'cen_SR', 'cen_RT', 'cen_TR', 'cen_1', 'cen_2', 'cen_3', 'broken_ratio',
                    'cen_broken', 'cen_broken_r', 'cen_broken_d',
                    'cen_broken_min', 'cen_broken_max', 'cen_broken_ave', 'cen_broken_std',
                    'cen_r_min', 'cen_r_max', 'cen_r_ave', 'cen_r_std',
                    'cen_d_min', 'cen_d_max', 'cen_d_ave', 'cen_d_std']
        row = [instance, len(information.rider.keys()) + len(information.driver.keys()), len(information.rider.keys()),
               len(information.driver.keys()), len(information.type_SR), len(information.type_RT),
               len(information.type_TR), t_feas, len(mat_list)]
        feas_sr, feas_rt, feas_tr, feas_1, feas_2, feas_3 = 0, 0, 0, 0, 0, 0
        for (s, j, i1, i2, i3) in mat_list:
            if matchings[s][s, j, i1, i2, i3]['type'] == 'SR':
                feas_sr += 1
            elif matchings[s][s, j, i1, i2, i3]['type'] == 'RT':
                feas_rt += 1
            else:
                feas_tr += 1
            if matchings[s][s, j, i1, i2, i3]['num_riders'] == 1:
                feas_1 += 1
            elif matchings[s][s, j, i1, i2, i3]['num_riders'] == 2:
                feas_2 += 1
            else:
                feas_3 += 1
        row += [feas_sr, feas_rt, feas_tr, feas_1, feas_2, feas_3, obj, t_cen]
        matched_r, matched_d = 0, 0
        opt_sr, opt_rt, opt_tr, opt_1, opt_2, opt_3 = 0, 0, 0, 0, 0, 0
        for (s, j, i1, i2, i3) in cen_res:
            matched_d += 1
            matched_r += matchings[s][s, j, i1, i2, i3]['num_riders']
            if matchings[s][s, j, i1, i2, i3]['type'] == 'SR':
                opt_sr += 1
            elif matchings[s][s, j, i1, i2, i3]['type'] == 'RT':
                opt_rt += 1
            else:
                opt_tr += 1
            if matchings[s][s, j, i1, i2, i3]['num_riders'] == 1:
                opt_1 += 1
            elif matchings[s][s, j, i1, i2, i3]['num_riders'] == 2:
                opt_2 += 1
            else:
                opt_3 += 1
        row += [matched_r, matched_d, len(cen_res), opt_sr, opt_rt, opt_tr, opt_1, opt_2, opt_3]
        ######## 计算每个用户在当前匹配结果下的成本节约值
        pi_r, pi_d = {}, {}
        for i in information.rider.keys():
            pi_r[i] = 0
        for j in information.driver.keys():
            pi_d[j] = 0
        for (s, j, i1, i2, i3) in cen_res:
            pi_d[j] = pre_d[j]['mat'][s, j, i1, i2, i3]
            for i in ({i1, i2, i3} - {0}):
                pi_r[i] = pre_r[i]['mat'][s, j, i1, i2, i3]
        ##### 计算阻塞率、阻塞数量等相关的指标
        broken_match, bro_r, bro_d = [], {}, {}
        for (s, j, i1, i2, i3) in (set(mat_list) - set(cen_res)):
            # 判断匹配是否为阻塞对
            isunstable = False
            if pre_d[j]['mat'][s, j, i1, i2, i3] > pi_d[j]:
                isunstable = True
                for i in ({i1, i2, i3} - {0}):
                    if pre_r[i]['mat'][s, j, i1, i2, i3] <= pi_r[i]:
                        isunstable = False
                        break
            if isunstable:         # if the match is a broken match
                broken_match.append((s, j, i1, i2, i3))
                # 计算每个用户阻塞时，最大阻塞的成本节约值
                delta_j = pre_d[j]['mat'][s, j, i1, i2, i3] - pi_d[j]
                if j not in bro_d.keys():
                    bro_d[j] = delta_j
                else:
                    if delta_j > bro_d[j]:
                        bro_d[j] = delta_j
                for i in ({i1, i2, i3} - {0}):
                    delta_i = pre_r[i]['mat'][s, j, i1, i2, i3] - pi_r[i]
                    if i not in bro_r.keys():
                        bro_r[i] = delta_i
                    else:
                        if delta_i > bro_r[i]:
                            bro_r[i] = delta_i
        # 计算所选择的集中式匹配被阻塞的概率
        num_ratio = 0
        for (s, j, i1, i2, i3) in cen_res:
            cap = {i1, i2, i3} & set(bro_r.keys())   # 找出阻塞的乘客
            if j in bro_d.keys() or len(cap) != 0:   #表明该匹配被阻塞
                num_ratio += 1
        broken_ratio = round(num_ratio / len(cen_res) * 100, 2)      # 被选中的匹配被阻塞的比率
        num_bro = len(broken_match)    # 阻塞对数量
        num_bro_r = len(bro_r.keys())      # 阻塞乘客数量
        num_bro_d = len(bro_d.keys())      # 阻塞司机数量
        bro_r_list, bro_d_list = [], []
        for i in bro_r.keys():
            bro_r_list.append(bro_r[i])
        for j in bro_d.keys():
            bro_d_list.append(bro_d[j])
        r_np = np.array(bro_r_list)
        d_np = np.array(bro_d_list)
        bro_np = np.array(bro_r_list + bro_d_list)
        row += [broken_ratio, num_bro, num_bro_r, num_bro_d, round(np.min(bro_np), 2), round(np.max(bro_np), 2),
                round(np.average(bro_np), 2), round(np.std(bro_np), 2),
                round(np.min(r_np), 2), round(np.max(r_np), 2), round(np.average(r_np), 2), round(np.std(r_np), 2),
                round(np.min(d_np), 2), round(np.max(d_np), 2), round(np.average(d_np), 2), round(np.std(d_np), 2)]
        cen_np.append(row)
        cen_df = pd.DataFrame(cen_np, columns=col_name)
        cen_df.to_csv('Results/centralized.csv', index=False)

    # The relaxed blocking searching algorithm指标参数
    def compute_appr(self, instance, information, ins_r, ins_d, res_np, matchings, mat_list, time_feas, obj, sol, iter, num_bro, mat_broken, pre_r, pre_d, run_time, num_theta):
        col_name = ['ID', 'num_users', 'num_riders', 'num_drivers', 'num_SR', 'num_RT', 'num_TR',
                    'num_matches', 'num_SR', 'num_RT', 'num_TR','num_1', 'num_2', 'num_3',
                    'Mr_ave', 'Mr_std', 'Md_ave', 'Md_std', 'Mu_ave', 'Mu_std', 'time_feasible',
                    'appr_obj', 'appr_time', 'appr_iter', 'appr_theta', 'appr_matches',
                    'appr_matched_r', 'appr_matched_d', 'appr_SR', 'appr_RT', 'appr_TR', 'appr_1', 'appr_2', 'appr_3',
                    'broken_ratio', 'broken', 'broken_r', 'broken_d', 'broken_min', 'broken_max', 'broken_ave', 'broken_std',
                    'r_min', 'r_max', 'r_ave', 'r_std', 'd_min', 'd_max', 'd_ave', 'd_std']
        row = [instance, len(ins_r)+len(ins_d), len(ins_r), len(ins_d), len(information.type_SR),
               len(information.type_RT), len(information.type_TR), len(mat_list)]
        ##### 各个类型匹配数量
        num_sr, num_rt, num_tr, num_1, num_2, num_3 = 0, 0, 0, 0, 0, 0
        for (s, j, i1, i2, i3) in mat_list:
            if matchings[s][s, j, i1, i2, i3]['type'] == 'SR':
                num_sr += 1
            elif matchings[s][s, j, i1, i2, i3]['type'] == 'RT':
                num_rt += 1
            else:
                num_tr += 1
            if matchings[s][s, j, i1, i2, i3]['num_riders'] == 1:
                num_1 += 1
            elif matchings[s][s, j, i1, i2, i3]['num_riders'] == 2:
                num_2 += 1
            else:
                num_3 += 1
        r_M, d_M = [], []
        for i in pre_r.keys():
            r_M.append(len(pre_r[i]['sort']))
        for j in pre_d.keys():
            d_M.append(len(pre_d[j]['sort']))
        u_M = r_M + d_M
        Mr_ave, Mr_std = np.average(np.array(r_M)), np.std(np.array(r_M))
        Md_ave, Md_std = np.average(np.array(d_M)), np.std(np.array(d_M))
        Mu_ave, Mu_std = np.average(np.array(u_M)), np.std(np.array(u_M))
        row += [num_sr, num_rt, num_tr, num_1, num_2, num_3, Mr_ave, Mr_std, Md_ave, Md_std, Mu_ave, Mu_std,
                time_feas, obj, run_time, iter, num_theta, len(sol)]
        ###### 选中匹配对应的用户数量和各个类型匹配的数量
        appr_sr, appr_rt, appr_tr, appr_1, appr_2, appr_3 = 0, 0, 0, 0, 0, 0
        matched_r, matched_d = 0, 0
        pi_r, pi_d = {}, {}
        for i in ins_r:
            pi_r[i] = 0
        for j in ins_d:
            pi_d[j] = 0
        for (s, j, i1, i2, i3) in sol:
            matched_d += 1
            matched_r += matchings[s][s, j, i1, i2, i3]['num_riders']
            if matchings[s][s, j, i1, i2, i3]['type'] == 'SR':
                appr_sr += 1
            elif matchings[s][s, j, i1, i2, i3]['type'] == 'RT':
                appr_rt += 1
            else:
                appr_tr += 1
            if matchings[s][s, j, i1, i2, i3]['num_riders'] == 1:
                appr_1 += 1
            elif matchings[s][s, j, i1, i2, i3]['num_riders'] == 2:
                appr_2 += 1
            else:
                appr_3 += 1
            pi_d[j] = pre_d[j]['mat'][s, j, i1, i2, i3]
            for i in ({i1, i2, i3} - {0}):
                pi_r[i] = pre_r[i]['mat'][s, j, i1, i2, i3]
        row += [matched_r, matched_d, appr_sr, appr_rt, appr_tr, appr_1, appr_2, appr_3]
        ###### 计算阻塞指标
        if num_bro > 0:
            bro_r, bro_d = {}, {}
            for (s, j, i1, i2, i3) in mat_broken:
                delta_j = pre_d[j]['mat'][s, j, i1, i2, i3] - pi_d[j]
                if j not in bro_d.keys():
                    bro_d[j] = delta_j
                else:
                    if delta_j > bro_d[j]:
                        bro_d[j] = delta_j
                for i in ({i1, i2, i3} - {0}):
                    delta_i = pre_r[i]['mat'][s, j, i1, i2, i3] - pi_r[i]
                    if i not in bro_r.keys():
                        bro_r[i] = delta_i
                    else:
                        if delta_i > bro_r[i]:
                            bro_r[i] = delta_i
            # 计算所选择的集中式匹配被阻塞的概率
            num_ratio = 0
            for (s, j, i1, i2, i3) in sol:
                cap = {i1, i2, i3} & set(bro_r.keys())  # 找出阻塞的乘客
                if j in bro_d.keys() or len(cap) != 0:  # 表明该匹配被阻塞
                    num_ratio += 1
            broken_ratio = round(num_ratio / len(sol) * 100, 2)  # 被选中的匹配被阻塞的比率
            num_bro_r = len(bro_r.keys())
            num_bro_d = len(bro_d.keys())
            bro_r_list, bro_d_list = [], []
            for i in bro_r.keys():
                bro_r_list.append(bro_r[i])
            for j in bro_d.keys():
                bro_d_list.append(bro_d[j])
            r_np = np.array(bro_r_list)
            d_np = np.array(bro_d_list)
            bro_np = np.array(bro_r_list + bro_d_list)
            row += [broken_ratio, num_bro, num_bro_r, num_bro_d, round(np.min(bro_np), 2), round(np.max(bro_np), 2),
                    round(np.average(bro_np), 2), round(np.std(bro_np), 2),
                    round(np.min(r_np), 2), round(np.max(r_np), 2), round(np.average(r_np), 2), round(np.std(r_np), 2),
                    round(np.min(d_np), 2), round(np.max(d_np), 2), round(np.average(d_np), 2), round(np.std(d_np), 2)]
        else:
            row += [0, num_bro, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        res_np.append(row)
        res_df = pd.DataFrame(res_np, columns=col_name)
        res_df.to_csv('Results/approximate.csv', index=False)

    # The feasibility and blocking searching algorithm指标参数
    def compute_exact(self, instance, information, ins_r, ins_d, res_np, matchings, mat_list, time_feasible, obj, sol, iter, run_time, num_theta):
        col_name = ['ID', 'num_users', 'num_riders', 'num_drivers', 'num_SR', 'num_RT', 'num_TR',
                    'num_matches', 'num_SR', 'num_RT', 'num_TR', 'num_1', 'num_2', 'num_3', 'time_feasible',
                    'exact_obj', 'exact_time', 'exact_iter',
                    'exact_theta', 'exact_matches', 'exact_matched_r', 'exact_matched_d',
                    'exact_SR', 'exact_RT', 'exact_TR', 'exact_1', 'exact_2', 'exact_3']
        row = [instance, len(ins_r)+len(ins_d), len(ins_r), len(ins_d), len(information.type_SR),
               len(information.type_RT), len(information.type_TR), len(mat_list)]
        num_sr, num_rt, num_tr, num_1, num_2, num_3 = 0, 0, 0, 0, 0, 0,
        for (s, j, i1, i2, i3) in mat_list:
            if matchings[s][s, j, i1, i2, i3]['type'] == 'SR':
                num_sr += 1
            elif matchings[s][s, j, i1, i2, i3]['type'] == 'RT':
                num_rt += 1
            else:
                num_tr += 1
            if matchings[s][s, j, i1, i2, i3]['num_riders'] == 1:
                num_1 += 1
            elif matchings[s][s, j, i1, i2, i3]['num_riders'] == 2:
                num_2 += 1
            else:
                num_3 += 1
        row += [num_sr, num_rt, num_tr, num_1, num_2, num_3, time_feasible, obj, run_time, iter, num_theta, len(sol)]
        exact_sr, exact_rt, exact_tr, exact_1, exact_2, exact_3 = 0, 0, 0, 0, 0, 0
        matched_r, matched_d = 0, 0
        for (s, j, i1, i2, i3) in sol:
            matched_d += 1
            matched_r += matchings[s][s, j, i1, i2, i3]['num_riders']
            if matchings[s][s, j, i1, i2, i3]['type'] == 'SR':
                exact_sr += 1
            elif matchings[s][s, j, i1, i2, i3]['type'] == 'RT':
                exact_rt += 1
            else:
                exact_tr += 1
            if matchings[s][s, j, i1, i2, i3]['num_riders'] == 1:
                exact_1 += 1
            elif matchings[s][s, j, i1, i2, i3]['num_riders'] == 2:
                exact_2 += 1
            else:
                exact_3 += 1
        row += [matched_r, matched_d, exact_sr, exact_rt, exact_tr, exact_1, exact_2, exact_3]
        res_np.append(row)
        res_df = pd.DataFrame(res_np, columns=col_name)
        res_df.to_csv('Results/exact.csv', index=False)







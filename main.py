import numpy as np
import pandas as pd
import Tools as tl
import time
import Matching as mtg
import Algorithm as alg
import Instance as ins

# 设置灵敏性参数
def instance_factor(i, factors):
    if factors['vot'][i-1] == 'L':
        alpha = 15 / 3600
    else:
        alpha = 30 / 3600
    if factors['pick'][i-1] == 'L':
        flex_pick = 10 * 60
    else:
        flex_pick = 20 * 60
    if factors['trip'][i-1] == 'L':
        flex_trip_r, flex_trip_d = 0.4, 0.2
    else:
        flex_trip_r, flex_trip_d = 0.6, 0.3
    return alpha, flex_pick, flex_trip_r, flex_trip_d



if __name__ == "__main__":
    ############# 参数设置
    parameters = tl.Parameters()
    factors = pd.read_csv('Instance/factors_small.csv')

    # 存储所有算例的结果
    optimal_np = []
    appr_np = []
    exact_np = []
    cen_np = []

    ############### 算例
    instance_list = list(range(1, 3))
    for a in instance_list:
        print('------------------算例{}的实验结果-------------------'.format(a))
        s_1 = time.time()
        # 读取算例a中的相应的信息，并进行预处理，返回信息参数对象、乘客列表、司机列表
        information, r_ins, d_ins = tl.instance_preprocess(a, parameters, 'Instance/instance' + str(a) + '.csv')
        alpha, flex_pick, flex_trip_r, flex_trip_d = instance_factor(a, factors)
        # 根据灵敏参数计算对应的广义成本和时间窗约束
        information.compute_gencost(alpha)
        information.compute_time(flex_pick, parameters.flex_trip_max, flex_trip_r, flex_trip_d)
        e_1 = time.time()
        print('预处理数据的时间为{}分钟'.format(round((e_1 - s_1) / 60, 4)))

        ################# 首先找到所有的可行匹配并对所有的可行匹配进行预处理
        s_feas = time.time()
        Feasible_match = mtg.Find_All_Matches(information, r_ins, d_ins)
        matchings, mat_list = Feasible_match.find_all_matches()
        e_feas = time.time()
        time_feas = round((e_feas - s_feas) / 60, 4)
        s_sort = time.time()
        pre_r, pre_d, rins_new, dins_new = Feasible_match.preference_sort(matchings, mat_list)
        e_sort = time.time()
        print('找到所有的可行匹配需要{}min，可行匹配数量为{}，预处理和排序所有匹配需要{}分钟'.format(
            time_feas, len(mat_list), round((e_sort - s_sort) / 60, 4)))


        ################ 求解最优的稳定匹配结果
        print('===========最优稳定匹配============')
        s_t = time.time()
        opt_obj, opt_res, gap, t_model = mtg.optimal_stable(matchings, mat_list, rins_new, dins_new, pre_r, pre_d)
        e_t = time.time()
        time_optimal = round((e_t-s_t)/60, 4)
        print('run time: {} minutes'.format(time_optimal))
        # tl.Save_Result().save_match(a, opt_res, matchings, 'optimal')
        # tl.Save_Result().compute_optimal(a, information, optimal_np, time_feas, matchings, mat_list, opt_obj, opt_res, time_optimal, gap, t_model)



        ###################### 求解集中式最优解
        print('==========集中式匹配=============')
        s_t = time.time()
        cen_obj, cen_res = mtg.centralized_matching(matchings, mat_list, rins_new, dins_new)
        e_t = time.time()
        time_centralized = round((e_t-s_t)/60, 4)
        print('run time: {} minutes'.format(time_centralized))
        # tl.Save_Result().save_match(a, cen_res, matchings, 'centralized')
        # tl.Save_Result().compute_centralized(a, information, cen_np, time_feas, matchings, mat_list, cen_obj, cen_res, time_centralized, pre_r, pre_d)




        col_row = alg.Column_Row(rins_new, dins_new, matchings, mat_list, pre_r, pre_d)
        ################ The relaxed blocking searching algorithm
        print('==========近似稳定匹配=============')
        s_t = time.time()
        appr_obj, appr_sol, appr_iter, num_broken, mat_broken, appr_num_theta = col_row.approximate('greedy')
        e_t = time.time()
        appr_time = round((e_t - s_t) / 60, 4)
        print('run time: {} minutes'.format(appr_time))
        print('最终选择了{}个匹配，目标函数值为{}，迭代次数为{}，松弛了{}稳定性约束'.format(len(appr_sol), appr_obj, appr_iter, num_broken))
        # tl.Save_Result().save_match(a, appr_sol, matchings, 'approximate_0')
        # tl.Save_Result().compute_appr(a, information, r_ins, d_ins, appr_np, matchings, mat_list, time_feas, appr_obj,
        #                               appr_sol, appr_iter, num_broken, mat_broken, pre_r, pre_d, appr_time, appr_num_theta)



        ################# 精确行列生成框架
        print('===========精确稳定匹配============')
        s_t = time.time()
        exa_obj, exa_sol, exa_iter, exa_num_theta = col_row.exact('greedy')
        e_t = time.time()
        exa_time = round((e_t - s_t) / 60, 4)
        print('run time: {} minutes'.format(exa_time))
        print('最终选择了{}个匹配，目标函数值为{}，迭代次数为{}'.format(len(exa_sol), exa_obj, exa_iter))
        # tl.Save_Result().save_match(a, exa_sol, matchings, 'exact')
        # tl.Save_Result().compute_exact(a, information, r_ins, d_ins, exact_np, matchings, mat_list, time_feas,
        #                                exa_obj, exa_sol, exa_iter, exa_time, exa_num_theta)























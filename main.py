import numpy as np
import pandas as pd
import Tools as tl
import time
import Matching as mtg
import Algorithm as alg
import Instance as ins






if __name__ == "__main__":
    ############# 参数设置
    parameters = tl.Parameters()
    factors = pd.read_csv('Instance/factors_small.csv')
    price_scaling = 1.0        # ridesharing价格缩放比例，一般为1，实验可以验证0.5，1.5，2.0
    omega = -10000     # 表示加权目标函数的系数，取值为-10000，-100，和“double”配合使用
    # RSS算法RRMP问题的目标函数：double（加权目标函数），inf（只考虑最小化阻塞对的数量），zero（表示只考虑最大化成本节约值），platform（最大化匹配数量，加权函数）
    rss_obj_choice = 'double'
    bfs_obj_choice = 'welfare'     # BFS算法RMP问题的目标函数：platform（最大化匹配用户数量）   welfare（最大化社会福利值）
    dynamic_instance_size = 'large'     # small(先BFS在RSS)   large（直接RSS）

    # 存储所有算例的结果
    optimal_np = []
    appr_np = []
    exact_np = []
    cen_np = []
    result_np = []
    ############### 算例
    instance_list = list(range(30, 31))
    rss_list = [5, 9, 11, 14, 15, 16, 21, 22, 24, 26, 29]      # [5, 9, 11, 14, 15, 16, 21, 22, 24, 26, 29]
    for a in instance_list:
        print('------------------算例{}的实验结果-------------------'.format(a))
        s_1 = time.time()
        # 读取算例a中的相应的信息，并进行预处理，返回信息参数对象、乘客列表、司机列表
        information, r_ins, d_ins = tl.instance_preprocess(a, parameters, 'Instance/instance' + str(a) + '.csv')
        alpha, flex_pick, flex_trip_r, flex_trip_d = tl.instance_factor(a, factors)
        # 根据灵敏参数计算对应的广义成本和时间窗约束
        information.compute_gencost(alpha)
        information.compute_time(flex_pick, parameters.flex_trip_max, flex_trip_r, flex_trip_d)
        e_1 = time.time()
        print('预处理数据的时间为{}分钟'.format(round((e_1 - s_1) / 60, 4)))


        # ################## 分析用户的行为
        # alg.Behavior_Analysis(a, information, r_ins, d_ins).analysis_main(result_np, dynamic_instance_size)
        # result_df = pd.DataFrame(result_np,
        #                          columns=['instance', 'num_r', 'num_d', 'day', 'centralized', 'approximate', 'dynamic',
        #                                   'prt_appr', 'prt_dyn', 'empty', 'appr_remain_r', 'appr_remain_d',
        #                                   'cen_remain_r', 'cen_remain_d', 'appr_fix', 'cen_fix']
        #                          )
        # result_df.to_csv('Results/dynamic_large.csv', index=False)



        s_feas = time.time()
        Feasible_match = mtg.Recursive_Match_Genneration(information, r_ins, d_ins, price_scaling)
        matchings, mat_list = Feasible_match.find_all_matches()
        e_feas = time.time()
        time_feas = round((e_feas - s_feas) / 60, 4)

        for s in matchings.keys():
            print(len(matchings[s].keys()))
        print(len(mat_list))
        print('找到所有的可行匹配需要{}min'.format(time_feas))
        print('----------------------------------')



        ################# 首先找到所有的可行匹配并对所有的可行匹配进行预处理
        # s_feas = time.time()


        # Feasible_match = mtg.Find_All_Matches(information, r_ins, d_ins, price_scaling)
        # matchings, mat_list = Feasible_match.find_all_matches()
        # for s in matchings.keys():
        #     print(len(matchings[s].keys()))
        # print(len(mat_list))



        # e_feas = time.time()
        # time_feas = round((e_feas - s_feas) / 60, 4)
        # s_sort = time.time()
        # pre_r, pre_d, rins_new, dins_new = Feasible_match.preference_sort(matchings, mat_list)
        # e_sort = time.time()
        # print('找到所有的可行匹配需要{}min，可行匹配数量为{}，预处理和排序所有匹配需要{}分钟'.format(
        #     time_feas, len(mat_list), round((e_sort - s_sort) / 60, 4)))


        # # ################ 求解最优的稳定匹配结果
        # print('===========最优稳定匹配============')
        # s_t = time.time()
        # opt_obj, opt_res, gap, t_model = mtg.optimal_stable(matchings, mat_list, rins_new, dins_new, pre_r, pre_d)
        # e_t = time.time()
        # time_optimal = round((e_t-s_t)/60, 4)
        # print('run time: {} minutes'.format(time_optimal))
        #tl.Save_Result().save_match(a, opt_res, matchings, 'optimal')
        # tl.Save_Result().compute_optimal(a, information, optimal_np, time_feas, matchings, mat_list, opt_obj, opt_res, time_optimal, gap, t_model)



        ###################### 求解集中式最优解
        # print('==========集中式匹配=============')
        # s_t = time.time()
        # cen_obj, cen_res = mtg.centralized_matching(matchings, mat_list, rins_new, dins_new)
        # e_t = time.time()
        # time_centralized = round((e_t-s_t)/60, 4)
        # print('run time: {} minutes'.format(time_centralized))
        # tl.Save_Result().save_match(a, cen_res, matchings, 'centralized')
        # tl.Save_Result().compute_centralized(a, information, cen_np, time_feas, matchings, mat_list, cen_obj, cen_res, time_centralized, pre_r, pre_d)




        # col_row = alg.Column_Row(rins_new, dins_new, matchings, mat_list, pre_r, pre_d)
        # ############## The relaxed blocking searching algorithm
        # print('==========近似稳定匹配=============')
        # s_t = time.time()
        # appr_obj, appr_sol, appr_iter, num_broken, mat_broken, appr_num_theta = col_row.approximate(
        #     'greedy', rss_obj_choice, omega, matchings
        # )
        # e_t = time.time()
        # appr_time = round((e_t - s_t) / 60, 4)
        # print('run time: {} minutes'.format(appr_time))
        # print('最终选择了{}个匹配，目标函数值为{}，迭代次数为{}，松弛了{}稳定性约束'.format(len(appr_sol), appr_obj,
        #                                                                                  appr_iter, num_broken))
        # tl.Save_Result().save_match(a, appr_sol, matchings, 'approximate')
        # tl.Save_Result().compute_appr(a, information, r_ins, d_ins, appr_np, matchings, mat_list, time_feas, appr_obj,
        #                               appr_sol, appr_iter, num_broken, mat_broken, pre_r, pre_d, appr_time, appr_num_theta)


        ################ 精确行列生成框架
        # print('===========精确稳定匹配============')
        # s_t = time.time()
        # exa_obj, exa_sol, exa_iter, exa_num_theta = col_row.exact('greedy', bfs_obj_choice, matchings)
        # e_t = time.time()
        # exa_time = round((e_t - s_t) / 60, 4)
        # print('run time: {} minutes'.format(exa_time))
        # print('最终选择了{}个匹配，目标函数值为{}，迭代次数为{}'.format(len(exa_sol), exa_obj, exa_iter))
        # tl.Save_Result().save_match(a, exa_sol, matchings, 'objective')
        # tl.Save_Result().compute_exact(a, information, r_ins, d_ins, exact_np, matchings, mat_list, time_feas,
        #                                exa_obj, exa_sol, exa_iter, exa_time, exa_num_theta)
        #



        ############### 动态环境稳定性验证，无稳定匹配解的算例直接使用RSS算法求解近似解
        # if a in rss_list:
        #     ############## The relaxed blocking searching algorithm
        #     print('==========近似稳定匹配=============')
        #     s_t = time.time()
        #     appr_obj, appr_sol, appr_iter, num_broken, mat_broken, appr_num_theta = col_row.approximate(
        #         'greedy', rss_obj_choice, omega, matchings
        #     )
        #     e_t = time.time()
        #     appr_time = round((e_t - s_t) / 60, 4)
        #     print('run time: {} minutes'.format(appr_time))
        #     print('最终选择了{}个匹配，目标函数值为{}，迭代次数为{}，松弛了{}稳定性约束'.format(len(appr_sol), appr_obj, appr_iter, num_broken))
        #     tl.Save_Result().save_match(a, appr_sol, matchings, 'objective')
        #     # tl.Save_Result().compute_appr(a, information, r_ins, d_ins, appr_np, matchings, mat_list, time_feas, appr_obj,
        #     #                               appr_sol, appr_iter, num_broken, mat_broken, pre_r, pre_d, appr_time, appr_num_theta)
        #     tl.Save_Result().compute_exact(a, information, r_ins, d_ins, exact_np, matchings, mat_list, time_feas,
        #                                    appr_obj, appr_sol, appr_iter, appr_time, appr_num_theta)
        # else:
        #     ################ 精确行列生成框架
        #     print('===========精确稳定匹配============')
        #     s_t = time.time()
        #     exa_obj, exa_sol, exa_iter, exa_num_theta = col_row.exact('greedy', bfs_obj_choice, matchings)
        #     e_t = time.time()
        #     exa_time = round((e_t - s_t) / 60, 4)
        #     print('run time: {} minutes'.format(exa_time))
        #     print('最终选择了{}个匹配，目标函数值为{}，迭代次数为{}'.format(len(exa_sol), exa_obj, exa_iter))
        #     tl.Save_Result().save_match(a, exa_sol, matchings, 'objective')
        #     tl.Save_Result().compute_exact(a, information, r_ins, d_ins, exact_np, matchings, mat_list, time_feas,
        #                                    exa_obj, exa_sol, exa_iter, exa_time, exa_num_theta)























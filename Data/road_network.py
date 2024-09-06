import pandas as pd
import Tools as tl
import datetime

def driver_station():
    '''
    司机和站点的预处理，根据司机的行程时间、时间窗
    t(o_j,v)+t(v,d_j)<=T_j^max, T_j^-+t(o_j,v)+t(v,d_j)<=T_j^+
    :return: 司机-站点的信息
    '''
    list0 = []
    for k in driver.keys():
        d = driver[k]
        for s in (set(station.keys()) - {0}):
            # 司机起点到站点的时间
            t_ov = tl.car_time(d.org_lat, d.org_lon, station[s].lat, station[s].lon)
            # 站点到司机终点的时间
            t_vd = tl.car_time(station[s].lat, station[s].lon, d.des_lat, d.des_lon)
            if t_ov + t_vd <= d.Tmax and d.departure + t_ov + t_vd <= d.arrival:
                # [司机，站点，起点—站点时间，站点—终点的时间]
                list0.append([k, s, t_ov, t_vd])
    df = pd.DataFrame(list0, columns=['driver_id', 'station_id', 'o_v', 'v_d'])
    df.to_csv('driver_station.csv', index=False)

def rider_station():
    '''
    乘客和站点的预处理，根据乘客的行程时间、时间窗
    起点大于1000米：t(o_i,v)+t^P(v,B_i)+t^W(B_i,d_i)<=T_i^max, T_i^-+t(o_i,v)+t^P(v,B_i)+t^W(B_i,d_i)<=T_i^+
    终点大于1000米：t^W(o_i,A_i)+t^P(A_i,v)+t(v,d_i)<=T_i^max, T_i^-+t^W(o_i,A_i)+t^P(A_i,v)+t(v,d_i)<=T_i^+
    :return: 乘客-站点的信息
    '''
    list0 = []
    for i in rider.keys():
        r = rider[i]
        # RT乘客,起点大于1000米
        if i in type_RT:
            for s in (set(station.keys()) - {0}):
                # 要求起点到站点的距离要小于站点到终点的距离
                if tl.dist(r.org_lat, r.org_lon, station[s].lat, station[s].lon) \
                        <= tl.dist(station[s].lat, station[s].lon, r.des_lat, r.des_lon):
                    # 乘客起点到站点的时间
                    t_ov = tl.car_time(r.org_lat, r.org_lon, station[s].lat, station[s].lon)
                    t_p_vB = sta_sta[s, r.des_sta].trans_duration
                    if t_ov + t_p_vB + r.des_time <= r.Tmax and r.departure + t_ov + t_p_vB + r.des_time <= r.arrival:
                        # [RT乘客，站点，起点——站点，0]
                        list0.append([i, s, t_ov, 0])
        # TR乘客，终点大于1000米
        elif i in type_TR:
            for s in (set(station.keys()) - {0}):
                if tl.dist(r.org_lat, r.org_lon, station[s].lat, station[s].lon)\
                        >= tl.dist(station[s].lat, station[s].lon, r.des_lat, r.des_lon):
                    # 站点到乘客终点的时间
                    t_vd = tl.car_time(station[s].lat, station[s].lon, r.des_lat, r.des_lon)
                    t_p_Av = sta_sta[r.org_sta, s].trans_duration
                    if r.org_dis + t_p_Av + t_vd <= r.Tmax and r.departure + r.org_dis + t_p_Av + t_vd <= r.arrival:
                        # [乘客，站点，0，站点——终点]
                        list0.append([i, s, 0, t_vd])
    df = pd.DataFrame(list0, columns=['rider_id', 'station_id', 'o_v', 'v_d'])
    df.to_csv('rider_station.csv', index=False)



#######################################################
#######################################################
def func_SR(r, d):
    a = False
    t_oo = tl.car_time(d.org_lat, d.org_lon, r.org_lat, r.org_lon)
    t_dd = tl.car_time(r.des_lat, r.des_lon, d.des_lat, d.des_lon)
    if t_oo + r.drive_time + t_dd <= d.Tmax:
        if max(d.departure + t_oo, r.departure) + r.drive_time <= min(r.arrival, d.arrival - t_dd):
            a = True
    return a, t_oo, t_dd

def func_RT(i, j, s, r, d, t_oo):
    a = False
    if t_oo + rid_sta[i, s].o_v + dri_sta[j, s].v_d <= d.Tmax:
        if max(d.departure + t_oo, r.departure) + rid_sta[i, s].o_v <= \
                min(r.arrival - r.des_time - sta_sta[s, r.des_sta].trans_duration, d.arrival - dri_sta[j, s].v_d):
            a = True
    return a

def func_TR(i, j, s, r, d, t_dd):
    a = False
    if dri_sta[j, s].o_v + rid_sta[i, s].v_d + t_dd <= d.Tmax:
        if max(d.departure + dri_sta[j, s].o_v, r.departure + r.org_time + sta_sta[r.org_sta, s].trans_duration) + rid_sta[i, s].v_d \
                <= min(r.arrival, d.arrival - t_dd):
            a = True
    return a

def rider_driver():
    '''
    乘客和司机的预处理，判断司机-乘客是否能够在一个站点满足时间约束
    SR：t(o_j,o_i)+t(o_i,d_i)+t(d_i,d_j)<=T_j^max,
        max{T_j^-+t(o_j,o_i),T_i^-}+t(o_i,d_i)<=min{T_i^+,T_j^+-t(d_i,d_j)}
    RT: t(o_j,o_i)+t(o_i,v)+t(v,d_j)<=T_j^max
        t(o_i,v)+t_p(v,B_i)+t_w(B_i,d_i)<=T_i^max (乘客i预处理得到的站点以满足这一条件)
        max{T_j^-+t(o_j,o_i),T_i^-}+t(o_i,v)<=min{T_i^+-t_p(v,B_i)-t_w(B_i,d_i),T_j^+-t(v,d_j)}
    TR: t(o_j,v)+t(v,d_i)+t(d_i,d_j)<=T_j^max
        t_w(o_i,A_i)+t_p(A_i,v)+t(v,d_i)<=T_i^max (乘客i预处理得到的站点以满足这一条件)
        max{T_j^-+t(o_j,v),T_i^-+t_w(o_i,A_i)+t_p(A_i,v)}+t(v,d_i)<=min{T_i^+,T_j^+-t(d_i,d_j)}
    :return: 乘客-司机的信息
    '''
    list0 = []
    for i in rider.keys():
        r = rider[i]
        for j in driver.keys():
            d = driver[j]
            # 计算起点到起点，终点到终点的距离，并判断乘客和司机SR匹配时间上是否可行
            con_SR, t_oo, t_dd = func_SR(r, d)
            # 如果为SR乘客，只需判断一个条件
            if i in type_SR:
                if con_SR == True:
                    list0.append([i, j, t_oo, t_dd])
            # 如果为其他乘客，除了判断SR匹配条件还需判断RT/TR的条件
            else:
                if con_SR == True:
                    list0.append([i, j, t_oo, t_dd])
                    continue
                else:
                    # RT乘客，判断和站点s构成RT匹配时间上是否可行
                    if i in type_RT:
                        # 能够共同换乘的站点。包括站点0
                        cap_sta = list(set(d.station) & set(r.station))
                        cap_sta.remove(0)
                        if len(cap_sta) != 0:
                            for s in cap_sta:
                                con_RT = func_RT(i, j, s, r, d, t_oo)
                                if con_RT == True:
                                    # 找到一个合适在时间上满足RT匹配的站点，则认为该司机和乘客可以构成匹配，并跳出改循环
                                    list0.append([i, j, t_oo, t_dd])
                                    break
                    # TR乘客，判断和站点s构成TRT匹配时间上是否可行
                    elif i in type_TR:
                        cap_sta = list(set(d.station) & set(r.station))
                        cap_sta.remove(0)  # 删除公共可选的站点0
                        if len(cap_sta) != 0:
                            for s in cap_sta:
                                con_TR = func_TR(i, j, s, r, d, t_dd)
                                if con_TR == True:
                                    # 找到一个合适在时间上满足TR匹配的站点，则认为该司机和乘客可以构成匹配，并跳出改循环
                                    list0.append([i, j, t_oo, t_dd])
                                    break
    df = pd.DataFrame(list0, columns=['rider_id', 'driver_id', 'o_o', 'd_d'])
    df.to_csv('rider_driver.csv', index=False)



if __name__=="__main__":
    # 根据时间约束对数据进行预处理
    parameters = tl.Parameters()
    W_max = parameters.W_max           # 米
    v_c = parameters.v_c                # 开车的速度，米/秒
    num_drivers = parameters.total_drivers
    num_riders = parameters.total_riders

    start = datetime.datetime.now()
    #######################################################
    # 读取相关信息
    r_ins = list(range(1, num_riders+1))
    rider = tl.DataReader().rider_reader('rider.csv', r_ins)
    d_ins = list(range(1, num_drivers+1))
    driver = tl.DataReader().driver_reader('driver.csv', d_ins)
    station = tl.DataReader().station_reader('station.xls')
    sta_sta = tl.DataReader().stasta_reader('station-station.xls')


    #######################################################
    # 乘客分类， driver-station, rider-station
    type_SR, type_RT, type_TR = tl.type_rider(rider, W_max)
    print('各类型乘客的数量分别为：SR（{}），RT（{}），TR（{}）'.format(
        len(type_SR), len(type_RT), len(type_TR))
    )
    # 司机——站点，预处理，生成司机起点—站点，站点—司机终点的时间段
    driver_station()
    # 乘客——站点，预处理，生成乘客起点—站点，站点—乘客终点的时间段
    rider_station()


    #######################################################
    #######################################################
    # 读取之前生成的乘客、司机——站点之间的信息
    dri_sta = tl.DataReader().driver_station_reader('driver_station.csv', d_ins)
    rid_sta = tl.DataReader().rider_station_reader('rider_station.csv', r_ins)
    # 将乘客-站点，司机-站点预处理的信息传到站点、乘客、司机对应的对象中
    # for s in station.keys():
    #     station[s].pick_rider(rid_sta, r_ins)
    #     station[s].pick_driver(dri_sta, d_ins)
    valid_sta = list(range(1, 285))
    for r in rider.keys():
        rider[r].pick_station(rid_sta, valid_sta)
    for d in driver.keys():
        driver[d].pick_station(dri_sta, valid_sta)
    # 司机起点-乘客起点，乘客终点-司机终点
    rider_driver()

    #######################################################
    end = datetime.datetime.now()
    print(len(driver.keys()), '个司机', len(rider.keys()), '个乘客',
          '生成除乘客与乘客之间关系的路网需要的时间', (end-start).total_seconds()/60)
    # 5000 个司机 10000 个乘客 生成除乘客与乘客之间关系的路网需要的时间 20.76min



























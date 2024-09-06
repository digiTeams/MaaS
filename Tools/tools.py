import numpy as np
import Tools as tl

def dist(lat1, lng1, lat2, lng2):
    '''
    根据经纬度计算任意两点之间的开车距离，返回距离单位为米，且保留整小数
    :param lat1: 第一个点的纬度
    :param lng1: 第一个点的经度
    :param lat2: 第二个点的纬度
    :param lng2: 第二个点的经度
    :return: 开车距离，输出单位 米
    '''
    lat1, lng1, lat2, lng2 = map(np.radians, (lat1, lng1, lat2, lng2))
    radius = 6371  # Earth's radius taken from google
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = np.sin(lat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(lng / 2) ** 2
    h = 2 * radius * np.arcsin(np.sqrt(d))  # 两点之间的球面距离
    h = h * 1.3  # 开车距离，球面距离的1.3倍
    return int(h * 1000)


def car_time(lat1, lng1, lat2, lng2):
    '''
    :param lat1: 第一个点的纬度
    :param lng1: 第一个点的经度
    :param lat2: 第二个点的纬度
    :param lng2: 第二个点的经度
    :return: 意两点开车时间，输出单位 秒
    '''
    h = dist(lat1, lng1, lat2, lng2)
    v = tl.Parameters().v_c
    t = h / v
    return int(t)


def type_rider(rider: dict, W_max):
    '''
    根据最大可接受步行距离对乘客进行分类
    :param rider: 所有乘客的信息
    :param W_max: 最大可接受步行距离
    :return: 每个类型的乘客编号集合
    '''
    type_SR = set()
    type_RT = set()
    type_TR = set()
    for i in rider.keys():
        r = rider[i]
        if r.org_sta == r.des_sta:
            type_SR.add(i)
        else:
            if r.org_dis <= W_max and r.des_dis > W_max:
                type_TR.add(i)
            elif r.org_dis > W_max and r.des_dis <= W_max:
                type_RT.add(i)
            else:
                type_SR.add(i)
    return type_SR, type_RT, type_TR

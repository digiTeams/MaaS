

'''参数类'''
class Parameters:
    def __init__(self):
        self.W_max = 1000             # 最大可接受步行距离，米
        self.v_c = 7                  # 开车的速度，米/秒
        self.v_w = 1                  # 步行的速度，米/秒
        self.total_drivers = 5000     # 总计选中的司机数
        self.total_riders = 10000     # 总计选中的乘客数
        self.cost_car = 1.5 / 1000    # 开车的成本，元/米
        self.taxi_cost = 1.9 / 1000   # 出租车收费，元/m
        self.taxi_start = 9           # 元
        # 灵敏性参数设置
        self.flex_trip_r = 0.6        # 乘客的灵活性参数（标准）
        self.flex_trip_d = 0.3        # 司机的灵活性参数（标准）
        self.flex_pick = 20 * 60      # 灵活最早接取时间，秒（标准）
        self.flex_trip_max = 30 * 60  # 灵活trip duration时间，秒
        self.r_d_ratio = [2, 3]       # 司机数量/乘客数量*100
        self.rule = 'fix'             # 服务费用规则
        self.alpha = 15 / 3600        # 时间成本系数，元/秒
        self.max_riders = 3           # 最多匹配的人数
        self.vehicle_capacity = 3     # 每个司机能够提供的座位数量
        self.max_stops = 4            # 司机全程最多经过4个站点，即额外经过2个站点
        self.dis_near = 300









import numpy as np
import matplotlib.pyplot as plt

# 定义横坐标距离范围
distances = np.linspace(0, 120, 500)

# 定义独享和拼车的总收费函数
def solo_price(distance):
    if distance <= 10:
        return 1.01 * 4 + 1.01 * distance
    elif distance <= 30:
        return 1.01 * 4 + 1.01 * 10 + 1.12 * (distance - 10)
    elif distance <= 50:
        return 1.01 * 4 + 1.01 * 10 + 1.12 * 20 + 0.57 * (distance - 30)
    elif distance <= 100:
        return 1.01 * 4 + 1.01 * 10 + 1.12 * 20 + 0.57 * 20 + 0.92 * (distance - 50)
    else:
        return 1.01 * 4 + 1.01 * 10 + 1.12 * 20 + 0.57 * 20 + 0.92 * 50 + 0.4 * (distance - 100)
def shared_price(distance):
    if distance <= 10:
        return 0.81 * 4 + 0.81 * distance
    elif distance <= 30:
        return 0.81 * 4 + 0.81 * 10 + 0.9 * (distance - 10)
    elif distance <= 50:
        return 0.81 * 4 + 0.81 * 10 + 0.9 * 20 + 0.57 * (distance - 30)
    elif distance <= 100:
        return 0.81 * 4 + 0.81 * 10 + 0.9 * 20 + 0.57 * 20 + 0.92 * (distance - 50)
    else:
        return 0.81 * 4 + 0.81 * 10 + 0.9 * 20 + 0.57 * 20 + 0.92 * 50 + 0.4 * (distance - 100)

# 计算独享和拼车的总费用
solo_costs = [solo_price(d) for d in distances]
shared_costs = [shared_price(d) for d in distances]

# 绘制独享和拼车的总费用与距离的关系
plt.plot(distances, solo_costs, label='one-to-one match', color='blue', linestyle='-')
plt.plot(distances, shared_costs, label='one-to-many match', color='red', linestyle='--')

# 设置网格线
plt.xticks([10, 30, 50, 100])
critical_points = []
for x in [10, 30, 50, 100]:
    critical_points.append(solo_price(x))
    critical_points.append(shared_price(x))
plt.yticks(critical_points)
plt.tick_params(axis='x', labelsize=8)  # 设置x轴刻度字体大小为8
plt.tick_params(axis='y', labelsize=8)  # 设置y轴刻度字体大小为8
plt.grid(True)   # 显示网格
plt.grid(color='gray',linewidth=0.5, alpha=0.4)    # 设置网格线参数

# 设置图形标题和标签
plt.title('The ridesharing pricing scheme of Dida Chuxing', fontsize=12)
plt.xlabel('distance (unit: km)', fontsize=12)
plt.ylabel('total fare (unit: CNY)', fontsize=12)

# 显示图例
plt.legend(fontsize=8)

# 添加文本注释和指向箭头
text_solo = ('    0 - 10 km: 1.01 CNY/km \n  10 - 30 km: 1.12 CNY/km \n  30 - 50 km: 0.57 CNY/km \n'
             '  50-100 km: 0.92 CNY/km \n  100 -    km: 0.40 CNY/km')
plt.text(0, 66, text_solo, fontsize=8, ha='left', color='black', alpha=0.7)
plt.arrow(48,48, -10, 15, color='darkblue', alpha=0.4)   # 添加箭头
text_share = ('    0 - 10 km: 0.81 CNY/km \n  10 - 30 km: 0.90 CNY/km \n  30 - 50 km: 0.57 CNY/km \n'
              '  50-100 km: 0.92 CNY/km \n  100 -    km: 0.40 CNY/km')
plt.text(73, 24, text_share, fontsize=8, ha='left', color='black', alpha=0.7)
plt.arrow(55,44, 15, -10, color='darkblue', alpha=0.4)   # 添加箭头

# 设置全局字体
plt.rcParams['font.family'] = 'serif'
# 显示图形
# plt.show()
plt.savefig('pricing.pdf')




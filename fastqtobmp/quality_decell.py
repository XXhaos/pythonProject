import os
import numpy as np
from collections import defaultdict
from itertools import product
from PIL import Image
import time

# 定义输入和输出文件夹路径
input_folder = r'D:\pythonProject\fastqtobmp\input\compressed\quality_reflection\g_prime'
output_folder = r'D:\pythonProject\fastqtobmp\input\recovered\quality_reflection'

# 创建输出文件夹（如果不存在）
os.makedirs(output_folder, exist_ok=True)

# 定义可能的元素列表
elements = [5, 12, 18, 24]
# 初始化规则字典，记录规则的使用次数
rules_dict = defaultdict(int)

# 按照顺序对规则表进行排序
sort_order = [5, 12, 18, 24]
rule_table = []

# 添加所有可能的规则到规则表
values = [5, 12, 18, 24]
combinations = list(product(values, repeat=4))
for combination in combinations:
    rule_table.append(combination)

rule_table.sort(key=lambda x: (sort_order.index(x[0]), sort_order.index(x[1]), sort_order.index(x[2]), sort_order.index(x[3])))

# 获取以 '.tiff' 结尾的文件列表，并按照文件名中的序号排序
tiff_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.tiff')],
                    key=lambda x: int(x.split('_')[1]))

number = 0
for tiff_file in tiff_files:
    start_time = time.time()  # 开始计时
    number += 1

    # 加载图像文件
    img_path = os.path.join(input_folder, tiff_file)
    img = Image.open(img_path)

    # 转换为灰度图像
    img_gray = img.convert('L')

    # 将灰度图像转换为NumPy数组
    Q_prime = np.array(img_gray)

    Q = np.zeros((Q_prime.shape[0], Q_prime.shape[1]))

    if number == 1:
        # 初始化Q矩阵，将Q_prime矩阵的前1/1000行和前1/20列复制到Q矩阵中
        Q[:(Q_prime.shape[0] // 1000), : (Q_prime.shape[1] // 20)] = Q_prime[:(Q_prime.shape[0] // 1000), : (Q_prime.shape[1] // 20)]

        for i in range(0, Q_prime.shape[0] // 1000):
            for j in range(0, Q_prime.shape[1] // 20):
                center = Q_prime[i, j]
                if i == 0:
                    up = 5
                else:
                    up = Q_prime[i - 1, j]
                if j == 0:
                    left = 5
                else:
                    left = Q_prime[i, j - 1]
                if i != 0 and j != 0:
                    left_up = Q_prime[i - 1, j - 1]
                else:
                    left_up = 5
                matched_rule = (up, left_up, left, center)
                rules_dict[matched_rule] += 1

        for i in range(0, Q_prime.shape[0]):
            for j in range(0, Q_prime.shape[1]):
                if i >= (Q_prime.shape[0] // 1000) or j >= (Q_prime.shape[1] // 20):
                    center = Q_prime[i, j]
                    if i == 0:
                        up = 5
                    else:
                        up = Q[i - 1, j]
                    if j == 0:
                        left = 5
                    else:
                        left = Q[i, j - 1]
                    if i != 0 and j != 0:
                        left_up = Q[i - 1, j - 1]
                    else:
                        left_up = 5
                    matched_rule = (up, left_up, left, center)
                    matched_rule1 = (up, left_up, left, 5)
                    matched_rule2 = (up, left_up, left, 12)
                    matched_rule3 = (up, left_up, left, 18)
                    matched_rule4 = (up, left_up, left, 24)

                    matched_rules = [matched_rule1, matched_rule2, matched_rule3, matched_rule4]
                    max_freq = -1
                    top_rule = None

                    for rule in matched_rules:
                        freq = rules_dict[rule]
                        if freq > max_freq:
                            max_freq = freq
                            top_rule = rule

                    # 如果Q_prime[i, j] == 1，说明预测正确，则将预测值赋给Q
                    # 否则保留当前值
                    Q[i, j] = top_rule[3] if Q_prime[i, j] == 1 else center
                    # 更新规则字典中该规则的频率
                    rules_dict[matched_rule] += 1
    else:
        for i in range(0, Q_prime.shape[0]):
            for j in range(0, Q_prime.shape[1]):
                center = Q_prime[i, j]
                if i == 0:
                    up = 5
                else:
                    up = Q[i - 1, j]
                if j == 0:
                    left = 5
                else:
                    left = Q[i, j - 1]
                if i != 0 and j != 0:
                    left_up = Q[i - 1, j - 1]
                else:
                    left_up = 5
                matched_rule = (up, left_up, left, center)
                matched_rule1 = (up, left_up, left, 5)
                matched_rule2 = (up, left_up, left, 12)
                matched_rule3 = (up, left_up, left, 18)
                matched_rule4 = (up, left_up, left, 24)

                matched_rules = [matched_rule1, matched_rule2, matched_rule3, matched_rule4]
                max_freq = -1
                top_rule = None

                for rule in matched_rules:
                    freq = rules_dict[rule]
                    if freq > max_freq:
                        max_freq = freq
                        top_rule = rule

                # 如果Q_prime[i, j] == 1，说明预测正确，则将预测值赋给Q
                # 否则保留当前值
                Q[i, j] = top_rule[3] if Q_prime[i, j] == 1 else center
                # 更新规则字典中该规则的频率
                rules_dict[matched_rule] += 1

    # 构建输出文件路径
    output_name = os.path.splitext(tiff_file)[0]
    q_file_path = os.path.join(output_folder, f'{output_name}_q.tiff')

    # 将Q矩阵转换为图像并保存为TIFF文件
    q_img = Image.fromarray(Q.astype(np.uint8))
    q_img.save(q_file_path)

    end_time = time.time()  # 结束计时
    elapsed_time = end_time - start_time  # 计算运行时间

    print(f'{tiff_file} 处理完成，运行时间: {elapsed_time:.2f} 秒')

print('所有文件处理完毕')

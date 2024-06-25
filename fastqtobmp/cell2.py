import os
import numpy as np
from collections import defaultdict
from itertools import product
from PIL import Image
import time

# 定义输入和输出文件夹路径
input_folder = r"D:\pythonProject\fastqtobmp\cache\change_to_gray\SRR554369_grayimage"
output_folder = r'D:\pythonProject\fastqtobmp\input\compressed\change_to_gray'

# 定义g和g_prime的输出子目录
g_output_folder = os.path.join(output_folder, 'g')
g_prime_output_folder = os.path.join(output_folder, 'g_prime')

# 创建g和g_prime子目录（如果不存在）
os.makedirs(g_output_folder, exist_ok=True)
os.makedirs(g_prime_output_folder, exist_ok=True)

# 定义可能的元素列表
elements = [0, 32, 64, 192, 224]
# 定义规则表，此处使用提供的规则表
rule_table = []

# 添加所有五个值的可能搭配到规则库
values = [0, 32, 64, 192, 224]
combinations = list(product(values, repeat=4))

for combination in combinations:
    rule_table.append(combination)

# 初始化规则字典，记录规则的使用次数
rules_dict = defaultdict(int)

# 按照 32， 224， 192， 64， 0 的顺序对规则表进行排序
sort_order = [32, 224, 192, 64, 0]
rule_table.sort(key=lambda x: (sort_order.index(x[0]), sort_order.index(x[1]), sort_order.index(x[2]), sort_order.index(x[3])))

# 获取输入文件夹中的所有 .tiff 文件，并按照数字顺序排序
tiff_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.tiff')], key=lambda x: int(x.split('_')[-1].split('.')[0]))

for tiff_file in tiff_files:
    start_time = time.time()  # 开始计时

    # 加载图像文件
    img_path = os.path.join(input_folder, tiff_file)
    img = Image.open(img_path)

    # 转换为灰度图像
    img_gray = img.convert('L')

    # 将灰度图像转换为NumPy数组
    G = np.array(img_gray)
    # 定义初始的灰度矩阵G'，只保留左上角4*4的灰度值，其余矩阵元素置为0
    G_prime = np.zeros((G.shape[0], G.shape[1]))
    G_prime[:(G.shape[0] // 5), :(G.shape[1] // 1000)] = G[:(G.shape[0] // 5), :(G.shape[1] // 1000)]


    for i in range(0, G.shape[0] // 5):
        for j in range(0, G.shape[1] // 1000):
            center = G[i, j]
            if i == 0:
                up = 0
            else:
                up = G[i - 1, j]
            if j == 0:
                left = 0
            else:
                left = G[i, j - 1]
            if i != 0 and j != 0:
                left_up = G[i - 1, j - 1]
            else:
                left_up = 0
            matched_rule = (up, left_up, left, center)
            rules_dict[matched_rule] += 1

    for i in range(0, G.shape[0]):
        for j in range(0, G.shape[1]):
            if i >= (G.shape[0] // 5) or j >= (G.shape[1] // 1000):
                center = G[i, j]
                if i == 0:
                    up = 0
                else:
                    up = G[i - 1, j]
                if j == 0:
                    left = 0
                else:
                    left = G[i, j - 1]
                if i != 0 and j != 0:
                    left_up = G[i - 1, j - 1]
                else:
                    left_up = 0
                matched_rule = (up, left_up, left, center)
                matched_rule1 = (up, left_up, left, 32)
                matched_rule2 = (up, left_up, left, 224)
                matched_rule3 = (up, left_up, left, 192)
                matched_rule4 = (up, left_up, left, 64)
                matched_rule5 = (up, left_up, left, 0)

                matched_rules = [matched_rule1, matched_rule2, matched_rule3, matched_rule4, matched_rule5]
                max_freq = -1
                top_rule = None

                for rule in matched_rules:
                    freq = rules_dict[rule]
                    if freq > max_freq:
                        max_freq = freq
                        top_rule = rule

                # 如果规则中心与当前元素相同，则将G_prime[i, j]赋值为1，否则赋值为当前元素
                G_prime[i, j] = 1 if top_rule[3] == center else center
            # 更新规则字典中该规则的频率
                rules_dict[matched_rule] += 1


    # 构建输出文件路径
    output_name = os.path.splitext(tiff_file)[0]
    g_file_path = os.path.join(g_output_folder, f'{output_name}_g.tiff')
    g_prime_file_path = os.path.join(g_prime_output_folder, f'{output_name}_g_prime.tiff')

    # 将G矩阵转换为图像并保存为TIFF文件
    g_img = Image.fromarray(G.astype(np.uint8))
    g_img.save(g_file_path)

    # 将G_prime矩阵转换为图像并保存为TIFF文件
    g_prime_img = Image.fromarray(G_prime.astype(np.uint8))
    g_prime_img.save(g_prime_file_path)


    end_time = time.time()  # 结束计时
    elapsed_time = end_time - start_time  # 计算运行时间

    print(f'{tiff_file} 处理完成，运行时间: {elapsed_time:.2f} 秒')

print('所有文件处理完毕')
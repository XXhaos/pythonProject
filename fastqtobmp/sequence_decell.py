import os
import numpy as np
from collections import defaultdict
from itertools import product
import time
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
# 定义输入和输出文件夹路径
input_folder = r'D:\pythonProject\change_to_gray_press\g_prime'
output_folder = r'D:\pythonProject\decompression\de_g'

# 定义g_prime和de_g的输出子目录
g_output_folder = os.path.join(output_folder, 'g_prime')
De_g_output_folder = os.path.join(output_folder, 'de_g')

# 创建g_prime和de_g子目录（如果不存在）
os.makedirs(g_output_folder, exist_ok=True)
os.makedirs(De_g_output_folder, exist_ok=True)

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
tiff_files = sorted([f for f in os.listdir(input_folder) if f.endswith('.tiff')],
                    key=lambda x: int(x.split('_')[-2].split('.')[0]) if x.split('_')[-2].isdigit() else float('inf'))
for tiff_file in tiff_files:
    start_time = time.time()  # 开始计时
    # 加载图像文件
    img_path = os.path.join(input_folder, tiff_file)
    img = Image.open(img_path)

    # 转换为灰度图像
    img_gray = img.convert('L')

    # 将灰度图像转换为NumPy数组
    G_prime = np.array(img_gray)
    # 定义初始的灰度矩阵G'，只保留左上角4*4的灰度值，其余矩阵元素置为0
#    G_prime = np.zeros((G.shape[0], G.shape[1]))
    # 初始化G_prime为与G相同大小的零矩阵
    De_g = np.zeros_like(G_prime)
    for i in range(0, G_prime.shape[0]):
        for j in range(0, G_prime.shape[1]):
            center = G_prime[i, j]
            if i == 0:
                up = 0
            else:
                up = De_g[i - 1, j]
            if j == 0:
                left = 0
            else:
                left = De_g[i, j - 1]
            if i != 0 and j != 0:
                left_up = De_g[i - 1, j - 1]
            else:
                left_up = 0
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
            De_g[i, j] = top_rule[3] if G_prime[i, j] == 1 else center
            # 更新规则字典中该规则的频率
            matched_rule = (up, left_up, left, De_g[i, j])
            rules_dict[matched_rule] += 1


    # 构建输出文件路径
    output_name = os.path.splitext(tiff_file)[0]
    g_prime_file_path = os.path.join(g_output_folder, f'{output_name}_g.tiff')
    De_g_file_path = os.path.join(De_g_output_folder, f'{output_name}_De_g.tiff')

    # 将G矩阵转换为图像并保存为TIFF文件
    g_prime_img = Image.fromarray(G_prime.astype(np.uint8))
    g_prime_img.save(g_prime_file_path)

    # 将G_prime矩阵转换为图像并保存为TIFF文件
    De_g_img = Image.fromarray(De_g.astype(np.uint8))
    De_g_img.save(De_g_file_path)


    end_time = time.time()  # 结束计时
    elapsed_time = end_time - start_time  # 计算运行时间

    print(f'{tiff_file} 处理完成，运行时间: {elapsed_time:.2f} 秒')

print('所有文件处理完毕')
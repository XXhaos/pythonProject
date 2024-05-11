import numpy as np
from collections import defaultdict
from itertools import product
from PIL import Image


# # 打开TIFF图像文件
# image = Image.open('grayimage_base_2.tiff')
#
# # 将图像转换为灰度图像
# image_gray = image.convert('L')
#
# #定义要提取的部分区域的左上角和右下角坐标
# left = 0
# top = 0
# right = 50
# bottom = 100000
#
# # 提取部分区域的矩阵
# G = np.array(image_gray.crop((left, top, right, bottom)))

#加载图像文件
img = Image.open("test1/SRR21733577_2_base_1.tiff")

# 转换为灰度图像
img_gray = img.convert('L')

# 将灰度图像转换为NumPy数组
G = np.array(img_gray)

#定义可能的元素列表
elements = [0, 32, 64, 192, 224]

# # 生成随机矩阵
# G = np.random.choice(elements, size=(1000, 50))

# 定义初始的灰度矩阵G'，只保留左上角4*4的灰度值，其余矩阵元素置为0。
G_prime = np.zeros((G.shape[0], G.shape[1]))
G_prime[:(G.shape[0] // 4), :(G.shape[1] // 4)] = G[:(G.shape[0] // 4), :(G.shape[1] // 4)]

# 定义规则表，此处使用提供的规则表
rule_table = []

# 初始化规则字典，记录规则的使用次数
rules_dict = defaultdict(int)

# 添加所有六个值的可能搭配到规则库
values = [0, 32, 64, 192, 224]
combinations = list(product(values, repeat=4))


for combination in combinations:
    rule_table.append(combination)

for i in range(0, (G.shape[0] // 4)):
    for j in range(0, (G.shape[1] // 4)):
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
        new_rule = (up, left_up, left, center)
        rules_dict[new_rule] += 1

#按照 32， 224， 192， 64， 0 的顺序对规则表进行排序
sort_order = [32, 224, 192, 64, 0]
rule_table.sort(key=lambda x: (sort_order.index(x[0]), sort_order.index(x[1]), sort_order.index(x[2]), sort_order.index(x[3])))


for i in range(0, G.shape[0]):
    for j in range(0, G.shape[1]):
        if i >= (G.shape[0] // 4) or j >= (G.shape[1] // 4):
            # 获取当前元素及邻居的状态
            center = G[i, j]
            if i != 0 and j != 0:
                left_up = G[i - 1, j - 1]
            else:
                left_up = 0
            if i == 0:
                up = 0
            else:
                up = G[i - 1, j]
            if j == 0:
                left = 0
            else:
                left = G[i, j - 1]

            # 查找最匹配的规则
            matched_rule = (up, left_up, left, center)
            # 查找与邻居相同的前三个元素的规则
            matched_rules = [(rule, freq) for rule, freq in rules_dict.items() if rule[0] == up and rule[1] == left_up and rule[2] == left]

            # 如果找到匹配的规则
            if matched_rules:
                # 按频率排序规则
                matched_rules.sort(key=lambda x: x[1], reverse=True)
                # 选择频率最高的规则
                top_rule = matched_rules[0][0]
                # 如果规则中心与当前元素相同，则将G_prime[i, j]赋值为1，否则赋值为当前元素
                G_prime[i, j] = 1 if top_rule[3] == center else center
                # 更新规则字典中该规则的频率
                rules_dict[matched_rule] += 1


print('正在写入数据')


with open("Rule.txt", "w") as f:
    for rule in rule_table:
        f.write(f"{rule} - Frequency: {rules_dict[rule] if rules_dict[rule] > 0 else 0}\n")

#定义一个按字母排序的规则库
rule_table1 = rule_table

# 将矩阵中的所有元素转换为整数
G_prime = G_prime.astype(int)

with open("Rule1.txt", "w") as f:
    for rule in rule_table1:
        f.write(f"{rule} - Frequency: {rules_dict[rule] if rules_dict[rule] > 0 else 0}\n")

# 写入文件的代码不需要更改，因为在写入文件之前已经将值转换为整数类型
with open('G_prime.txt', 'w') as f:
    for row in G_prime:
        # 将每一行转换为字符串并写入文件
        f.write(' '.join([str(elem) for elem in row]))
        f.write('\n')

with open('G.txt', 'w') as f:
    for row in G:
        # 将每一行转换为字符串并写入文件
        f.write(' '.join([str(elem) for elem in row]))
        f.write('\n')

print("execute over")
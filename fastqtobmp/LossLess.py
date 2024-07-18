import os
import numpy as np
from collections import defaultdict
from itertools import product
from PIL import Image
from Bio import SeqIO
import time
import re

def find_delimiters(identifier):
    delimiters = re.findall(r'[.:_\s=/-]', identifier)
    return delimiters

def split_identifier(identifier, delimiters):
    tokens = re.split(r'[.:_\s=/-]', identifier)
    return tokens

def generate_regex(delimiters):
    regex = ""
    count = 1
    for delimiter in delimiters:
        regex += f"T{count}"
        regex += delimiter
        count += 1
    regex += f"T{count}"
    return regex

def fastq_to_g_prime(fastq_path, output_path, block_size=256 * 1024 * 1024):
    """
    将 FASTQ 文件分批读取并转换为预测后的 g_prime 矩阵，每批的大小接近给定的 block_size。

    参数：
    fastq_path：FASTQ 文件的路径。
    output_path：输出路径。
    block_size：每个图像块的目标大小（以字节为单位），默认为 256MB。
    """
    start_time = time.time()

    # 创建输出目录
    os.makedirs(output_path, exist_ok=True)

    # 定义碱基到灰度值的映射
    base_to_gray = {'A': 32, 'T': 64, 'G': 192, 'C': 224, 'N': 0}

    # 使用 SeqIO.parse() 预读取第一个 read 来确定 read 长度
    with open(fastq_path, 'r') as file:
        first_record = next(SeqIO.parse(file, "fastq"))
        read_length = len(first_record.seq)

    # 计算每个read所需的字节数（DNA序列和质量分数各占一半）
    bytes_per_read = read_length * 2

    # 根据block_size和bytes_per_read计算每个图像块应包含的reads数目
    reads_per_block = block_size // bytes_per_read

    read_count = 0
    block_count = 0
    id_block = []
    base_image_block = []
    quality_image_block = []

    # 定义可能的元素列表
    elements = [0, 32, 64, 192, 224]
    # 定义规则表
    rule_table = []

    # 添加所有可能的规则到规则库
    values = [0, 32, 64, 192, 224]
    combinations = list(product(values, repeat=4))

    for combination in combinations:
        rule_table.append(combination)

    # 初始化规则字典，记录规则的使用次数
    rules_dict = defaultdict(int)

    # 使用 SeqIO.parse() 函数逐条读取 FASTQ 文件
    with open(fastq_path, 'r') as file:
        for record in SeqIO.parse(file, "fastq"):
            id_str = record.description
            delimiters = find_delimiters(id_str)
            tokens = split_identifier(id_str, delimiters)
            regex = generate_regex(delimiters)
            id_block.append((tokens, regex))

            base_gray_values = [base_to_gray.get(base, 0) for base in record.seq]
            base_image_block.append(base_gray_values)

            quality_gray_values = [min(q * 2, 255) for q in record.letter_annotations["phred_quality"]]
            quality_image_block.append(quality_gray_values)

            read_count += 1

            # 当达到指定的 reads_per_block 时，处理图像块
            if len(base_image_block) == reads_per_block:
                block_count += 1
                process_block(np.array(base_image_block, dtype=np.uint8), output_path, block_count, rules_dict)
                save_quality_image(np.array(quality_image_block, dtype=np.uint8), output_path, block_count)
                save_id_block(id_block, output_path, block_count)
                print(f"图像块 {block_count} 已处理。")

                id_block = []
                base_image_block = []
                quality_image_block = []

    # 处理最后一个图像块（如果有剩余）
    if base_image_block:
        block_count += 1
        process_block(np.array(base_image_block, dtype=np.uint8), output_path, block_count, rules_dict)
        save_quality_image(np.array(quality_image_block, dtype=np.uint8), output_path, block_count)
        save_id_block(id_block, output_path, block_count)
        print(f"最后的图像块 {block_count} 已处理。")

    end_time = time.time()
    print(f"代码执行时间: {(end_time - start_time)/60} 分钟")

    return read_count, reads_per_block, block_count

def process_block(G, output_path, block_count, rules_dict):
    # 初始化G_prime为与G相同大小的零矩阵
    G_prime = np.zeros_like(G)

    # 按照规则表进行预测并生成G_prime矩阵
    for i in range(0, G.shape[0]):
        for j in range(0, G.shape[1]):
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
    output_name = f"chunk_{block_count}_base"
    g_prime_file_path = os.path.join(output_path, f'{output_name}_g_prime.tiff')

    # 将G_prime矩阵转换为图像并保存为TIFF文件
    g_prime_img = Image.fromarray(G_prime.astype(np.uint8))
    g_prime_img.save(g_prime_file_path)

def save_quality_image(G, output_path, block_count):
    # 构建输出文件路径
    output_name = f"chunk_{block_count}_quality"
    quality_file_path = os.path.join(output_path, f'{output_name}.tiff')

    # 将G矩阵转换为图像并保存为TIFF文件
    quality_img = Image.fromarray(G.astype(np.uint8))
    quality_img.save(quality_file_path)

def save_id_block(id_block, output_path, block_count):
    tokens_file_path = os.path.join(output_path, f"chunk_{block_count}_id_tokens.txt")
    regex_file_path = os.path.join(output_path, f"chunk_{block_count}_id_regex.txt")

    with open(tokens_file_path, 'w') as tokens_file, open(regex_file_path, 'w') as regex_file:
        for tokens, regex in id_block:
            tokens_file.write(' '.join(tokens) + '\n')
            regex_file.write(regex + '\n')

# 示例文件路径（需要替换为实际路径）
fastq_path = r"D:\pythonProject\fastqtobmp\input\SRR13679454_1.fastq"
output_path = r"D:\pythonProject\fastqtobmp\input\compressed"

# 调用函数处理FASTQ文件
read_count, reads_per_block, total_blocks = fastq_to_g_prime(fastq_path, output_path)

# 打印处理的reads数量、每块reads数量和图像块数量
print(f"处理的reads数量: {read_count}，每个图像块的reads数量: {reads_per_block}，一共有: {total_blocks}个图像块。")

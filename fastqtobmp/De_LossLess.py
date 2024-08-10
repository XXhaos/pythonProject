import os
import numpy as np
from PIL import Image
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
import re
import glob
from collections import defaultdict

# 定义碱基从灰度值的映射
gray_to_base = {32: 'A', 64: 'T', 192: 'G', 224: 'C', 0: 'N'}

def load_id_block(id_block_path, regex_path):
    with open(id_block_path, 'r') as tokens_file, open(regex_path, 'r') as regex_file:
        tokens = [line.strip().split(' ') for line in tokens_file.readlines()]
        regex = [line.strip() for line in regex_file.readlines()]
    return tokens, regex

def reconstruct_id(tokens, regex):
    reconstructed_ids = []
    for t, r in zip(tokens, regex):
        id_str = r
        for i, token in enumerate(t):
            id_str = id_str.replace(f"T{i+1}", token)
        reconstructed_ids.append(id_str)
    return reconstructed_ids

def reconstruct_g_from_g_prime(g_prime_array, rules_dict):
    De_g = np.zeros_like(g_prime_array)

    for i in range(g_prime_array.shape[0]):
        for j in range(g_prime_array.shape[1]):
            center = g_prime_array[i, j]
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

            De_g[i, j] = top_rule[3] if g_prime_array[i, j] == 1 else center
            matched_rule = (up, left_up, left, De_g[i, j])
            rules_dict[matched_rule] += 1

    return De_g

def reconstruct_base_quality_and_write(base_file, quality_file, id_block, regex_block, rules_dict, output_handle):
    base_img = Image.open(base_file)
    g_prime_array = np.array(base_img)
    bases_array = reconstruct_g_from_g_prime(g_prime_array, rules_dict)

    quality_img = Image.open(quality_file)
    quality_array = np.array(quality_img)

    reconstructed_ids = reconstruct_id(id_block, regex_block)

    for i in range(bases_array.shape[0]):
        base_str = ''.join([gray_to_base[pixel] for pixel in bases_array[i]])
        quality_scores = [q // 2 for q in quality_array[i]]

        seq = Seq(base_str)
        record = SeqRecord(seq, id=reconstructed_ids[i], description="")
        record.letter_annotations["phred_quality"] = quality_scores
        SeqIO.write(record, output_handle, "fastq")

def reconstruct_fastq(id_token_files, id_regex_files, base_files, quality_files, output_fastq_path):
    rules_dict = defaultdict(int)

    with open(output_fastq_path, "w") as output_handle:
        for id_tokens_path, id_regex_path, base_file, quality_file in zip(id_token_files, id_regex_files, base_files, quality_files):
            tokens, regex = load_id_block(id_tokens_path, id_regex_path)
            reconstruct_base_quality_and_write(base_file, quality_file, tokens, regex, rules_dict, output_handle)

# 示例文件路径（需要替换为实际路径）
output_path = r"D:\pythonProject\fastqtobmp\output\first_compressed"
id_token_files = sorted(
    glob.glob(f"{output_path}/chunk_*_id_tokens.txt"),
    key=lambda x: int(re.search(r'chunk_(\d+)_id_tokens.txt', x).group(1))
)
id_regex_files = sorted(
    glob.glob(f"{output_path}/chunk_*_id_regex.txt"),
    key=lambda x: int(re.search(r'chunk_(\d+)_id_regex.txt', x).group(1))
)
base_files = sorted(
    glob.glob(f"{output_path}/chunk_*_base_g_prime.tiff"),
    key=lambda x: int(re.search(r'chunk_(\d+)_base_g_prime.tiff', x).group(1))
)
quality_files = sorted(
    glob.glob(f"{output_path}/chunk_*_quality.tiff"),
    key=lambda x: int(re.search(r'chunk_(\d+)_quality.tiff', x).group(1))
)
output_fastq_path = r"D:\pythonProject\fastqtobmp\input\reconstructed.fastq"

# 调用函数还原FASTQ文件
reconstruct_fastq(id_token_files, id_regex_files, base_files, quality_files, output_fastq_path)
print("FASTQ文件已还原。")
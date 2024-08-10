import os
import shutil
from Bio.Seq import Seq
import glob
from Bio.SeqRecord import SeqRecord
import numpy as np
from collections import defaultdict
from itertools import product
from PIL import Image
from Bio import SeqIO
import time
import re
from lpaq8 import compress_all_files_in_directory, decompress_all_files_in_directory
from tools import check_output_path, get_file_size, get_directory_size


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
    print(f"代码执行时间: {(end_time - start_time) / 60} 分钟")

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


def combine(input_path, output_path):
    with open(output_path, "w+b") as output_file:

        # 获取文件块的最大id
        pattern = re.compile(r"^chunk_(\d+)_base_g_prime.lpaq8$")
        max_batch_id = -1

        if len(os.listdir(input_path)) <= 0:
            print("错误：输入的路径不存在文件")
            exit(1)

        if len(os.listdir(input_path)) % 4 != 0:
            print("错误：文件缺失")
            exit(1)

        for file in os.listdir(input_path):
            matches = pattern.findall(file)
            if matches is not None and len(matches) > 0:
                file_id_str = matches[0]

                if not file_id_str.isdigit():
                    print("错误：id类型不是整数")
                    exit(1)

                batch_id = int(file_id_str)

                if batch_id > max_batch_id:
                    max_batch_id = batch_id

        if max_batch_id == -1:
            print("错误：id不能小于0")
            exit(1)

        if len(os.listdir(input_path)) / 4 != max_batch_id:
            print("错误：文件缺失")
            exit(1)

        # 按顺序进行写入
        # 将所有id_regex写入
        for batch_id in range(1, max_batch_id + 1):
            id_regex = f"chunk_{batch_id}_id_regex.lpaq8"

            with open(os.path.join(input_path, id_regex), "rb") as input_file:
                output_file.write(b"%id_regex%")
                output_file.write(input_file.read())

        # 将所有id_token写入
        for batch_id in range(1, max_batch_id + 1):
            id_token = f"chunk_{batch_id}_id_tokens.lpaq8"

            with open(os.path.join(input_path, id_token), "rb") as input_file:
                output_file.write(b"%id_tokens%")
                output_file.write(input_file.read())

        # 将所有base_g_prime写入
        for batch_id in range(1, max_batch_id + 1):
            base_g_prime = f"chunk_{batch_id}_base_g_prime.lpaq8"

            with open(os.path.join(input_path, base_g_prime), "rb") as input_file:
                output_file.write(b"%base_g_prime%")
                output_file.write(input_file.read())

        # 将所有quality写入
        for batch_id in range(1, max_batch_id + 1):
            quality = f"chunk_{batch_id}_quality.lpaq8"

            with open(os.path.join(input_path, quality), "rb") as input_file:
                output_file.write(b"%quality%")
                output_file.write(input_file.read())

        output_file.write(b"%eof%")


def decombine(input_path, output_path):
    with open(input_path, "rb") as input_file:

        # 确保输出文件夹存在
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        content = input_file.read()

        start = 0
        end = 0

        # 拆分出id_regex
        seperator = b"%id_regex%"
        counter = 1
        while True:
            start = content.find(seperator, end)
            if start == -1:
                break

            end = content.find(seperator, start + len(seperator))
            if end == -1:
                break

            data = content[start + len(seperator): end]

            output_name = os.path.join(output_path, f"chunk_{counter}_id_regex.lpaq8")

            with open(output_name, "w+b") as output_file:
                output_file.write(data)
                counter += 1

        # 对最后一个id_regex作处理
        next_seperator = b"%id_tokens%"
        end = content.find(next_seperator, start + len(next_seperator))
        data = content[start + len(seperator): end]

        output_name = os.path.join(output_path, f"chunk_{counter}_id_regex.lpaq8")

        with open(output_name, "w+b") as output_file:
            output_file.write(data)

        # 拆分出id_token
        seperator = b"%id_tokens%"
        counter = 1
        while True:
            start = content.find(seperator, end)
            if start == -1:
                break

            end = content.find(seperator, start + len(seperator))
            if end == -1:
                break

            data = content[start + len(seperator): end]

            output_name = os.path.join(output_path, f"chunk_{counter}_id_tokens.lpaq8")

            with open(output_name, "w+b") as output_file:
                output_file.write(data)
                counter += 1

        # 对最后一个id_tokens作处理
        next_seperator = b"%base_g_prime%"
        end = content.find(next_seperator, start + len(next_seperator))
        data = content[start + len(seperator): end]

        output_name = os.path.join(output_path, f"chunk_{counter}_id_tokens.lpaq8")

        with open(output_name, "w+b") as output_file:
            output_file.write(data)

        # 拆分出base_g_prime
        seperator = b"%base_g_prime%"
        counter = 1
        while True:
            start = content.find(seperator, end)
            if start == -1:
                break

            end = content.find(seperator, start + len(seperator))
            if end == -1:
                break

            data = content[start + len(seperator): end]

            output_name = os.path.join(output_path, f"chunk_{counter}_base_g_prime.lpaq8")

            with open(output_name, "w+b") as output_file:
                output_file.write(data)
                counter += 1

        # 对最后一个base_g_prime作处理
        next_seperator = b"%quality%"
        end = content.find(next_seperator, start + len(next_seperator))
        data = content[start + len(seperator): end]

        output_name = os.path.join(output_path, f"chunk_{counter}_base_g_prime.lpaq8")

        with open(output_name, "w+b") as output_file:
            output_file.write(data)

        # 将所有quality写入
        seperator = b"%quality%"
        counter = 1
        while True:
            start = content.find(seperator, end)
            if start == -1:
                break

            end = content.find(seperator, start + len(seperator))
            if end == -1:
                break

            data = content[start + len(seperator): end]

            output_name = os.path.join(output_path, f"chunk_{counter}_quality.lpaq8")

            with open(output_name, "w+b") as output_file:
                output_file.write(data)
                counter += 1

        # 对最后一个id_tokens作处理
        next_seperator = b"%eof%"
        end = content.find(next_seperator, start + len(next_seperator))
        data = content[start + len(seperator): end]

        output_name = os.path.join(output_path, f"chunk_{counter}_quality.lpaq8")

        with open(output_name, "w+b") as output_file:
            output_file.write(data)


def first_compress(fastq_path, first_compressed_path):
    read_count, reads_per_block, total_blocks = fastq_to_g_prime(fastq_path, first_compressed_path)
    print(f"处理的reads数量: {read_count}，每个图像块的reads数量: {reads_per_block}，一共有: {total_blocks}个图像块。")
    print(f"前端压缩完成，压缩前文件大小：{get_file_size(fastq_path)}")
    return read_count, reads_per_block, total_blocks


def first_decompress(fastq_path, first_compressed_path):
    id_token_files = sorted(
        glob.glob(f"{first_compressed_path}/chunk_*_id_tokens.txt"),
        key=lambda x: int(re.search(r'chunk_(\d+)_id_tokens.txt', x).group(1))
    )
    id_regex_files = sorted(
        glob.glob(f"{first_compressed_path}/chunk_*_id_regex.txt"),
        key=lambda x: int(re.search(r'chunk_(\d+)_id_regex.txt', x).group(1))
    )
    base_files = sorted(
        glob.glob(f"{first_compressed_path}/chunk_*_base_g_prime.tiff"),
        key=lambda x: int(re.search(r'chunk_(\d+)_base_g_prime.tiff', x).group(1))
    )
    quality_files = sorted(
        glob.glob(f"{first_compressed_path}/chunk_*_quality.tiff"),
        key=lambda x: int(re.search(r'chunk_(\d+)_quality.tiff', x).group(1))
    )
    output_fastq_path = r"D:\pythonProject\fastqtobmp\input\reconstructed.fastq"
    reconstruct_fastq(id_token_files, id_regex_files, base_files, quality_files, output_fastq_path)
    print("FASTQ文件已还原。")


def second_compress(first_compressed_path, second_compressed_path, lpaq8_path):
    compress_all_files_in_directory(first_compressed_path, second_compressed_path, lpaq8_path)
    print("后端压缩完成")


def second_decompress(first_compressed_path, second_compressed_path, lpaq8_path):
    decompress_all_files_in_directory(first_compressed_path, second_compressed_path, lpaq8_path)
    print("后端解压完成")


def final_compress(second_compressed_path, final_compressed_path):
    combine(second_compressed_path, final_compressed_path)
    # file_size = get_file_size(final_compressed_path)
    print(f"打包完成，压缩后文件大小：{get_file_size(final_compressed_path)}")


def final_decompress(final_compressed_path, second_compressed_path):
    print(f"开始拆包，拆包前文件大小：{get_file_size(final_compressed_path)}")
    decombine(final_compressed_path, second_compressed_path)
    # file_size = get_file_size(final_compressed_path)
    print(f"拆包完成")


def post_process_after_compression(first_compressed_path, second_compressed_path):
    try:
        shutil.rmtree(first_compressed_path)
        print(f"Folder '{first_compressed_path}' has been deleted.")
        shutil.rmtree(second_compressed_path)
        print(f"Folder '{second_compressed_path}' has been deleted.")
    except OSError as e:
        print(f"Error: {e.strerror}")


def compress(fastq_path, output_path, lpaq8_path, remove_intermediate_products):
    # 拼好三次压缩的路径
    first_compressed_path = os.path.join(output_path, "first_compressed")
    second_compressed_path = os.path.join(output_path, "second_compressed")
    final_compressed_path = os.path.join(output_path, os.path.splitext(os.path.basename(fastq_path))[0])

    # 第一步处理：调用函数处理FASTQ文件，并打印处理的reads数量、每块reads数量和图像块数量
    first_compress(fastq_path, first_compressed_path)

    # 第二步处理：将处理后的文件进行后端压缩
    second_compress(first_compressed_path, second_compressed_path, lpaq8_path)

    # 最后一步处理：将完成后端压缩的文件打包为一个文件
    final_compress(second_compressed_path, final_compressed_path)

    if remove_intermediate_products:
        post_process_after_compression(first_compressed_path, second_compressed_path)


def decompress(compressed_path, output_path, lpaq8_path, remove_intermediate_products):
    first_decompressed_path = os.path.join(output_path, "first_compressed")
    second_decompressed_path = os.path.join(output_path, "second_compressed")
    final_decompressed_path = compressed_path

    # 最后一步压缩的逆操作：将打包文件拆开
    final_decompress(final_decompressed_path, second_decompressed_path)

    # 第二步压缩的逆操作：将处理后的文件进行后端解压
    second_decompress(second_decompressed_path, first_decompressed_path, lpaq8_path)

    # 第一步压缩的逆操作：将解压后的文件组合成fastq文件
    # TODO 将解压后的文件组合成fastq文件
    first_decompress(fastq_path, first_decompressed_path)

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


def main(type, input_path, output_path, lpaq8_path, remove_intermediate_products):
    # if output_path is None:
    #     output_path = os.path.dirname(fastq_path)
    # check = check_output_path(output_path)
    # if not check:
    #     print("指定的输出路径必须是一个目录！")
    #     exit()

    if type == "compress" or type == "c":
        print(f"开始进行压缩程序，压缩文件名：{fastq_path}")
        compress(input_path, output_path, lpaq8_path, remove_intermediate_products)
    elif type == "decompress" or type == "d":
        print(f"开始进行解压程序，压缩文件名：{fastq_path}")
        decompress(input_path, output_path, lpaq8_path, remove_intermediate_products)
    else:
        print("指定类型错误")


if __name__ == '__main__':
    fastq_path = f"{os.getcwd()}\input\SRR6819330.fastq"
    output_path = f"{os.getcwd()}\output"
    # output_path = None
    lpaq8_path = f"{os.getcwd()}\lpaq8.exe"
    # lpaq8_path = None
    compressed_path = f"{os.getcwd()}\output\SRR6819330"

    # remove_intermediate_products = True 时，删去中间产物
    # main("compress", fastq_path, output_path, lpaq8_path, False)
    main("decompress", compressed_path, output_path, lpaq8_path, False)

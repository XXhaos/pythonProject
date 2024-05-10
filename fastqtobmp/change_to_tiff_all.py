from Bio import SeqIO
import numpy as np
import tifffile as tiff
import time
import os

def fastq_to_image_segmented(fastq_path, output_path, block_size=32 * 1024 * 1024):
    """
    将 FASTQ 文件分批读取并转换为图像，每批的大小接近给定的 block_size。

    参数：
    fastq_path：FASTQ 文件的路径。
    output_path：输出图像的路径。
    block_size：每个图像块的目标大小（以字节为单位），默认为 16MB。
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
    # 注意：这里简化计算，实际情况中还需考虑其他因素，如编码等
    bytes_per_read = read_length * 2

    # 根据block_size和bytes_per_read计算每个图像块应包含的reads数目
    reads_per_block = block_size // bytes_per_read

    read_count = 0
    block_count = 0
    base_image_block = []
    quality_image_block = []

    # 使用 SeqIO.parse() 函数逐条读取 FASTQ 文件
    with open(fastq_path, 'r') as file:
        for record in SeqIO.parse(file, "fastq"):
            base_gray_values = [base_to_gray.get(base, 0) for base in record.seq]
            base_image_block.append(base_gray_values)

            quality_gray_values = [min(q * 2, 255) for q in record.letter_annotations["phred_quality"]]
            quality_image_block.append(quality_gray_values)

            read_count += 1

            # 当达到指定的 reads_per_block 时，保存图像块
            if len(base_image_block) == reads_per_block:
                block_count += 1
                tiff.imwrite(f"{output_path}/grayimage_base_{block_count}.tiff", np.array(base_image_block, dtype=np.uint8))
                tiff.imwrite(f"{output_path}/grayimage_quality_{block_count}.tiff", np.array(quality_image_block, dtype=np.uint8))
                print(f"图像块 {block_count} 已保存。")

                base_image_block = []
                quality_image_block = []

    # 保存最后一个图像块（如果有剩余）
    if base_image_block:
        block_count += 1
        tiff.imwrite(f"{output_path}/grayimage_base_{block_count}.tiff", np.array(base_image_block, dtype=np.uint8))
        tiff.imwrite(f"{output_path}/grayimage_quality_{block_count}.tiff", np.array(quality_image_block, dtype=np.uint8))
        print(f"最后的图像块 {block_count} 已保存。")

    end_time = time.time()
    print(f"代码执行时间: {end_time - start_time} 秒")

    return read_count, reads_per_block, block_count

# # 示例文件路径（需要替换为实际路径）
# fastq_path = "input/ERR3365952.fastq"
# output_path = "cache/change_to_gray/"
#
# # 调用函数处理FASTQ文件
# read_count, reads_per_block, total_blocks = fastq_to_image_segmented(fastq_path, output_path)
#
# # 打印处理的reads数量、每块reads数量和图像块数量
# print(f"处理的reads数量: {read_count}，每个图像块的reads数量: {reads_per_block}，一共有: {total_blocks}个图像块。")

def process_all_fastq(input_directory, output_base_path):
    """
    处理 input_directory 下的所有 .fastq 文件，并将结果输出到以文件名命名的目录中。

    参数:
    - input_directory: 包含 .fastq 文件的目录路径。
    - output_base_path: 输出基本路径，将创建子目录保存图像文件。
    """
    # 检索所有 .fastq 文件
    for file_name in os.listdir(input_directory):
        if file_name.endswith('.fastq'):
            fastq_path = os.path.join(input_directory, file_name)
            # 创建输出路径，去掉文件后缀
            output_path = os.path.join(output_base_path, os.path.splitext(file_name)[0] + '_grayimage')
            os.makedirs(output_path, exist_ok=True)  # 确保输出目录存在

            fastq_to_image_segmented(fastq_path, output_path)

            # 打印信息作为演示
            print(f"Processing {fastq_path} into {output_path}")


# 示例路径（需要根据实际情况调整）
input_directory = 'input'
output_base_path = 'cache/change_to_gray'

# 调用函数处理所有 .fastq 文件
process_all_fastq(input_directory, output_base_path)
from Bio import SeqIO
import numpy as np
import tifffile as tiff
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import glob
import time


def image_to_fastq(image_directory, fastq_output_path):
    # 记录开始时间
    start_time = time.time()

    # 灰度值到碱基的映射
    gray_to_base = {32: 'A', 64: 'T', 192: 'G', 224: 'C', 0: 'N'}

    # 获取所有碱基序列图像块路径
    base_image_paths = sorted(glob.glob(f"{image_directory}/grayimage_base_*.tiff"))
    # 获取所有质量分数图像块路径
    quality_image_paths = sorted(glob.glob(f"{image_directory}/grayimage_quality_*.tiff"))

    if not base_image_paths or not quality_image_paths:
        print("错误：没有找到图像文件。")
        return

    # 打开输出文件进行写入
    with open(fastq_output_path, 'w') as output_handle:
        # 设置批处理大小
        batch_size = 50000  # 这个值可以根据内存限制进行调整

        # 遍历每个图像块，将灰度值转换回reads序列
        for base_path, quality_path in zip(base_image_paths, quality_image_paths):
            # 读取碱基序列图像块
            base_image_block = tiff.imread(base_path)
            # 读取质量分数图像块
            quality_image_block = tiff.imread(quality_path)

            # 初始化reads列表
            reads = []

            # 逐行处理图像块
            for base_row, quality_row in zip(base_image_block, quality_image_block):
                bases = ''.join([gray_to_base.get(pixel, 'N') for pixel in base_row])
                qualities = [min(pixel // 2, 40) for pixel in quality_row]
                record = SeqRecord(Seq(bases), letter_annotations={"phred_quality": qualities})
                reads.append(record)

                # 如果达到批处理大小或处理完图像块，则写入文件
                if len(reads) >= batch_size:
                    SeqIO.write(reads, output_handle, "fastq")
                    reads = []  # 重置reads列表

            # 检查在图像块处理完后是否还有剩余的reads未写入
            if reads:
                SeqIO.write(reads, output_handle, "fastq")

    # 记录结束时间
    end_time = time.time()

    # 打印执行时间
    execution_time = end_time - start_time
    print(f"代码执行时间: {execution_time} 秒")

# 示例用法
image_directory = "cache/change_to_gray"  # 替换为存储图像块的文件夹路径
fastq_output_path = "cache/change_to_fastq/restored_reads.fastq"  # 输出FASTQ文件路径
image_to_fastq(image_directory, fastq_output_path)
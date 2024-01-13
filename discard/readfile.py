from Bio import SeqIO
import numpy as np
import tifffile as tiff
import time

def process_batch(records, output_path, batch_index):
    # 碱基到灰度值的映射
    base_to_gray = {'A': 32, 'T': 64, 'G': 192, 'C': 224, 'N': 0}

    base_image_list = []
    quality_image_list = []

    for record in records:
        # 将碱基序列转换为灰度值
        base_gray_values = np.array([base_to_gray.get(base, 0) for base in record.seq], dtype=np.uint8)
        base_image_list.append(base_gray_values)

        # 将质量分数转换为灰度值
        quality_gray_values = np.array([min(q * 2, 255) for q in record.letter_annotations["phred_quality"]], dtype=np.uint8)
        quality_image_list.append(quality_gray_values)

    # 将列表转换为NumPy数组并保存
    if base_image_list and quality_image_list:
        base_image_block = np.stack(base_image_list)
        quality_image_block = np.stack(quality_image_list)
        tiff.imwrite(f"{output_path}_base_{batch_index + 1}.tiff", base_image_block)
        tiff.imwrite(f"{output_path}_quality_{batch_index + 1}.tiff", quality_image_block)
        print(f"批次 {batch_index + 1} 的图像已保存。")

def process_fastq(file_path, output_path, batch_size):
    # 记录开始时间
    start_time = time.time()

    with open(file_path, 'r') as fastq_file:
        buffer = []
        batch_index = 0
        for record in SeqIO.parse(fastq_file, "fastq"):
            buffer.append(record)

            if len(buffer) >= batch_size:
                process_batch(buffer, output_path, batch_index)
                buffer = []
                batch_index += 1

        if buffer:
            process_batch(buffer, output_path, batch_index)

    # 记录结束时间
    end_time = time.time()

    # 打印执行时间
    execution_time = end_time - start_time
    print(f"代码执行时间: {execution_time} 秒")

# 调用函数来处理FASTQ文件
file_path = '/fastqtobmp/input/SRR554369.fastq'
output_path = '/Users/hbxnlsy/pythonProject/fastqtobmp/cache/change_to_gray/grayimage'
batch_size = 1500000  # 每次读取150万条read,大约300MB,可根据需要调整
process_fastq(file_path, output_path, batch_size)
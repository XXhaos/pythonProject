import os
import numpy as np
import tifffile as tiff
from Bio import SeqIO
import time
import shutil
import logging

# 配置日志
logging.basicConfig(filename='fastq_to_image_errors.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')

def fastq_to_image_segmented(fastq_path, output_path, block_size=16 * 1024 * 1024):
    try:
        start_time = time.time()
        os.makedirs(output_path, exist_ok=True)
        quality_image_block = []

        with open(fastq_path, 'r') as file:
            for record in SeqIO.parse(file, "fastq"):
                quality_gray_values = [min(q * 2, 255) for q in record.letter_annotations["phred_quality"]]
                quality_image_block.append(quality_gray_values)

                if len(quality_image_block) == block_size:
                    tiff.imwrite(f"{output_path}/grayimage_quality_{len(quality_image_block)}.tiff", np.array(quality_image_block, dtype=np.uint8))
                    quality_image_block = []

            if quality_image_block:
                tiff.imwrite(f"{output_path}/grayimage_quality_{len(quality_image_block)}.tiff", np.array(quality_image_block, dtype=np.uint8))

        end_time = time.time()
        print(f"处理完成: {fastq_path} 时间: {end_time - start_time} 秒")
        return True
    except Exception as e:
        logging.error(f"错误处理文件: {fastq_path} 错误: {str(e)}")
        return False

def process_all_fastq(input_directory, output_base_path):
    archive_directory = os.path.join(input_directory, 'archive')
    os.makedirs(archive_directory, exist_ok=True)  # 确保存档目录存在

    for file_name in os.listdir(input_directory):
        if file_name.endswith('.fastq'):
            fastq_path = os.path.join(input_directory, file_name)
            output_path = os.path.join(output_base_path, os.path.splitext(file_name)[0] + '_grayimage')
            os.makedirs(output_path, exist_ok=True)
            if fastq_to_image_segmented(fastq_path, output_path):
                shutil.move(fastq_path, os.path.join(archive_directory, file_name))
                print(f"成功处理并存档文件: {file_name}")
            else:
                print(f"跳过文件 {file_name} 由于处理错误.")

input_directory = 'input'
output_base_path = 'cache/change_to_gray'
process_all_fastq(input_directory, output_base_path)

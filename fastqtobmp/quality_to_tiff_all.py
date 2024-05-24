from Bio import SeqIO
import numpy as np
import tifffile as tiff
import time
import os
import shutil

def fastq_to_image_segmented(fastq_path, output_path, block_size=64 * 1024):
    """
    将 FASTQ 文件分批读取并转换为图像，每批的大小接近给定的 block_size。
    """
    start_time = time.time()
    os.makedirs(output_path, exist_ok=True)
    with open(fastq_path, 'r') as file:
        first_record = next(SeqIO.parse(file, "fastq"))
        read_length = len(first_record.seq)
    bytes_per_read = read_length
    reads_per_block = block_size // bytes_per_read

    read_count = 0
    block_count = 0
    quality_image_block = []

    with open(fastq_path, 'r') as file:
        for record in SeqIO.parse(file, "fastq"):
            quality_gray_values = [min(q * 2, 255) for q in record.letter_annotations["phred_quality"]]
            quality_image_block.append(quality_gray_values)
            read_count += 1
            if len(quality_image_block) == reads_per_block:
                block_count += 1
                tiff.imwrite(f"{output_path}/grayimage_quality_{block_count}.tiff", np.array(quality_image_block, dtype=np.uint8))
                print(f"图像块 {block_count} 已保存。")
                quality_image_block = []
    if quality_image_block:
        block_count += 1
        tiff.imwrite(f"{output_path}/grayimage_quality_{block_count}.tiff", np.array(quality_image_block, dtype=np.uint8))
        print(f"最后的图像块 {block_count} 已保存。")
    end_time = time.time()
    print(f"代码执行时间: {end_time - start_time} 秒")
    return read_count, reads_per_block, block_count

def process_all_fastq(input_directory, output_base_path):
    """
    处理 input_directory 下的所有 .fastq 文件，并将结果输出到以文件名命名的目录中。
    """
    for file_name in os.listdir(input_directory):
        # 忽略ERR3365952.fastq文件
        if file_name == 'ERR3365952.fastq':
            continue
        if file_name.endswith('.fastq'):
            try:
                fastq_to_image_segmented(fastq_path, output_path)
            except Exception as e:
                print(f"处理文件 {fastq_path} 时遇到错误：{e}，跳过该文件。")
                continue  # 发生异常时跳过当前文件，继续处理下一个文件
            fastq_path = os.path.join(input_directory, file_name)
            output_path = os.path.join(output_base_path, os.path.splitext(file_name)[0] + '_grayimage')
            os.makedirs(output_path, exist_ok=True)

            shutil.move(fastq_path, os.path.join(input_directory, 'archive', file_name))
            print(f"Processing {fastq_path} into {output_path}")

input_directory = 'input'
output_base_path = 'cache/change_to_gray'
process_all_fastq(input_directory, output_base_path)
from Bio import SeqIO
import numpy as np
import tifffile as tiff
import time

def fastq_to_image_segmented(fastq_path, output_path):
    start_time = time.time()

    base_to_gray = {'A': 32, 'T': 64, 'G': 192, 'C': 224, 'N': 0}
    target_image_size_bytes = 64 * 1024 * 1024  # 一次处理64MB，序列和质量图像各占一半

    with open(fastq_path, 'r') as file:
        first_record = next(SeqIO.parse(file, "fastq"))
        read_length = len(first_record.seq)
        image_height = target_image_size_bytes // (2 * read_length)
        base_image_block = np.zeros((image_height, read_length), dtype=np.uint8)
        quality_image_block = np.zeros((image_height, read_length), dtype=np.uint8)

    read_count = 0

    with open(fastq_path, 'r') as file:
        for record in SeqIO.parse(file, "fastq"):
            base_gray_values = [base_to_gray.get(base, 0) for base in record.seq]
            base_image_block[read_count % image_height, :] = base_gray_values

            quality_gray_values = [min(q * 2, 255) for q in record.letter_annotations["phred_quality"]]
            quality_image_block[read_count % image_height, :] = quality_gray_values

            if read_count % image_height == image_height - 1:
                tiff.imwrite(f"{output_path}_base_{read_count // image_height + 1}.tiff", base_image_block)
                tiff.imwrite(f"{output_path}_quality_{read_count // image_height + 1}.tiff", quality_image_block)
                print(f"图像块 {read_count // image_height + 1} 已保存。")
                base_image_block = np.zeros((image_height, read_length), dtype=np.uint8)
                quality_image_block = np.zeros((image_height, read_length), dtype=np.uint8)

            read_count += 1

        if read_count % image_height > 0:
            final_base_image_block = base_image_block[:read_count % image_height, :]
            final_quality_image_block = quality_image_block[:read_count % image_height, :]
            tiff.imwrite(f"{output_path}_base_{read_count // image_height + 1}.tiff", final_base_image_block)
            tiff.imwrite(f"{output_path}_quality_{read_count // image_height + 1}.tiff", final_quality_image_block)
            total_blocks = read_count // image_height + 1
            print(f"最后的图像块 {total_blocks} 已保存。")

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"代码执行时间: {execution_time} 秒")

    # 返回读取的reads数
    return read_count,read_length,image_height,total_blocks

# 示例文件路径（需要替换为实际路径）
fastq_path = "input/SRR554369.fastq"
output_path = "cache/change_to_gray/grayimage"

# 调用函数处理FASTQ文件并接收read_count
read_count,read_length,image_height,total_blocks = fastq_to_image_segmented(fastq_path, output_path)

# 打印处理的reads数量
print(f"处理的reads数量: {read_count}，每个read的长度: {read_length}，图像的高度: {image_height}，一共有: {total_blocks}个图像块。")
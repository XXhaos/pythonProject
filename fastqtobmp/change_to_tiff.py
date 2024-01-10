from Bio import SeqIO
import numpy as np
import tifffile as tiff


def fastq_to_image_segmented(fastq_path, output_path):
    # 碱基到灰度值的映射
    base_to_gray = {'A': 32, 'T': 64, 'G': 192, 'C': 224, 'N': 0}

    # 初始化图像块的高度
    image_height = 2000000

    # 使用 BioPython 读取 FASTQ 文件的第一个 read 以确定 reads 的长度
    with open(fastq_path, 'r') as file:
        first_record = next(SeqIO.parse(file, "fastq"))
        read_length = len(first_record.seq)
        # 初始化碱基图像块和质量分数图像块
        base_image_block = np.zeros((image_height, read_length), dtype=np.uint8)
        quality_image_block = np.zeros((image_height, read_length), dtype=np.uint8)

    # 用于记录当前处理的 reads 数量
    read_count = 0

    # 使用 with open 结构读取 FASTQ 文件
    with open(fastq_path, 'r') as file:
        for record in SeqIO.parse(file, "fastq"):
            # 将碱基序列转换为灰度值
            base_gray_values = [base_to_gray.get(base, 0) for base in record.seq]
            base_image_block[read_count % image_height, :] = base_gray_values

            # 将质量分数转换为灰度值
            quality_gray_values = [min(q * 2, 255) for q in record.letter_annotations["phred_quality"]]
            quality_image_block[read_count % image_height, :] = quality_gray_values

            # 当达到图像块的高度时，保存图像并重置图像块
            if read_count % image_height == image_height - 1:
                tiff.imwrite(f"{output_path}_base_{read_count // image_height + 1}.tiff", base_image_block)
                tiff.imwrite(f"{output_path}_quality_{read_count // image_height + 1}.tiff", quality_image_block)
                print(f"图像块 {read_count // image_height + 1} 已保存。")
                base_image_block = np.zeros((image_height, read_length), dtype=np.uint8)
                quality_image_block = np.zeros((image_height, read_length), dtype=np.uint8)

            read_count += 1

        # 检查并保存最后一个不完整的图像块
        if read_count % image_height > 0:
            final_base_image_block = base_image_block[:read_count % image_height, :]
            final_quality_image_block = quality_image_block[:read_count % image_height, :]
            tiff.imwrite(f"{output_path}_base_{read_count // image_height + 1}.tiff", final_base_image_block)
            tiff.imwrite(f"{output_path}_quality_{read_count // image_height + 1}.tiff", final_quality_image_block)
            print(f"最后的图像块 {read_count // image_height + 1} 已保存。")

# 示例文件路径（需要替换为实际路径）
fastq_path = "input/SRR554369.fastq"
output_path = "cache/change_to_gray/grayimage"

# 调用函数处理 FASTQ 文件
fastq_to_image_segmented(fastq_path, output_path)
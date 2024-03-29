from Bio import SeqIO
import numpy as np
import tifffile as tiff
import time

def fastq_to_image_segmented(fastq_path, output_path, block_size=4096 * 1024 * 1024):
    """
    将 FASTQ 文件分块读取并转换为 FASTQ 图像。

    参数：
    fastq_path：FASTQ 文件路径。
    output_path：输出图像路径。
    block_size：每个图像块的大小（以字节为单位）。
    """

    start_time = time.time()

    base_to_gray = {'A': 32, 'T': 64, 'G': 192, 'C': 224, 'N': 0}

    with open(fastq_path, 'r') as file:
        record = next(SeqIO.parse(file, "fastq"))
        read_length = len(record.seq)
        image_height = block_size // read_length

    read_count = 0
    block_count = 0

    with open(fastq_path, 'r') as file:
        base_image_block = np.zeros((image_height, read_length), dtype=np.uint8)
        quality_image_block = np.zeros((image_height, read_length), dtype=np.uint8)

        for record in SeqIO.parse(file, "fastq"):
            base_gray_values = [base_to_gray.get(base, 0) for base in record.seq]
            base_image_block[read_count % image_height, :] = base_gray_values

            quality_gray_values = [min(q * 2, 255) for q in record.letter_annotations["phred_quality"]]
            quality_image_block[read_count % image_height, :] = quality_gray_values

            read_count += 1

            # 检查是否需要保存图像块
            if read_count % image_height == 0:
                block_count += 1
                tiff.imwrite(f"{output_path}_base_{block_count}.tiff", base_image_block)
                tiff.imwrite(f"{output_path}_quality_{block_count}.tiff", quality_image_block)
                print(f"图像块 {block_count} 已保存。")
                base_image_block = np.zeros((image_height, read_length), dtype=np.uint8)
                quality_image_block = np.zeros((image_height, read_length), dtype=np.uint8)

        # 保存最后一个图像块
        if read_count % image_height > 0:
            block_count += 1
            final_base_image_block = base_image_block[:read_count % image_height, :]
            final_quality_image_block = quality_image_block[:read_count % image_height, :]
            tiff.imwrite(f"{output_path}_base_{block_count}.tiff", final_base_image_block)
            tiff.imwrite(f"{output_path}_quality_{block_count}.tiff", final_quality_image_block)
            print(f"最后的图像块 {block_count} 已保存。")

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"代码执行时间: {execution_time} 秒")

    return read_count, read_length, image_height, block_count

# 示例文件路径（需要替换为实际路径）
fastq_path = "input/ERR3365952.fastq"
output_path = "cache/change_to_gray/grayimage"

# 调用函数处理FASTQ文件并接收read_count
read_count,read_length,image_height,total_blocks = fastq_to_image_segmented(fastq_path, output_path)

# 打印处理的reads数量
print(f"处理的reads数量: {read_count}，每个read的长度: {read_length}，图像的高度: {image_height}，一共有: {total_blocks}个图像块。")
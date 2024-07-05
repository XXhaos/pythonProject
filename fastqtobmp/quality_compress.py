import os
from Bio import SeqIO
import numpy as np
import time


def process_quality_chunk(quality_scores, chunk_index):
    quality_scores = np.array(quality_scores, dtype=int)

    # 创建输出目录
    quality_output_folder = "D:\\pythonProject\\fastqtobmp\\input\\quality_scores"
    quality_compress_output_folder = "D:\\pythonProject\\fastqtobmp\\input\\quality_scores_compress"

    os.makedirs(quality_output_folder, exist_ok=True)
    os.makedirs(quality_compress_output_folder, exist_ok=True)

    # 将质量分数转换为txt文件
    quality_path = os.path.join(quality_output_folder, f'quality_{chunk_index}.txt')
    np.savetxt(quality_path, quality_scores, fmt='%d')

    # 调用lpaq8压缩
    quality_compress_path = os.path.join(quality_compress_output_folder, f'quality_{chunk_index}.txt.compressed')
    os.system(f'D:\\pythonProject\\lpaq8\\lpaq8.exe 9 {quality_path} {quality_compress_path}')

    # 删除未压缩的质量分数文件
    os.remove(quality_path)


def main():
    start_time = time.time()
    input_file = "/fastqtobmp/input/SRR554369.fastq"
    chunk_size = 16 * 1024 * 1024  # 16 MB

    chunk_index = 0
    quality_scores = []
    total_size = 0

    for record in SeqIO.parse(input_file, "fastq"):
        quality = record.letter_annotations["phred_quality"]
        total_size += len(quality)
        quality_scores.append(quality)
        if total_size >= chunk_size:
            process_quality_chunk(quality_scores, chunk_index)
            chunk_index += 1
            quality_scores = []
            total_size = 0

    # 处理剩余部分
    if quality_scores:
        process_quality_chunk(quality_scores, chunk_index)

    end_time = time.time()
    print(f'所有质量分数块处理完成，运行时间: {end_time - start_time:.2f} 秒')


if __name__ == "__main__":
    main()

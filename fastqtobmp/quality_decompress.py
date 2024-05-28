import os
import numpy as np
import time


def restore_quality_chunk(quality_compress_path, quality_path):
    # 调用lpaq8解压缩
    os.system(f'D:\\pythonProject\\lpaq8\\lpaq8.exe d {quality_compress_path} {quality_path}')

    # 读取解压缩的质量分数文件
    quality_scores = np.loadtxt(quality_path, dtype=int)

    # 删除未压缩的质量分数文件
    os.remove(quality_path)

    return quality_scores


def main():
    start_time = time.time()

    quality_compress_folder = "D:\\pythonProject\\fastqtobmp\\input\\quality_scores_compress"
    output_fastq = "D:\\pythonProject\\fastqtobmp\\input\\recovered_quality.fastq"
    os.makedirs(os.path.dirname(output_fastq), exist_ok=True)

    quality_compress_files = [f for f in os.listdir(quality_compress_folder) if
                              f.startswith('quality_') and f.endswith('.compressed')]

    with open(output_fastq, 'w') as out_file:
        for quality_compress_file in sorted(quality_compress_files, key=lambda x: int(x.split('_')[1].split('.')[0])):
            chunk_index = quality_compress_file.split('_')[1].split('.')[0]
            quality_compress_path = os.path.join(quality_compress_folder, quality_compress_file)
            quality_path = os.path.join(quality_compress_folder, f'quality_{chunk_index}.txt')

            quality_scores = restore_quality_chunk(quality_compress_path, quality_path)

            for i, quality in enumerate(quality_scores):
                out_file.write(f"@SEQ_ID_{chunk_index}_{i}\n")
                out_file.write("N" * len(quality) + "\n")  # 随意填充序列
                out_file.write("+\n")
                out_file.write("".join(chr(q + 33) for q in quality) + "\n")

    end_time = time.time()
    print(f'所有质量分数还原完成，运行时间: {end_time - start_time:.2f} 秒')


if __name__ == "__main__":
    main()
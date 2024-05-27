import os
import numpy as np
from Bio import SeqIO
import time

# 符号到索引的映射
symbol_to_index = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'N': 4}
index_to_symbol = {0: 'A', 1: 'C', 2: 'G', 3: 'T', 4: 'N', 5: 'P'}

def fill_Z_prime(Z, Z_prime, freq_array):
    rows, cols = Z.shape
    for i in range(1, rows):
        for j in range(1, cols):
            left_up = Z[i - 1, j - 1] if i > 0 and j > 0 else 0
            left = Z[i, j - 1] if j > 0 else 0
            up = Z[i - 1, j] if i > 0 else 0
            current = Z[i, j]

            prediction = predict_value(freq_array, left_up, left, up)

            if prediction == current:
                Z_prime[i, j] = 5  # 用5表示预测正确
            else:
                Z_prime[i, j] = current  # 用当前值表示预测错误

            update_frequency_array(freq_array, left_up, left, up, current)

def predict_value(freq_array, left_up, left, up):
    frequencies = freq_array[left_up, left, up]
    if np.all(frequencies == 0):
        return -1
    return np.argmax(frequencies)

def update_frequency_array(freq_array, left_up, left, up, current):
    freq_array[left_up, left, up, current] += 1

def process_chunk(reads, chunk_index):
    read_length = len(reads[0])
    Z = np.array([[symbol_to_index[base] for base in read] for read in reads])
    Z_prime = np.zeros_like(Z, dtype=int)

    # 初始化独立的频率数组
    freq_array = np.zeros((5, 5, 5, 5), dtype=int)

    # 初始化Z_prime的第一行和第一列
    Z_prime[0, :] = Z[0, :]
    Z_prime[:, 0] = Z[:, 0]

    # 填充Z_prime剩余部分
    fill_Z_prime(Z, Z_prime, freq_array)

    # 创建输出目录
    Z_output_folder = "D:\\pythonProject\\fastqtobmp\\input\\Z"
    Z_prime_output_folder = "D:\\pythonProject\\fastqtobmp\\input\\Z_prime"
    Z_compress_output_folder = "D:\\pythonProject\\fastqtobmp\\input\\Z_compress"
    Z_prime_compress_output_folder = "D:\\pythonProject\\fastqtobmp\\input\\Z_prime_compress"

    os.makedirs(Z_output_folder, exist_ok=True)
    os.makedirs(Z_prime_output_folder, exist_ok=True)
    os.makedirs(Z_compress_output_folder, exist_ok=True)
    os.makedirs(Z_prime_compress_output_folder, exist_ok=True)

    # 将Z和Z_prime转换为txt文件
    Z_path = os.path.join(Z_output_folder, f'Z_{chunk_index}.txt')
    Z_prime_path = os.path.join(Z_prime_output_folder, f'Z_prime_{chunk_index}.txt')

    np.savetxt(Z_path, Z, fmt='%d')
    np.savetxt(Z_prime_path, Z_prime, fmt='%d')

    # 调用lpaq8压缩
    Z_compress_path = os.path.join(Z_compress_output_folder, f'Z_{chunk_index}.txt.compressed')
    Z_prime_compress_path = os.path.join(Z_prime_compress_output_folder, f'Z_prime_{chunk_index}.txt.compressed')

    os.system(f'D:\\pythonProject\\lpaq8\\lpaq8.exe 9 {Z_path} {Z_compress_path}')
    os.system(f'D:\\pythonProject\\lpaq8\\lpaq8.exe 9 {Z_prime_path} {Z_prime_compress_path}')

def main():
    start_time = time.time()
    input_file = "D:\\pythonProject\\fastqtobmp\\input\\ERR3365952.fastq"
    chunk_size = 16 * 1024 * 1024  # 16 MB

    chunk_index = 0
    reads = []
    total_size = 0

    for record in SeqIO.parse(input_file, "fastq"):
        seq = str(record.seq)
        total_size += len(seq)
        reads.append(seq)
        if total_size >= chunk_size:
            process_chunk(reads, chunk_index)
            chunk_index += 1
            reads = []
            total_size = 0

    # 处理剩余部分
    if reads:
        process_chunk(reads, chunk_index)

    end_time = time.time()
    print(f'所有块处理完成，运行时间: {end_time - start_time:.2f} 秒')

if __name__ == "__main__":
    main()
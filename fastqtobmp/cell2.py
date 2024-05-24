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
    # 如果所有频率都为0，则返回-1表示无法预测
    if np.all(frequencies == 0):
        return -1
    return np.argmax(frequencies)

def update_frequency_array(freq_array, left_up, left, up, current):
    freq_array[left_up, left, up, current] += 1

def main():
    input_file = "D:\\pythonProject\\fastqtobmp\\input\\ERR3365952.fastq"
    output_folder = os.path.dirname(input_file)
    chunk_size = 16 * 1024 * 1024  # 16 MB

    reads = []
    total_size = 0
    for record in SeqIO.parse(input_file, "fastq"):
        seq = str(record.seq)
        total_size += len(seq)
        reads.append(seq)
        if total_size >= chunk_size:
            break

    read_length = len(reads[0])
    num_reads_in_chunk = chunk_size // read_length

    Z = np.array([[symbol_to_index[base] for base in read] for read in reads[:num_reads_in_chunk]])
    Z_prime = np.zeros_like(Z, dtype=int)

    # 初始化Z'的第一行和第一列
    Z_prime[0, :] = Z[0, :]
    Z_prime[:, 0] = Z[:, 0]

    # 初始化频率数组
    freq_array = np.zeros((5, 5, 5, 5), dtype=int)

    # 填充Z_prime
    fill_Z_prime(Z, Z_prime, freq_array)

    # 将Z和Z_prime转换为txt文件
    Z_path = os.path.join(output_folder, 'Z_0.txt')
    Z_prime_path = os.path.join(output_folder, 'Z_prime_0.txt')

    np.savetxt(Z_path, Z, fmt='%d')
    np.savetxt(Z_prime_path, Z_prime, fmt='%d')

    # 调用lpaq8压缩
    start_time = time.time()
    os.system(f'D:\\pythonProject\\lpaq8\\lpaq8.exe 9 {Z_path} {Z_path}.compressed')
    os.system(f'D:\\pythonProject\\lpaq8\\lpaq8.exe 9 {Z_prime_path} {Z_prime_path}.compressed')
    end_time = time.time()

    print(f'压缩完成，运行时间: {end_time - start_time:.2f} 秒')

if __name__ == "__main__":
    main()

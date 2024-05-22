import os
import numpy as np
from collections import defaultdict
from itertools import product
from heapq import heappush, heappop, heapify

# 定义符号到索引的映射和反向映射
symbol_to_index = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'N': 4}
index_to_symbol = {0: 'A', 1: 'C', 2: 'G', 3: 'T', 4: 'N'}


# 从FASTQ文件中读取序列并拼接成矩阵Z
def read_fastq(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        sequences = [line.strip() for i, line in enumerate(lines) if i % 4 == 1]
    return np.array([list(seq) for seq in sequences])


# 初始化预测矩阵Z'
def initialize_Z_prime(Z):
    Z_prime = np.zeros(Z.shape, dtype=int)
    Z_prime[:4, :4] = np.vectorize(symbol_to_index.get)(Z[:4, :4])
    return Z_prime


# 生成四维频率数组
def initialize_frequency_array():
    return np.zeros((5, 5, 5, 5), dtype=int)


# 更新频率数组
def update_frequency_array(freq_array, left_up, left, up, current):
    freq_array[left_up, left, up, current] += 1


# 预测值
def predict_value(freq_array, left_up, left, up):
    predictions = freq_array[left_up, left, up]
    return np.argmax(predictions)


# 填充预测矩阵Z'
def fill_Z_prime(Z, Z_prime, freq_array):
    rows, cols = Z.shape
    for i in range(4, rows):
        for j in range(4, cols):
            left_up = symbol_to_index[Z[i - 1, j - 1]] if i > 0 and j > 0 else 0
            left = symbol_to_index[Z[i, j - 1]] if j > 0 else 0
            up = symbol_to_index[Z[i - 1, j]] if i > 0 else 0
            current = symbol_to_index[Z[i, j]]

            prediction = predict_value(freq_array, left_up, left, up)
            if prediction == current:
                Z_prime[i, j] = -1  # 用-1表示预测正确
            else:
                Z_prime[i, j] = current

            update_frequency_array(freq_array, left_up, left, up, current)


# 计算每个符号的出现频率
def calculate_frequencies(freq_array):
    frequencies = np.sum(freq_array, axis=(0, 1, 2))
    freq_dict = {index_to_symbol[i]: freq for i, freq in enumerate(frequencies)}
    freq_dict[-1] = 0  # 添加-1的频率
    return freq_dict


# 生成哈夫曼编码
def huffman_encoding(frequencies):
    heap = [[weight, [symbol, ""]] for symbol, weight in frequencies.items()]
    heapify(heap)
    while len(heap) > 1:
        lo = heappop(heap)
        hi = heappop(heap)
        for pair in lo[1:]:
            pair[1] = '0' + pair[1]
        for pair in hi[1:]:
            pair[1] = '1' + pair[1]
        heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
    huff_dict = sorted(heappop(heap)[1:], key=lambda p: (len(p[-1]), p))
    return {symbol: code for symbol, code in huff_dict}


# 用哈夫曼编码重新编码矩阵Z'
def reencode_Z_prime(Z_prime, huff_dict):
    rows, cols = Z_prime.shape
    encoded_Z_prime = ""
    for i in range(rows):
        for j in range(cols):
            symbol = Z_prime[i, j]
            if symbol == -1:
                encoded_Z_prime += huff_dict['-1']
            else:
                encoded_Z_prime += huff_dict[symbol]
    return encoded_Z_prime


# 保存重新编码的Z'为字节流
def save_encoded_Z_prime(encoded_Z_prime, file_path):
    with open(file_path, 'wb') as file:
        file.write(encoded_Z_prime.encode())


# 调用外部压缩算法
def compress_file(input_path, output_path):
    os.system(f'D:\\pythonProject\\lpaq8\\lpaq8.exe c {input_path} {output_path}')


# 主函数
def main():
    input_file = 'path_to_your_fastq_file.fastq'
    Z = read_fastq(input_file)
    Z_prime = initialize_Z_prime(Z)
    freq_array = initialize_frequency_array()

    fill_Z_prime(Z, Z_prime, freq_array)

    frequencies = calculate_frequencies(freq_array)
    huff_dict = huffman_encoding(frequencies)

    encoded_Z_prime = reencode_Z_prime(Z_prime, huff_dict)

    encoded_Z_prime_path = 'encoded_Z_prime.bin'

    save_encoded_Z_prime(encoded_Z_prime, encoded_Z_prime_path)

    compress_file(encoded_Z_prime_path, encoded_Z_prime_path + '.compressed')


if __name__ == "__main__":
    main()

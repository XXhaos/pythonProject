import os
import numpy as np
import time
import subprocess

# 定义映射
symbol_to_index = {'A': 0, 'C': 1, 'G': 2, 'T': 3, 'N': 4}
index_to_symbol = {0: 'A', 1: 'C', 2: 'G', 3: 'T', 4: 'N', 5: 'P'}


def fill_Z(Z_prime, Z, freq_array):
    rows, cols = Z.shape
    for i in range(1, rows):
        for j in range(1, cols):
            left_up = Z[i - 1, j - 1] if i > 0 and j > 0 else 0
            left = Z[i, j - 1] if j > 0 else 0
            up = Z[i - 1, j] if i > 0 else 0

            prediction = predict_value(freq_array, left_up, left, up)

            if Z_prime[i, j] == 5:
                Z[i, j] = prediction
            else:
                Z[i, j] = Z_prime[i, j]

            update_frequency_array(freq_array, left_up, left, up, Z[i, j])


def predict_value(freq_array, left_up, left, up):
    frequencies = freq_array[left_up, left, up]
    if np.all(frequencies == 0):
        return -1
    return np.argmax(frequencies)


def update_frequency_array(freq_array, left_up, left, up, current):
    freq_array[left_up, left, up, current] += 1


def restore_Z_from_Z_prime(z_prime_path, z_output_path):
    Z_prime = np.loadtxt(z_prime_path, dtype=int)
    Z = np.zeros_like(Z_prime, dtype=int)

    # 初始化独立的频率数组
    freq_array = np.zeros((5, 5, 5, 5), dtype=int)

    # 初始化Z的第一行和第一列
    Z[:, 0] = Z_prime[:, 0]
    Z[0, :] = Z_prime[0, :]

    # 填充Z的剩余部分
    fill_Z(Z_prime, Z, freq_array)

    # 保存还原的Z
    np.savetxt(z_output_path, Z, fmt='%d')


def generate_fastq_from_Z(Z_matrix, fastq_file):
    for row in Z_matrix:
        sequence = ''.join(index_to_symbol[val] for val in row)
        fastq_file.write(f"@Sequence\n")
        fastq_file.write(f"{sequence}\n")
        fastq_file.write(f"+\n")
        fastq_file.write(f"{'~' * len(sequence)}\n")  # 用'~'字符填充质量值行


def main():
    # 记录开始时间
    start_time = time.time()

    z_prime_compress_folder = "D:\\pythonProject\\fastqtobmp\\input\\Z_prime_compress"
    decompress_folder = "D:\\pythonProject\\fastqtobmp\\input\\decompress"
    z_output_folder = "D:\\pythonProject\\fastqtobmp\\input\\Z"
    fastq_output_file = "D:\\pythonProject\\fastqtobmp\\input\\output.fastq"

    os.makedirs(decompress_folder, exist_ok=True)
    os.makedirs(z_output_folder, exist_ok=True)

    z_prime_compress_files = sorted([f for f in os.listdir(z_prime_compress_folder) if f.endswith('.txt.compressed')],
                                    key=lambda x: int(x.split('_')[2].split('.')[0]))

    with open(fastq_output_file, 'w') as fastq_file:
        for z_prime_compress_file in z_prime_compress_files:
            chunk_index = z_prime_compress_file.split('_')[2].split('.')[0]
            z_prime_compress_path = os.path.join(z_prime_compress_folder, z_prime_compress_file)
            z_prime_path = os.path.join(decompress_folder, f'Z_prime_{chunk_index}.txt')
            z_output_path = os.path.join(z_output_folder, f'Z_{chunk_index}.txt')

            # 解压缩Z_prime文件
            subprocess.run(['D:\\pythonProject\\lpaq8\\lpaq8.exe', 'd', z_prime_compress_path, z_prime_path],
                           check=True)

            # 还原Z矩阵
            restore_Z_from_Z_prime(z_prime_path, z_output_path)

            # 根据Z矩阵生成FASTQ文件并写入到一个文件中
            Z_matrix = np.loadtxt(z_output_path, dtype=int)
            generate_fastq_from_Z(Z_matrix, fastq_file)

            # 删除临时解压缩文件
            os.remove(z_prime_path)
            os.remove(z_output_path)

            print(f'{z_prime_compress_file} 还原并写入FASTQ文件完成')

    # 记录结束时间
    end_time = time.time()
    print(f'所有文件还原并写入FASTQ文件完成，耗时 {end_time - start_time:.2f} 秒')


if __name__ == "__main__":
    main()
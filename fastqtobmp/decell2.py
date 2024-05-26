import os
import numpy as np

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

def restore_Z_from_Z_prime(z_prime_path, z_output_path, freq_array):
    Z_prime = np.loadtxt(z_prime_path, dtype=int)
    Z = np.zeros_like(Z_prime, dtype=int)

    # 初始化Z的第一行和第一列
    Z[:, 0] = Z_prime[:, 0]
    Z[0, :] = Z_prime[0, :]

    # 填充Z的剩余部分
    fill_Z(Z_prime, Z, freq_array)

    # 保存还原的Z
    np.savetxt(z_output_path, Z, fmt='%d')

def main():
    input_folder = "D:\\pythonProject\\fastqtobmp\\input\\Z_prime"
    output_folder = "D:\\pythonProject\\fastqtobmp\\input\\decell2"
    os.makedirs(output_folder, exist_ok=True)

    freq_array = np.zeros((5, 5, 5, 5), dtype=int)
    z_prime_files = [f for f in os.listdir(input_folder) if f.startswith('Z_prime_') and f.endswith('.txt')]

    for z_prime_file in z_prime_files:
        chunk_index = z_prime_file.split('_')[2].split('.')[0]
        z_prime_path = os.path.join(input_folder, z_prime_file)
        z_output_path = os.path.join(output_folder, f'Z_{chunk_index}.txt')

        restore_Z_from_Z_prime(z_prime_path, z_output_path, freq_array)
        print(f'{z_prime_file} 还原完成，保存为 {z_output_path}')

    print('所有文件还原完成')

if __name__ == "__main__":
    main()

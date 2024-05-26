import os
import numpy as np

def compare_files(file1, file2):
    data1 = np.loadtxt(file1, dtype=int)
    data2 = np.loadtxt(file2, dtype=int)
    return np.array_equal(data1, data2)

def main():
    original_folder = "D:\\pythonProject\\fastqtobmp\\input\\Z"
    restored_folder = "D:\\pythonProject\\fastqtobmp\\input\\decell2"

    original_files = [f for f in os.listdir(original_folder) if f.startswith('Z_') and f.endswith('.txt')]
    restored_files = [f for f in os.listdir(restored_folder) if f.startswith('Z_') and f.endswith('.txt')]

    all_files_matched = True

    for file in original_files:
        original_file_path = os.path.join(original_folder, file)
        restored_file_path = os.path.join(restored_folder, file)

        if not os.path.exists(restored_file_path):
            print(f'{restored_file_path} 文件不存在')
            all_files_matched = False
            continue

        if compare_files(original_file_path, restored_file_path):
            print(f'{file} 完全相同')
        else:
            print(f'{file} 不相同')
            all_files_matched = False

    if all_files_matched:
        print('所有文件完全相同')
    else:
        print('有些文件不相同')

if __name__ == "__main__":
    main()

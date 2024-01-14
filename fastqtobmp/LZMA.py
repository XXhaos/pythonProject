import lzma
import os
import time

def compress_files_with_lzma(directory):
    # 记录开始时间
    start_time = time.time()

    compressed_dir = os.path.join(directory, 'compressed')
    os.makedirs(compressed_dir, exist_ok=True)

    for filename in os.listdir(directory):
        if filename.endswith('.tiff'):
            file_path = os.path.join(directory, filename)
            compressed_file_path = os.path.join(compressed_dir, filename + '.xz')

            with open(file_path, 'rb') as file:
                file_data = file.read()

            # 使用LZMA进行无损压缩
            compressed_data = lzma.compress(file_data)

            # 保存压缩后的文件
            with open(compressed_file_path, 'wb') as compressed_file:
                compressed_file.write(compressed_data)
                print(f"Compressed and saved: {compressed_file_path}")

    # 记录结束时间
    end_time = time.time()
    # 打印执行时间
    execution_time = end_time - start_time
    print(f"代码执行时间: {execution_time} 秒")


# 指定需要压缩的文件夹路径
directory_path = 'cache/change_to_gray'
compress_files_with_lzma(directory_path)
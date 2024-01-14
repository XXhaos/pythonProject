import zstandard as zstd
import os
import time

def compress_files_with_zstd(directory):
    # 记录开始时间
    start_time = time.time()

    compressed_dir = os.path.join(directory, 'compressed')
    if not os.path.exists(compressed_dir):
        os.makedirs(compressed_dir)

    for filename in os.listdir(directory):
        if filename.endswith('.tiff'):
            file_path = os.path.join(directory, filename)
            compressed_file_name = filename + '.zst'
            compressed_file_path = os.path.join(compressed_dir, compressed_file_name)

            with open(file_path, 'rb') as file:
                file_data = file.read()

            # 使用Zstandard进行无损压缩
            compressed_data = zstd.ZstdCompressor().compress(file_data)

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
compress_files_with_zstd(directory_path)

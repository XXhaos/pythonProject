import brotli
import os

def compress_files_with_brotli(directory):
    # 创建保存压缩文件的文件夹路径
    compressed_folder = os.path.join(directory, 'compressed')
    if not os.path.exists(compressed_folder):
        os.makedirs(compressed_folder)

    for filename in os.listdir(directory):
        if filename.endswith('.tiff'):
            file_path = os.path.join(directory, filename)
            # 更改压缩文件的保存路径
            compressed_file_path = os.path.join(compressed_folder, filename + '.br')

            # 读取原始文件数据
            with open(file_path, 'rb') as file:
                file_data = file.read()

            # 使用Brotli进行无损压缩
            compressed_data = brotli.compress(file_data)

            # 保存压缩后的文件
            with open(compressed_file_path, 'wb') as compressed_file:
                compressed_file.write(compressed_data)
                print(f"Compressed and saved: {compressed_file_path}")

# 指定需要压缩的文件夹路径
directory_path = 'cache/change_to_gray'
compress_files_with_brotli(directory_path)
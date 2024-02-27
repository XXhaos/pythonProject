import lzma
import os
import time

def decompress_files_with_lzma(compressed_dir):
    # 记录开始时间
    start_time = time.time()

    decompressed_dir = os.path.join(compressed_dir, 'decompressed')
    os.makedirs(decompressed_dir, exist_ok=True)

    for filename in os.listdir(compressed_dir):
        if filename.endswith('.xz'):
            compressed_file_path = os.path.join(compressed_dir, filename)
            # 去除文件扩展名.xz，恢复为原始文件名
            decompressed_file_path = os.path.join(decompressed_dir, filename[:-3])

            with open(compressed_file_path, 'rb') as compressed_file:
                compressed_data = compressed_file.read()

            # 使用LZMA进行解压缩
            decompressed_data = lzma.decompress(compressed_data)

            # 保存解压缩后的文件
            with open(decompressed_file_path, 'wb') as decompressed_file:
                decompressed_file.write(decompressed_data)
                print(f"Decompressed and saved: {decompressed_file_path}")

    # 记录结束时间
    end_time = time.time()
    # 打印执行时间
    execution_time = end_time - start_time
    print(f"代码执行时间: {execution_time} 秒")

# 指定需要解压缩的文件夹路径，这个路径应该是压缩文件保存的地方
compressed_directory_path = 'cache/change_to_gray/compressed'
decompress_files_with_lzma(compressed_directory_path)
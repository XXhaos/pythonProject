import lzma
import os

def compress_files_with_lzma(directory):
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

# 指定需要压缩的文件夹路径
directory_path = 'cache/change_to_gray'
compress_files_with_lzma(directory_path)
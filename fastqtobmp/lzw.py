from PIL import Image
import os
import time

def compress_tiff_files_with_pillow(directory, compression='tiff_lzw'):
    # 记录开始时间
    start_time = time.time()

    for filename in os.listdir(directory):
        if filename.endswith('.tiff'):
            file_path = os.path.join(directory, filename)
            compressed_file_path = os.path.join(directory, 'compressed_' + filename)

            # 使用Pillow打开和保存图像
            with Image.open(file_path) as img:
                img.save(compressed_file_path, format='TIFF', compression=compression)
                print(f"Compressed and saved: {compressed_file_path}")

    # 记录结束时间
    end_time = time.time()
    # 打印执行时间
    execution_time = end_time - start_time
    print(f"代码执行时间: {execution_time} 秒")

# 指定需要压缩的文件夹路径
directory_path = 'cache/change_to_gray'
compress_tiff_files_with_pillow(directory_path)

from PIL import Image
import os
import time

def compress_tiff_files_with_pillow(directory, compression='tiff_adobe_deflate'):
    # 记录开始时间
    start_time = time.time()

    # 创建存放压缩文件的目录
    compressed_dir = os.path.join(directory, 'compressed')
    if not os.path.exists(compressed_dir):
        os.makedirs(compressed_dir)

    for filename in os.listdir(directory):
        if filename.endswith('.tiff'):
            file_path = os.path.join(directory, filename)
            # 修改后的压缩文件路径
            compressed_file_path = os.path.join(compressed_dir, 'compressed_' + filename)

            # 使用Pillow打开和保存图像
            with Image.open(file_path) as img:
                img.save(compressed_file_path, format='TIFF', compression=compression)
                print(f"Compressed and saved: {compressed_file_path}")

    # 记录结束时间
    end_time = time.time()
    print(f"总共用时 {end_time - start_time} 秒")

# 指定需要压缩的文件夹路径
directory_path = 'cache/change_to_gray'
compress_tiff_files_with_pillow(directory_path)
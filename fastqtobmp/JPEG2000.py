from PIL import Image
import os
import time

def compress_tiff_to_jpeg2000(directory):
    #记录开始时间
    start_time = time.time()

    # 在目标目录下创建 'compressed' 子文件夹
    compressed_dir = os.path.join(directory, 'compressed')
    if not os.path.exists(compressed_dir):
        os.makedirs(compressed_dir)

    for filename in os.listdir(directory):
        if filename.endswith('.tiff'):
            file_path = os.path.join(directory, filename)
            compressed_file_path = os.path.join(compressed_dir, filename.replace('.tiff', '.jp2'))

            # 使用Pillow打开TIFF图像并保存为JPEG 2000格式
            with Image.open(file_path) as img:
                img.save(compressed_file_path, format='JPEG2000', lossless=True)
                print(f"Compressed and saved: {compressed_file_path}")

    # 记录结束时间
    end_time = time.time()
    # 打印执行时间
    execution_time = end_time - start_time
    print(f"代码执行时间: {execution_time} 秒")

# 指定需要压缩的文件夹路径
directory_path = 'cache/change_to_gray'
compress_tiff_to_jpeg2000(directory_path)
import subprocess
import glob
import os
import time

def compress_all_images(image_directory, output_directory):
    #记录开始时间
    start_time = time.time()

    # 确保输出目录存在
    os.makedirs(output_directory, exist_ok=True)

    # 获取目录下的所有图像文件（包括png, jp2, webp, tiff格式）
    image_files = glob.glob(f"{image_directory}/*.*")
    image_files = [f for f in image_files if f.endswith(('.png', '.jp2', '.webp', '.tiff'))]

    for image_file in image_files:
        # 构建输出文件名
        output_file = f"{output_directory}/{image_file.split('/')[-1].split('.')[0]}"

        # 构建ZPAQ命令，并包含额外的参数
        command = f"zpaq a {output_file}.zpaq {image_file} -method 5 -threads 4"

        # 使用subprocess运行ZPAQ命令
        try:
            subprocess.run(command, check=True, shell=True)
            print(f"文件 {image_file} 已成功压缩为 {output_file}.zpaq")
        except subprocess.CalledProcessError as e:
            print(f"压缩文件 {image_file} 失败：", e)
        # 记录结束时间
        end_time = time.time()
        print(f"总共用时 {end_time - start_time} 秒")

# 示例用法
compress_all_images("cache/change_to_gray", "cache/backend_compressed_images")
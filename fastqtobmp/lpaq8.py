import os
import subprocess
import time

def compress_file(input_file, output_directory, lpaq8_path, compression_level='9'):
    """
    压缩指定的文件。

    参数:
    - input_file: 完整的输入文件路径。
    - output_directory: 压缩文件的输出目录。
    - lpaq8_path: lpaq8压缩器的完整路径。
    - compression_level: 压缩级别（默认为9，范围0-9）。
    """
    # 确保输出目录存在
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    compressed_filename = f"{os.path.splitext(os.path.basename(input_file))[0]}.lpaq8"
    output_path = os.path.join(output_directory, compressed_filename)

    # 调用lpaq8进行压缩
    compress_lpaq8(lpaq8_path, compression_level, input_file, output_path)


def compress_lpaq8(lpaq8_path, input_path, output_path, compression_level='9'):
    """
    使用lpaq8压缩单个文件。

    参数:
    - lpaq8_path: lpaq8的路径。
    - compression_level: 压缩级别。
    - input_path: 输入文件路径。
    - output_path: 输出文件路径。
    """
    command = [lpaq8_path, input_path, output_path, compression_level]
    try:
        subprocess.run(command, check=True)
        print(f"文件 {input_path} 压缩成功，保存为 {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"压缩过程中出错: {e}")
    except Exception as e:
        print(f"发生未知错误: {str(e)}")


def compress_all_files_in_directory(input_directory, output_directory, lpaq8_path, compression_level='9'):
    """
    压缩目录中的所有文件。

    参数:
    - input_directory: 输入目录路径。
    - output_directory: 输出目录路径。
    - lpaq8_path: lpaq8压缩器的完整路径。
    - compression_level: 压缩级别（默认为9，范围0-9）。
    """
    # 记录开始时间
    start_time = time.time()

    for root, dirs, files in os.walk(input_directory):
        for file in files:
            input_file_path = os.path.join(root, file)
            compress_file(input_file_path, output_directory, lpaq8_path, compression_level)

    # 记录结束时间
    end_time = time.time()

    print(f"所有文件已压缩完成。总共耗时: {(end_time - start_time)/60} 分钟。")

def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size / (1024 * 1024)  # 转换为MB

# 示例用法
input_directory1 = r"D:\pythonProject\fastqtobmp\input\change_to_gray" # 定义需要压缩的文件路径
destination_directory1 = r'D:\pythonProject\fastqtobmp\input\change_to_gray_lpaq8'  # 定义输出目录
lpaq8_exe_path = r"D:\pythonProject\lpaq8\lpaq8.exe"  # 确保这是正确的lpaq8路径

input_directory2 = r"D:\pythonProject\fastqtobmp\input\compressed" # 定义需要压缩的文件路径
destination_directory2 = r'D:\pythonProject\fastqtobmp\input\compressed_lpaq8'  # 定义输出目录

# 压缩目录中的所有文件
compress_all_files_in_directory(input_directory1, destination_directory1, lpaq8_exe_path)
compress_all_files_in_directory(input_directory2, destination_directory2, lpaq8_exe_path)

# 计算输出目录的大小，并转换为MB
size1 = get_directory_size(destination_directory1)
size2 = get_directory_size(destination_directory2)

# 输出两个目录大小的比较结果
difference = size1 - size2
print(f"{destination_directory1} 比 {destination_directory2} 大了 {difference:.2f} MB。")
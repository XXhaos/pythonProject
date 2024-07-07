import os
import subprocess

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
    for root, dirs, files in os.walk(input_directory):
        for file in files:
            input_file_path = os.path.join(root, file)
            compress_file(input_file_path, output_directory, lpaq8_path, compression_level)


# 示例用法
input_directory1 = r"D:\pythonProject\fastqtobmp\input\compressed\quality_reflection\q_prime" # 定义需要压缩的文件路径
destination_directory1 = r'D:\pythonProject\fastqtobmp\input\q_prime_lpaq8'  # 定义输出目录
lpaq8_exe_path = r"D:\pythonProject\lpaq8\lpaq8.exe"  # 确保这是正确的lpaq8路径

# 压缩目录中的所有文件
compress_all_files_in_directory(input_directory1, destination_directory1, lpaq8_exe_path)
import os
import subprocess

def decompress_lpaq8_files(compressed_directory, decompressed_directory, lpaq8_path):
    """
    解压缩指定目录下的所有.lpaq8文件。

    参数:
    - compressed_directory: 包含.lpaq8压缩文件的源目录。
    - decompressed_directory: 解压缩文件的输出目录。
    - lpaq8_path: lpaq8压缩器的完整路径。
    """
    # 确保输出目录存在
    if not os.path.exists(decompressed_directory):
        os.makedirs(decompressed_directory)

    # 遍历目录中的所有.lpaq8压缩文件
    for filename in os.listdir(compressed_directory):
        if filename.endswith('.lpaq8'):
            input_path = os.path.join(compressed_directory, filename)
            decompressed_filename = f"{os.path.splitext(filename)[0]}.tiff"
            output_path = os.path.join(decompressed_directory, decompressed_filename)

            # 调用lpaq8进行解压缩
            decompress_image(lpaq8_path, input_path, output_path)

def decompress_image(lpaq8_path, input_path, output_path):
    """
    使用lpaq8解压单个文件。

    参数:
    - lpaq8_path: lpaq8的路径。
    - input_path: 输入文件路径。
    - output_path: 输出文件路径。
    """
    command = [lpaq8_path, 'd', input_path, output_path]
    try:
        subprocess.run(command, check=True)
        print(f"文件 {input_path} 解压成功，保存为 {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"解压过程中出错: {e}")
    except Exception as e:
        print(f"发生未知错误: {str(e)}")

# 示例用法
compressed_files_directory = 'cache/compressed_images/'
decompressed_files_directory = 'cache/decompressed_images/'
lpaq8_exe_path = r"D:\pythonProject\lpaq8\lpaq8.exe"  # 确保这是正确的路径
decompress_lpaq8_files(compressed_files_directory, decompressed_files_directory, lpaq8_exe_path)

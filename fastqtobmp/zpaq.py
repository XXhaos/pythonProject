import os
import subprocess

def compress_file_with_zpaq(input_file, output_directory, zpaq_path):
    """
    使用zpaq压缩指定的文件。

    参数:
    - input_file: 完整的输入文件路径。
    - output_directory: 压缩文件的输出目录。
    - zpaq_path: zpaq压缩器的完整路径。
    """
    # 确保输出目录存在
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    output_file = f"{os.path.splitext(os.path.basename(input_file))[0]}.zpaq"
    output_path = os.path.join(output_directory, output_file)

    # 构建zpaq命令
    command = [zpaq_path, "add", output_path, input_file, "-method", "5"]
    try:
        subprocess.run(command, check=True)
        print(f"文件 {input_file} 压缩成功，保存为 {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"压缩过程中出错: {e}")
    except Exception as e:
        print(f"发生未知错误: {str(e)}")

# 示例用法
input_file_path = 'input/SRR554369_base_1/G_prime.txt'  # 定义需要压缩的文件
destination_directory = 'input/compressed/SRR554369_base_1'  # 定义输出目录
zpaq_exe_path = r"D:\pythonProject\zpaq715\zpaq.exe"  # 确保这是正确的zpaq路径
compress_file_with_zpaq(input_file_path, destination_directory, zpaq_exe_path)
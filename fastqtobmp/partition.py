# import re
# import os
#
#
# def split_ids(input_path, output_dir):
#     """
#     读取包含ID的文件，使用给定的分隔符分割这些ID，并将分割符和分割后的字段分别存储。
#
#     参数：
#     input_path：包含ID的文本文件路径。
#     output_dir：输出文件的目录。
#     """
#     # 确保输出目录存在
#     os.makedirs(output_dir, exist_ok=True)
#
#     # 设置分隔符
#     delimiters = '.:= _/-'
#     # 创建用于分割的正则表达式
#     split_pattern = re.compile(f'([{re.escape(delimiters)}])')
#
#     # 准备输出文件
#     fields_output_path = os.path.join(output_dir, 'split_fields.txt')
#     delimiters_output_path = os.path.join(output_dir, 'delimiters.txt')
#
#     with open(input_path, 'r') as f_in, \
#             open(fields_output_path, 'w') as f_fields, \
#             open(delimiters_output_path, 'w') as f_delimiters:
#
#         for line in f_in:
#             line = line.strip()
#             parts = split_pattern.split(line)  # 使用正则表达式分割ID
#
#             # 遍历分割结果，区分字段和分隔符
#             for part in parts:
#                 if part in delimiters:
#                     # 将分隔符写入分隔符文件
#                     f_delimiters.write(part + '\n')
#                 else:
#                     # 将字段写入字段文件
#                     f_fields.write(part + '\n')
#
#     print("分割完成，结果已保存到指定目录")
#
#
# # 示例文件路径（需要替换为实际路径）
# input_path = "input/ids_output/ids_output_1.txt"  # 示例ID文件路径
# output_dir = "input/split_results"  # 输出目录
#
# # 调用函数，分割ID并将结果保存到文件中
# split_ids(input_path, output_dir)


import subprocess
import os

def compress_with_lpaq8(input_file, compression_level=9):
    """
    使用 LPAQ8 压缩指定的文件。

    参数：
    input_file：待压缩的文件路径。
    compression_level：LPAQ8的压缩等级，默认为9。
    """
    # 构建 LPAQ8 命令
    output_file = f"{input_file}.lpaq8"
    command = [r"D:\pythonProject\lpaq8\lpaq8.exe", str(compression_level), input_file, output_file]

    # 执行 LPAQ8 命令
    try:
        subprocess.run(command, check=True)
        print(f"文件 {input_file} 已压缩为 {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"压缩失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

# 示例文件路径
fields_file = "input/split_results/split_fields.txt"
delimiters_file = "input/split_results/delimiters.txt"

# 压缩字段文件和分隔符文件
compress_with_lpaq8(fields_file)
compress_with_lpaq8(delimiters_file)
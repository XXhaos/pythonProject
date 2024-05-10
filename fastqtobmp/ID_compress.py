import os
import re
import subprocess


def split_and_compress_ids(input_dir, output_dir, compression_level=9):
    """
    分割指定目录下所有的 .txt 文件中的ID，保存分割结果和分隔符，并对这些文件使用LPAQ8进行压缩。

    参数：
    input_dir：包含 .txt 文件的源目录。
    output_dir：压缩文件的输出目录。
    compression_level：使用的LPAQ8的压缩等级。
    """
    # 定义ID的分隔符
    delimiters = '.:= _/-'
    delimiter_pattern = f"[{re.escape(delimiters)}]"

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 遍历源目录中的所有文件
    for file_name in os.listdir(input_dir):
        if file_name.endswith('.txt'):
            file_path = os.path.join(input_dir, file_name)
            base_name = os.path.splitext(file_name)[0]

            # 处理每个文件
            with open(file_path, 'r') as file:
                contents = file.read()

            # 分割ID
            fields = re.split(delimiter_pattern, contents)
            separators = re.findall(delimiter_pattern, contents)

            # 保存分割后的ID和分隔符到临时文件
            fields_path = os.path.join(output_dir, f"{base_name}_fields.txt")
            separators_path = os.path.join(output_dir, f"{base_name}_separators.txt")

            with open(fields_path, 'w') as f:
                f.write("\n".join(fields))
            with open(separators_path, 'w') as f:
                f.write("\n".join(separators))

            # 对每个文件进行压缩
            compress_file(fields_path, output_dir, compression_level)
            compress_file(separators_path, output_dir, compression_level)

            # 清理临时文件
            os.remove(fields_path)
            os.remove(separators_path)


def compress_file(file_path, output_dir, compression_level):
    """
    使用LPAQ8压缩单个文件。

    参数：
    file_path：待压缩的文件路径。
    output_dir：压缩文件的输出目录。
    compression_level：LPAQ8的压缩等级。
    """
    output_file = os.path.join(output_dir, os.path.basename(file_path) + ".lpaq8")
    command = [r"D:\pythonProject\lpaq8\lpaq8.exe", str(compression_level), file_path, output_file]
    try:
        subprocess.run(command, check=True)
        print(f"文件 {file_path} 已压缩为 {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"压缩过程中出错: {e}")
    except Exception as e:
        print(f"发生错误: {str(e)}")


# 示例文件路径和输出目录
source_directory = "cache/ids_output"
destination_directory = "cache/ids_compress"

# 调用函数处理所有 .txt 文件并压缩
split_and_compress_ids(source_directory, destination_directory)
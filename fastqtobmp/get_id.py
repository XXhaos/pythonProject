import os


def extract_full_ids_to_txt(fastq_path, output_dir, reads_per_file):
    """
    从 FASTQ 文件中提取完整的 ID 行，并分批将它们写入到不同的 TXT 文件中。
    每个文件包含指定数量的 ID。

    参数：
    fastq_path：FASTQ 文件的路径。
    output_dir：输出文件的目录。
    reads_per_file：每个输出文件应包含的 reads 数量。
    """
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 初始化计数器和文件索引
    count = 0
    file_index = 1

    # 准备第一个输出文件
    output_txt_path = os.path.join(output_dir, f'ids_output_{file_index}.txt')
    f_out = open(output_txt_path, 'w')

    # 打开并读取 FASTQ 文件
    with open(fastq_path, 'r') as file:
        while True:
            id_line = file.readline().strip()  # 读取 ID 行
            if not id_line:  # 如果读到文件末尾
                break

            # 写入完整的 ID 行
            f_out.write(id_line + '\n')
            count += 1

            # 跳过下三行（序列、+号、质量分数）
            file.readline()  # 序列行
            file.readline()  # +号行
            file.readline()  # 质量分数行

            # 检查是否达到了指定的数量，如果是，则开启新的文件
            if count == reads_per_file:
                f_out.close()  # 关闭当前文件
                file_index += 1  # 更新文件索引
                output_txt_path = os.path.join(output_dir, f'ids_output_{file_index}.txt')
                f_out = open(output_txt_path, 'w')  # 开启新的文件
                count = 0  # 重置计数器

    # 关闭最后一个文件
    f_out.close()

    print(f"所有ID已经被分批写入到 {output_dir} 目录下的文件中")


# 示例文件路径（需要替换为实际路径）
fastq_path = "input/ERR3365952.fastq"
output_dir = "cache/ids_output"
reads_per_file = 300000  # 每个文件包含1000个reads的ID

# 调用函数，提取完整ID并分批写入到多个TXT文件中
extract_full_ids_to_txt(fastq_path, output_dir, reads_per_file)
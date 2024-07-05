import os
from Bio import SeqIO


def check_reads_length(fastq_file):
    """检查FASTQ文件中的reads长度，并返回长度信息"""
    lengths = set()
    for record in SeqIO.parse(fastq_file, "fastq"):
        lengths.add(len(record.seq))

    if len(lengths) == 1:
        return (True, next(iter(lengths)))  # 所有reads长度相等时返回该长度
    else:
        return (False, (min(lengths), max(lengths)))  # 返回最小和最大的read长度


def check_directory_for_fastq(dir_path):
    """检查指定目录下所有FASTQ文件的reads长度"""
    for filename in os.listdir(dir_path):
        if filename.endswith(".fastq"):
            file_path = os.path.join(dir_path, filename)
            is_equal_length, length_info = check_reads_length(file_path)
            if not is_equal_length:
                print(f"{filename}中的reads长度不相等: 最短长度为{length_info[0]}，最长长度为{length_info[1]}")
            else:
                print(f"{filename}中所有reads的长度相等，长度为{length_info}。")


# 替换为你的FASTQ文件所在的目录路径
directory_path = r"C:\Users\hbxnlsy\Desktop\FASTQ Samples"
check_directory_for_fastq(directory_path)
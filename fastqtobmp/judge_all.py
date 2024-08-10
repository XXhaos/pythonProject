def compare_fastq_files(file1_path, file2_path):
    from Bio import SeqIO

    # 初始化计数器和标志变量
    diff_count = 0
    files_are_identical = True
    file1_length = 0
    file2_length = 0
    diff_ids = []
    diff_bases = []
    diff_qualities = []

    # 使用 with open 结构并行读取两个 FASTQ 文件
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        parser1 = SeqIO.parse(file1, "fastq")
        parser2 = SeqIO.parse(file2, "fastq")

        for record1, record2 in zip(parser1, parser2):
            file1_length += 1
            file2_length += 1

            if record1.description != record2.description:
                diff_ids.append(file1_length * 4 - 3)
                files_are_identical = False
                diff_count += 1

            if record1.seq != record2.seq:
                diff_bases.append(file1_length * 4 - 2)
                files_are_identical = False
                diff_count += 1

            if record1.letter_annotations["phred_quality"] != record2.letter_annotations["phred_quality"]:
                diff_qualities.append(file1_length * 4)
                files_are_identical = False
                diff_count += 1

        # 检查两个文件是否有相同数量的记录
        try:
            next(parser1)
            files_are_identical = False
            file1_length += sum(1 for _ in parser1) + 1  # +1 for the one already read
        except StopIteration:
            pass

        try:
            next(parser2)
            files_are_identical = False
            file2_length += sum(1 for _ in parser2) + 1  # +1 for the one already read
        except StopIteration:
            pass

    # 检查文件长度是否相同
    if file1_length != file2_length:
        print(f"文件长度不同。文件1长度: {file1_length}, 文件2长度: {file2_length}，共找到 {diff_count} 处差异")
    elif files_are_identical:
        print("文件长度相同，且ID、序列和质量分数完全相同")
    else:
        print(f"文件长度相同，共找到 {diff_count} 处差异")

    return diff_ids, diff_bases, diff_qualities

# 示例文件路径（需要替换为实际路径）
file1_path = r"D:\pythonProject\fastqtobmp\input\SRR6819330.fastq" # 原始FASTQ文件路径
file2_path = r"D:\pythonProject\fastqtobmp\input\reconstructed.fastq"  # 恢复后的FASTQ文件路径

# 调用函数比较两个 FASTQ 文件
diff_ids, diff_bases, diff_qualities = compare_fastq_files(file1_path, file2_path)
print("有差异的ID行号: ", diff_ids)
print("有差异的碱基行号: ", diff_bases)
print("有差异的质量分数行号: ", diff_qualities)

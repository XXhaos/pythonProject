def compare_fastq_files(file1_path, file2_path):
    from Bio import SeqIO

    # 初始化计数器和标志变量
    diff_count = 0
    files_are_identical = True
    file1_length = 0
    file2_length = 0

    # 使用 with open 结构并行读取两个 FASTQ 文件
    with open(file1_path, 'r') as file1, open(file2_path, 'r') as file2:
        parser1 = SeqIO.parse(file1, "fastq")
        parser2 = SeqIO.parse(file2, "fastq")

        for record1, record2 in zip(parser1, parser2):
            file1_length += 1
            file2_length += 1

            # 比较 DNA 序列和质量分数
            # if record1.seq != record2.seq or record1.letter_annotations["phred_quality"] != record2.letter_annotations["phred_quality"]:
            #     print(f"差异在行 {file1_length}:")
            #     print(f"文件1: {record1.seq}, 质量: {record1.letter_annotations['phred_quality']}")
            #     print(f"文件2: {record2.seq}, 质量: {record2.letter_annotations['phred_quality']}\n")
            #     files_are_identical = False
            if record1.seq != record2.seq:
                print(f"差异在行 {file1_length * 4 - 2}:")
                print(f"文件1序列: {record1.seq}")
                print(f"文件2序列: {record2.seq}")
                files_are_identical = False
                diff_count += 1

            if record1.letter_annotations["phred_quality"] != record2.letter_annotations["phred_quality"]:
                print(f"差异在行 {file1_length * 4}:")
                print(f"文件1质量: {record1.letter_annotations['phred_quality']}")
                print(f"文件2质量: {record2.letter_annotations['phred_quality']}\n")
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
        print("文件长度相同，且序列和质量分数完全相同")
    else:
        print(f"文件长度相同，共找到 {diff_count} 处差异")

# 示例文件路径（需要替换为实际路径）
file1_path = "input/SRR554369.fastq" # 原始FASTQ文件路径
file2_path = "cache/change_to_fastq/restored_reads.fastq"  # 恢复后的FASTQ文件路径

# 调用函数比较两个 FASTQ 文件
compare_fastq_files(file1_path, file2_path)
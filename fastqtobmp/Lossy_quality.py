import os
import numpy as np
from Bio import SeqIO
from PIL import Image


def Q4(qsc):
    if qsc <= 7:
        return 5
    elif qsc <= 13:
        return 12
    elif qsc <= 19:
        return 18
    else:
        return 24


def ascii_to_quality(ascii_char):
    return ord(ascii_char) - 33


def process_quality_scores(quality_scores):
    # 将质量分数从ASCII码转换为整数，并映射到0-93的范围
    quality_scores = [ascii_to_quality(char) for char in quality_scores]
    # 使用Q4量化器对质量分数进行量化
    quantized_scores = [Q4(score) for score in quality_scores]
    return quantized_scores


def process_chunk(records, chunk_index, output_folder):
    quantized_scores_list = []

    for record in records:
        quality_scores = record.letter_annotations["phred_quality"]
        ascii_quality_scores = ''.join(chr(q + 33) for q in quality_scores)
        quantized_scores = process_quality_scores(ascii_quality_scores)
        quantized_scores_list.append(quantized_scores)

    # 将量化后的质量分数转换为NumPy数组并保存为TIFF图像
    quantized_array = np.array(quantized_scores_list, dtype=np.uint8)
    image = Image.fromarray(quantized_array)
    image.save(os.path.join(output_folder, f"chunk_{chunk_index}_quantized_quality_scores.tiff"))


def main():
    input_file = "D:\\pythonProject\\fastqtobmp\\input\\SRR554369.fastq"
    output_folder = "D:\\pythonProject\\fastqtobmp\\input\\compressed"
    chunk_size = 16 * 1024 * 1024  # 16 MB
    os.makedirs(output_folder, exist_ok=True)

    # 使用 SeqIO.parse() 预读取第一个 read 来确定 read 长度
    with open(input_file, 'r') as file:
        first_record = next(SeqIO.parse(file, "fastq"))
        read_length = len(first_record.seq)

    records_per_chunk = chunk_size // read_length
    chunk_index = 0
    records = []
    total_records = 0

    for record in SeqIO.parse(input_file, "fastq"):
        records.append(record)
        total_records += 1
        if total_records >= records_per_chunk:
            process_chunk(records, chunk_index, output_folder)
            chunk_index += 1
            records = []
            total_records = 0

    # 处理剩余部分
    if records:
        process_chunk(records, chunk_index, output_folder)

    print('质量分数处理完毕，结果已保存到', output_folder)


if __name__ == "__main__":
    main()

from Bio import SeqIO

def compare_quality_scores(original_fastq, recovered_fastq):
    original_records = SeqIO.parse(original_fastq, "fastq")
    recovered_records = SeqIO.parse(recovered_fastq, "fastq")

    for original_record, recovered_record in zip(original_records, recovered_records):
        if original_record.letter_annotations["phred_quality"] != recovered_record.letter_annotations["phred_quality"]:
            print(f"序列 {original_record.id} 的质量分数不匹配")
            return

    print("所有质量分数完全相同")

def main():
    original_fastq = "D:\\pythonProject\\fastqtobmp\\input\\SRR554369.fastq"
    recovered_fastq = "D:\\pythonProject\\fastqtobmp\\input\\recovered_quality.fastq"

    compare_quality_scores(original_fastq, recovered_fastq)

if __name__ == "__main__":
    main()
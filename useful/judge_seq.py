import os
from Bio import SeqIO

def compare_fastq_sequences(source_fastq, recovered_fastq):
    with open(source_fastq, "r") as source_file, open(recovered_fastq, "r") as recovered_file:
        source_sequences = SeqIO.parse(source_file, "fastq")
        recovered_sequences = SeqIO.parse(recovered_file, "fastq")

        for source_record, recovered_record in zip(source_sequences, recovered_sequences):
            if str(source_record.seq) != str(recovered_record.seq):
                print(f"Sequence mismatch found:\nSource: {source_record.seq}\nRecovered: {recovered_record.seq}")
                return False

    print("All sequences match.")
    return True

def main():
    source_fastq = "D:\\pythonProject\\fastqtobmp\\input\\SRR554369.fastq"
    recovered_fastq = "D:\\pythonProject\\fastqtobmp\\input\\output.fastq"

    result = compare_fastq_sequences(source_fastq, recovered_fastq)
    if result:
        print("所有序列完全一致。")
    else:
        print("存在不一致的序列。")

if __name__ == "__main__":
    main()

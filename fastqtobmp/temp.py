import os

# 输入文件路径
input_file = r"D:\pythonProject\fastqtobmp\input\SRR554369.fastq"
# 输出文件路径
output_file = input_file + ".compressed"

# lpaq8 可执行文件路径
lpaq8_exe = r"D:\pythonProject\lpaq8\lpaq8.exe"

# 压缩级别
compression_level = 9

# 调用 lpaq8 压缩
os.system(f"{lpaq8_exe} {compression_level} {input_file} {output_file}")

print(f"压缩完成: {output_file}")
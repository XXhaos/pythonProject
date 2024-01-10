from Bio import SeqIO
from PIL import Image

# 输入FASTQ文件路径
fastq_file = "SRR554369.fastq"

# 输出灰度图像路径
base_image_path = "base_image.tiff"
quality_image_path = "quality_image.tiff"

# 映射碱基为灰度值
base_mapping = {'A': 32, 'T': 64, 'G': 192, 'C': 224, 'N': 0}

# 初始化图像数据
base_image_data = []  # 用于存储碱基图像数据
quality_image_data = []  # 用于存储质量分数图像数据

# # 逐行读取FASTQ文件并将数据分为碱基和质量分数
# max_quality = 0  # 记录最大的质量分数

with open(fastq_file, "r") as handle:
    for record in SeqIO.parse(handle, "fastq"):
        base_sequence = record.seq  # 读取碱基序列
        quality_scores = record.letter_annotations["phred_quality"]  # ASCII码为33-126的字符映射为0-93
        # max_quality = max(max(quality_scores), max_quality)  # 更新最大的质量分数

        # 将碱基序列映射为灰度值并添加到图像数据中
        base_image_data.append([base_mapping.get(base, 0) for base in base_sequence])
        # 将质量分数添加到图像数据中
        quality_image_data.append(quality_scores)

# 计算图像高度，为碱基序列的长度
image_height = len(base_image_data[0])

# 创建碱基图像
base_image = Image.new('L', (len(base_image_data), image_height))  # 创建一个灰度图像
for i in range(len(base_image_data)):
    base_image.putpixel((i, 0), 0)  # 设置图像宽度

    for j in range(image_height):
        pixel_value = base_image_data[i][j]  # 获取像素值
        base_image.putpixel((i, j), pixel_value)  # 将像素值添加到图像中

# 创建质量分数图像
quality_image = Image.new('L', (len(quality_image_data), image_height))  # 创建一个灰度图像
for i in range(len(quality_image_data)):
    quality_image.putpixel((i, 0), 0)  # 设置图像宽度

    for j in range(image_height):
        pixel_value = quality_image_data[i][j] * 2  # 将质量分数乘以2作为像素值
        quality_image.putpixel((i, j), pixel_value)   # 将像素值添加到图像中

# 保存图像
base_image.save(base_image_path)
quality_image.save(quality_image_path)

print(f"Saved {len(base_image_data)} records to base image: {base_image_path}")
print(f"Saved {len(quality_image_data)} records to quality image: {quality_image_path}")
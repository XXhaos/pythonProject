import tifffile as tiff

# 以下函数用于将灰度值转换为碱基序列和质量分数
def gray_to_base(gray_values):
    base_to_gray = {'A': 32, 'T': 64, 'G': 192, 'C': 224, 'N': 0}
    gray_to_base = {v: k for k, v in base_to_gray.items()}
    return ''.join(gray_to_base.get(g, 'N') for g in gray_values)

# 以下函数用于将灰度值转换为质量分数
def gray_to_quality_string(quality_gray_values):
    approx_quality_scores = [q // 2 for q in quality_gray_values]
    quality_string = ''.join(chr(q + 33) for q in approx_quality_scores)
    return quality_string

# 以下函数用于获取指定read的碱基序列
def GetRowBase(i, read_count, image_height, output_path):
    if i < 1 or i > read_count:
        raise ValueError("指定的read位置超出范围。")

    block_number = (i - 1) // image_height + 1
    position_in_block = (i - 1) % image_height

    base_image_file = f"{output_path}_base_{block_number}.tiff"
    base_image_block = tiff.imread(base_image_file)
    base_gray_values = base_image_block[position_in_block, :]

    return gray_to_base(base_gray_values)

# 以下函数用于获取指定read的质量分数
def GetRowQuality(i, read_count, image_height, output_path):
    if i < 1 or i > read_count:
        raise ValueError("指定的read位置超出范围。")

    block_number = (i - 1) // image_height + 1
    position_in_block = (i - 1) % image_height

    quality_image_file = f"{output_path}_quality_{block_number}.tiff"
    quality_image_block = tiff.imread(quality_image_file)
    quality_gray_values = quality_image_block[position_in_block, :]

    return gray_to_quality_string(quality_gray_values)


# 以下函数用于返回第j个位置的所有碱基
def GetLineBase(j, total_blocks, output_path, read_length):
    """
    读取第j个位置的所有碱基，并按顺序返回一个碱基列表。该函数利用已有的gray_to_base函数来转换灰度值到碱基。

    :param j: 要读取的碱基位置（从1开始计数）。
    :param total_blocks: 图像块的总数。
    :param image_height: 每个图像块中read的数量。
    :param output_path: 存储图像文件的路径。
    :param read_length: 每个read的长度。
    :return: 按顺序包含所有图像块第j个位置碱基的列表。
    """
    # 确保j的值在有效范围内
    if j < 1 or j > read_length:
        raise ValueError("指定的位置超出了read的长度范围。")

    # 调整j以适应Python的0开始索引
    j -= 1

    base_list = []  # 初始化一个空列表来存储所有图像块的第j个位置的碱基

    for block_number in range(1, total_blocks + 1):
        # 构造当前图像块的文件路径
        base_image_file = f"{output_path}_base_{block_number}.tiff"

        # 读取图像文件
        base_image_block = tiff.imread(base_image_file)

        # 从每个图像块中提取第j个位置的碱基灰度值
        column_gray_values = base_image_block[:, j]

        # 使用已有的gray_to_base函数转换灰度值数组到碱基序列
        bases = gray_to_base(column_gray_values)

        # 将碱基序列添加到all_bases列表中
        base_list.extend(bases)

    return base_list

# 以下函数用于返回第j个位置的所有质量分数
def GetLineQuality(j, total_blocks, output_path, read_length):
    """
    读取第j个位置的所有质量分数，并按顺序返回一个质量分数列表。该函数利用已有的gray_to_quality_string函数来转换灰度值到质量分数。

    :param j: 要读取的质量分数位置（从1开始计数）。
    :param total_blocks: 图像块的总数。
    :param image_height: 每个图像块中read的数量。
    :param output_path: 存储图像文件的路径。
    :param read_length: 每个read的长度。
    :return: 按顺序包含所有图像块第j个位置质量分数的列表。
    """
    # 确保j的值在有效范围内
    if j < 1 or j > read_length:
        raise ValueError("指定的位置超出了read的长度范围。")

    # 调整j以适应Python的0开始索引
    j -= 1

    quality_list = []  # 初始化一个空列表来存储所有图像块的第j个位置的质量分数

    for block_number in range(1, total_blocks + 1):
        # 构造当前图像块的文件路径
        quality_image_file = f"{output_path}_quality_{block_number}.tiff"

        # 读取图像文件
        quality_image_block = tiff.imread(quality_image_file)

        # 从每个图像块中提取第j个位置的质量分数灰度值
        column_gray_values = quality_image_block[:, j]

        # 使用已有的gray_to_quality_string函数转换灰度值数组到质量分数序列
        quality_string = gray_to_quality_string(column_gray_values)

        # 将质量分数序列添加到quality_list列表中
        quality_list.extend(quality_string)

    return quality_list

# 以下函数用于读取第i条read第j个位置的碱基
def GetBase(i, j , read_count, image_height, output_path):
    """
    读取第i条read第j个位置的碱基。

    :param i: 要读取的read的位置（从1开始计数）。
    :param j: 要读取的碱基的位置（从1开始计数）。
    :param read_count: FASTQ文件中的read总数。
    :param image_height: 每个图像块中read的数量。
    :param output_path: 存储图像文件的路径。
    :return: 第i条read第j个位置的碱基。
    """
    RowBase = GetRowBase(i, read_count, image_height, output_path)
    return RowBase[j-1]

# 以下函数用于读取第i条read第j个位置的质量分数
def GetQuality(i, j , read_count, image_height, output_path):
    """
    读取第i条read第j个位置的质量分数。

    :param i: 要读取的read的位置（从1开始计数）。
    :param j: 要读取的质量分数的位置（从1开始计数）。
    :param read_count: FASTQ文件中的read总数。
    :param image_height: 每个图像块中read的数量。
    :param output_path: 存储图像文件的路径。
    :return: 第i条read第j个位置的质量分数。
    """
    RowQuality = GetRowQuality(i, read_count, image_height, output_path)
    return RowQuality[j-1]

# 使用示例
i = 1657870
j = 1
read_count = 1657871
read_length = 200
image_height = 655360
total_blocks = 3
output_path = "cache/change_to_gray/grayimage"

try:
    bases = GetRowBase(i, read_count, image_height, output_path)
    qualities = GetRowQuality(i, read_count, image_height, output_path)
    base_list = GetLineBase(j, total_blocks, output_path, read_length)
    quality_list = GetLineQuality(j, total_blocks, output_path, read_length)
    base = GetLineBase(i, j, read_count, image_height, output_path)
    quality = GetQuality(i, j , read_count, image_height, output_path)
    print("碱基序列:", bases)
    print("质量分数:", qualities)
    print(f"第{j}个位置的碱基列表:", base_list)
    print(f"第{j}个位置的质量分数列表:", quality_list)
    print(f"第{i}条read第{j}个位置的碱基:", base)
    print(f"第{i}条read第{j}个位置的质量分数:", quality)
except ValueError as e:
    print(e)

from PIL import Image
import numpy as np

def txt_to_gray_image(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    # 将每行转换为数值列表
    data = [list(map(int, line.strip().split())) for line in lines]
    # 转换为 NumPy 数组
    matrix = np.array(data)
    # 将数值转换为灰度值
    gray_matrix = matrix.astype(np.uint8)
    # 创建灰度图像
    image = Image.fromarray(gray_matrix, mode='L')
    return image

# 示例用法
image = txt_to_gray_image("input/G.txt")
image.save("input/G.tiff")
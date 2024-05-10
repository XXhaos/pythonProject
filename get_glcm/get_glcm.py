import numpy as np
from skimage import feature, io
from skimage.util import img_as_ubyte


def calc_glcm_feature(img, i, j, pad_width, feature_name, window_size=5):
    """
    计算给定位置(i, j)处的窗口的GLCM特征值。

    参数:
    - img: 边缘填充后的图像。
    - i, j: 当前像素的坐标。
    - pad_width: 图像边缘填充的宽度。
    - feature_name: 需要计算的特征名称（'homogeneity', 'contrast', 'energy', 'entropy'）。
    - window_size: 使用的窗口大小，必须是奇数。

    返回:
    - 计算得到的特征值，缩放并转换为uint8类型。
    """
    # 提取以(i, j)为中心的窗口
    window = img[i - pad_width:i + pad_width + 1, j - pad_width:j + pad_width + 1]
    # 计算GLCM
    glcm = feature.graycomatrix(window, [1], [0], 256, symmetric=True, normed=True)
    # 根据特征名称计算对应的特征值
    if feature_name == 'homogeneity':
        value = feature.graycoprops(glcm, 'homogeneity')[0, 0]
    elif feature_name == 'contrast':
        value = feature.graycoprops(glcm, 'contrast')[0, 0]
    elif feature_name == 'energy':
        value = feature.graycoprops(glcm, 'energy')[0, 0]
    elif feature_name == 'entropy':
        # 计算熵
        entropy = -np.sum(glcm * np.log2(glcm + np.finfo(float).eps))
        value = entropy / np.log2(256)  # 简化的缩放方法，可能需要根据实际数据调整
    # 归一化并缩放值到0-255范围内，转换为uint8类型
    return np.clip(value * 255, 0, 255).astype(np.uint8)


def calculate_features(image_path, window_size=5):
    """
    计算并返回图像的同质性、对比度、能量和熵特征矩阵。

    参数:
    - image_path: 图像文件的路径。
    - window_size: 使用的窗口大小，必须是奇数。

    返回:
    - 包含四个特征矩阵的字典。
    """
    # 读取图像，确保为8位灰度图
    img = io.imread(image_path)
    img = img_as_ubyte(img)
    # 计算边缘填充宽度
    pad_width = window_size // 2
    # 对图像进行边缘填充
    img_padded = np.pad(img, pad_width, mode='edge')

    # 初始化特征矩阵字典
    features = {
        'homogeneity': np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8),
        'contrast': np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8),
        'energy': np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8),
        'entropy': np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8),
    }

    # 遍历每个像素，计算特征
    for feature_name in features:
        for i in range(pad_width, img.shape[0] + pad_width):
            for j in range(pad_width, img.shape[1] + pad_width):
                features[feature_name][i - pad_width, j - pad_width] = calc_glcm_feature(
                    img_padded, i, j, pad_width, feature_name, window_size
                )

    return features


# 示例使用
image_path = '../fastqtobmp/cache/change_to_gray/grayimage_base_1.tiff'
features = calculate_features(image_path, window_size=5)

# 打印每个特征矩阵的形状和类型以验证
for feature_name, matrix in features.items():
    print(f"{feature_name} matrix shape: {matrix.shape}, dtype: {matrix.dtype}")
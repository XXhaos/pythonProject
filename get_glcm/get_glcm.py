import numpy as np
from numba import jit
import matplotlib.pyplot as plt
import cv2
from PIL import Image
from skimage import data
from math import floor, ceil
from skimage.feature import graycomatrix, graycoprops


# 主函数，目前为空
def main():
    pass


# 图像分块函数
def image_patch(img2, slide_window, h, w):
    """
    将图像分割成指定大小的块
    参数：
        img2: 输入图像
        slide_window: 滑动窗口大小
        h: 图像高度
        w: 图像宽度
    返回：
        patch: 分割后的图像块
    """
    image = img2
    window_size = slide_window
    # 初始化一个存储图像块的数组
    patch = np.zeros((slide_window, slide_window, h, w), dtype=np.uint8)

    # 遍历图像，提取每个图像块
    for i in range(patch.shape[2]):
        for j in range(patch.shape[3]):
            patch[:, :, i, j] = img2[i: i + slide_window, j: j + slide_window]

    return patch


# 计算灰度共生矩阵 (GLCM)

def calcu_glcm(img, vmin=0, vmax=255, nbit=64, slide_window=5, step=[2], angle=[0]):
    mi, ma = vmin, vmax
    h, w = img.shape

    # Compressed gray range：vmin: 0-->0, vmax: 256-1 -->nbit-1
    bins = np.linspace(mi, ma + 1, nbit + 1)
    img1 = np.digitize(img, bins) - 1

    # (512, 512) --> (slide_window, slide_window, 512, 512)
    img2 = cv2.copyMakeBorder(img1, floor(slide_window / 2), floor(slide_window / 2)
                              , floor(slide_window / 2), floor(slide_window / 2), cv2.BORDER_REPLICATE)  # 图像扩充，计算边缘像素值

    patch = np.zeros((slide_window, slide_window, h, w), dtype=np.uint8)
    patch = image_patch(img2, slide_window, h, w)

    # Calculate GLCM (5, 5, 512, 512) --> (64, 64, 512, 512)
    # greycomatrix(image, distances, angles, levels=None, symmetric=False, normed=False)
    glcm = np.zeros((nbit, nbit, len(step), len(angle), h, w), dtype=np.uint8)
    for i in range(patch.shape[2]):
        for j in range(patch.shape[3]):
            glcm[:, :, :, :, i, j] = graycomatrix(patch[:, :, i, j], step, angle, levels=nbit)

    return glcm


# 计算 GLCM 同质性
def calcu_glcm_homogeneity(glcm, nbit=64):
    '''
    计算 GLCM 同质性
    '''
    Homogeneity = np.zeros((glcm.shape[2], glcm.shape[3]), dtype=np.float32)
    for i in range(nbit):
        for j in range(nbit):
            Homogeneity += glcm[i, j] / (1. + (i - j) ** 2)

    return Homogeneity


# 计算 GLCM 对比度
def calcu_glcm_contrast(glcm, nbit=64):
    '''
    计算 GLCM 对比度
    '''
    contrast = np.zeros((glcm.shape[2], glcm.shape[3]), dtype=np.float32)
    for i in range(nbit):
        for j in range(nbit):
            contrast += glcm[i, j] * (i - j) ** 2

    return contrast


# 计算 GLCM 熵
def calcu_glcm_entropy(glcm, nbit=64):
    '''
    计算 GLCM 熵
    '''
    eps = 0.00001
    entropy = np.zeros((glcm.shape[2], glcm.shape[3]), dtype=np.float32)
    for i in range(nbit):
        for j in range(nbit):
            entropy -= glcm[i, j] * np.log10(glcm[i, j] + eps)

    return entropy


# 计算 GLCM 能量
def calcu_glcm_energy(glcm, nbit=64):
    '''
    计算 GLCM 能量或二阶矩
    '''
    energy = np.zeros((glcm.shape[2], glcm.shape[3]), dtype=np.float32)
    for i in range(nbit):
        for j in range(nbit):
            energy += glcm[i, j] ** 2

    return energy


# 程序入口
if __name__ == '__main__':
    main()
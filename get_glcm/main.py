import numpy as np
import cv2
from matplotlib import pyplot as plt
import get_glcm
import time
from PIL import Image
import os

def main():
    pass


if __name__ == '__main__':

    main()

    folder = 'feature_images'
    if not os.path.exists(folder):
        os.makedirs(folder)

    t = 0

    path = '../fastqtobmp/cache/change_to_gray/'
    file_count = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])

    print(file_count)

    for k in range(file_count):
        image = f'../fastqtobmp/cache/change_to_gray/Quality_{k}.tiff'

        start = time.time()
        print('glcm:',k)
        print('---------------.0. Parameter Setting-----------------')
        nbit = 64 # gray levels
        mi, ma = 0, 255 # max gray and min gray
        slide_window = 7 # sliding window
        # step = [2, 4, 8, 16] # step
        # angle = [0, np.pi/4, np.pi/2, np.pi*3/4] # angle or direction
        step = [2]
        angle = [0]
        print('-------------------1. Load Data---------------------')

        img = np.array(Image.open(image)) # If the image has multi-bands, it needs to be converted to grayscale image
        img = np.uint8(255.0 * (img - np.min(img))/(np.max(img) - np.min(img))) # normalization
        h, w = img.shape
        print('------------------2. Calcu GLCM---------------------')
        glcm = get_glcm.calcu_glcm(img, mi, ma, nbit, slide_window, step, angle)
        print('-----------------3. Calcu Feature-------------------')

        #
        for i in range(glcm.shape[2]):
            for j in range(glcm.shape[3]):
                glcm_cut = np.zeros((nbit, nbit, h, w), dtype=np.uint8)
                glcm_cut = glcm[:, :, i, j, :, :]
                homogeneity = get_glcm.calcu_glcm_homogeneity(glcm_cut, nbit)#同质性
                contrast = get_glcm.calcu_glcm_contrast(glcm_cut, nbit)#对比度
                entropy = get_glcm.calcu_glcm_entropy(glcm_cut, nbit)#熵值
                energy = get_glcm.calcu_glcm_energy(glcm_cut, nbit)#能量

        # homogeneity_images1 = np.array(np.uint8(homogeneity))
        # contrast_images1 = np.array(np.uint8(contrast))
        # entropy_images1 = np.array(np.uint8(entropy))
        # energy_images1 = np.array(np.uint8(energy))

        print('---------------4. Display and Result----------------')


        # Image.fromarray(homogeneity_image).save(f'{folder}/homogeneity_{i}.tiff')
        # Image.fromarray(contrast_image).save(f'{folder}/contrast_{i}.tiff')
        # Image.fromarray(entropy_image).save(f'{folder}/entropy_{i}.tiff')
        # Image.fromarray(energy_image).save(f'{folder}/energy_{i}.tiff')

        homogeneity_image = np.array(np.uint8(homogeneity))
        contrast_image = np.array(np.uint8(contrast))
        entropy_image = np.array(np.uint8(entropy))
        energy_image = np.array(np.uint8(energy))

        # print(k)
        Image.fromarray(homogeneity_image).save(f'{folder}/homogeneity_{k}.tiff')
        Image.fromarray(contrast_image).save(f'{folder}/contrast_{k}.tiff')
        Image.fromarray(entropy_image).save(f'{folder}/entropy_{k}.tiff')
        Image.fromarray(energy_image).save(f'{folder}/energy_{k}.tiff')
        # cv2.imwrite(r"homogeneity.tiff", homogeneity_images1)

        end = time.time()
        print('Code run time:', end - start)

        t = t + end

    print('total time:', t)
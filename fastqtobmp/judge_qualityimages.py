import os
import numpy as np
from PIL import Image

# 定义原始图像和还原图像的文件夹路径
original_folder = r'D:\pythonProject\fastqtobmp\output\front_compressed'
recovered_folder = r'D:\pythonProject\fastqtobmp\output\LLLLLL\front_compressed'

# 获取以 '.tiff' 结尾的文件列表，并按照文件名中的序号排序
original_files = sorted([f for f in os.listdir(original_folder) if f.endswith('.tiff')],
                        key=lambda x: int(x.split('_')[1]))
recovered_files = sorted([f for f in os.listdir(recovered_folder) if f.endswith('.tiff')],
                         key=lambda x: int(x.split('_')[1]))

# 对比每一对文件
all_same = True
diff_details = {}

for original_file, recovered_file in zip(original_files, recovered_files):
    # 加载图像文件
    original_img_path = os.path.join(original_folder, original_file)
    recovered_img_path = os.path.join(recovered_folder, recovered_file)

    original_img = Image.open(original_img_path)
    recovered_img = Image.open(recovered_img_path)

    # 将图像转换为NumPy数组
    original_array = np.array(original_img)
    recovered_array = np.array(recovered_img)

    # 比较两个数组是否相同
    if np.array_equal(original_array, recovered_array):
        print(f'{original_file} 和 {recovered_file} 完全相同')
    else:
        print(f'{original_file} 和 {recovered_file} 不相同')
        all_same = False

        # 输出不相同的行
        diff_rows = np.where((original_array != recovered_array).any(axis=1))[0].tolist()
        diff_details[f'{original_file} 和 {recovered_file}'] = diff_rows

if all_same:
    print("全部相同")
else:
    print("存在不同")
    print("具体不同的行如下：")
    for files, rows in diff_details.items():
        print(f"{files} 不同的行: {rows}")

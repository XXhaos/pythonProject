import os
import numpy as np
from skimage import io
from skimage.feature import local_binary_pattern
from sklearn.cluster import KMeans
import time
import subprocess
import tempfile

def calculate_lbp_and_compress(image_path, output_dir, num_clusters=2, lpaq8_path="D:\\pythonProject\\lpaq8\\lpaq8.exe", compression_level='9'):
    start_time = time.time()

    # 读取图像
    img = io.imread(image_path)

    # 计算LBP特征
    radius = 3
    n_points = 8 * radius
    lbp = local_binary_pattern(img, n_points, radius, method="uniform")

    # 使用K-means算法对LBP特征进行聚类
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    lbp_flat = lbp.ravel().reshape(-1, 1)
    kmeans.fit(lbp_flat)
    labels = kmeans.labels_.reshape(img.shape)

    # 处理分类数据
    for i in range(num_clusters):
        # 提取当前类的数据
        class_data = img[labels == i]

        if class_data.size < 2:
            print(f"分类 {i} 的数据长度小于2，无法进行差分编码。跳过压缩。")
            continue

        # 应用差分编码
        if class_data.ndim == 1:
            # 一维数组差分
            diff_data = np.diff(class_data, n=1)
            diff_data = np.insert(diff_data, 0, class_data[0])  # 在差分数组前插入原始数据的第一个元素
        else:
            # 二维数组差分
            diff_data = np.diff(class_data, axis=0)
            diff_data = np.vstack([class_data[0:1, :], diff_data])  # 将第一行数据保留，便于恢复原始数据

        # 保存差分数据并压缩
        with tempfile.NamedTemporaryFile(delete=False, mode='wb') as temp_file:
            temp_file.write(diff_data.tobytes())
            temp_file_name = temp_file.name

        # 定义压缩文件的完整路径，包括原始文件名和类标签
        compressed_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(image_path))[0]}_class_{i}.lpaq8")
        compress_data(temp_file_name, compressed_path, lpaq8_path, compression_level)
        os.remove(temp_file_name)  # 清理临时文件

    end_time = time.time()
    print(f"代码执行时间: {end_time - start_time} 秒")

def compress_data(input_path, output_path, lpaq8_path, compression_level):
    """使用lpaq8压缩数据。"""
    command = [lpaq8_path, compression_level, input_path, output_path]
    try:
        subprocess.run(command, check=True)
        print(f"文件 {input_path} 压缩成功，保存为 {output_path}")
    except subprocess.CalledProcessError as e:
        print("压缩过程中出错")
        print("错误输出:", e.stderr)
    except Exception as e:
        print(f"发生未知错误: {str(e)}")

# 示例用法
image_dir = 'cache/change_to_gray/'
output_dir = 'cache/cluster/'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

for filename in os.listdir(image_dir):
    if filename.endswith('.tiff') and "quality" in filename:
        image_path = os.path.join(image_dir, filename)
        calculate_lbp_and_compress(image_path, output_dir, num_clusters=2, lpaq8_path="D:\\pythonProject\\lpaq8\\lpaq8.exe", compression_level='9')

print("处理完成")
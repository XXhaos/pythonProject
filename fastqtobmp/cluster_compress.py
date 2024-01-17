import os
import glob
import numpy as np
import tifffile as tiff
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import subprocess
import time


def extract_features(image_path):
    # 读取图像并计算其统计特征
    image = tiff.imread(image_path)
    features = np.array([np.mean(image), np.std(image)])
    return features


def cluster_images(image_directory, n_clusters=3):
    # 获取目录下的所有 tiff 图像
    image_paths = glob.glob(f"{image_directory}/*.tiff")

    # 提取图像特征
    features = np.array([extract_features(path) for path in image_paths])

    # 标准化特征
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # 应用 K-means 聚类
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(features_scaled)

    # 对图像进行分组
    clustered_images = {}
    for label, path in zip(kmeans.labels_, image_paths):
        if label not in clustered_images:
            clustered_images[label] = []
        clustered_images[label].append(path)

    return clustered_images


def compress_grouped_images(clustered_images, output_directory):
    # 确保输出目录存在
    os.makedirs(output_directory, exist_ok=True)

    # 压缩每个分组的图像
    for group, paths in clustered_images.items():
        group_output_file = f"{output_directory}/group_{group}.xz"
        command = f"tar -cJvf {group_output_file} " + " ".join(paths)

        # 使用 subprocess 运行压缩命令
        try:
            subprocess.run(command, check=True, shell=True)
            print(f"分组 {group} 的图像已成功压缩为 {group_output_file}")
        except subprocess.CalledProcessError as e:
            print(f"压缩分组 {group} 的图像失败：", e)


# 开始时间
start_time = time.time()

# 示例用法
image_directory = "cache/change_to_gray"
output_directory = "cache/clustered_compress"
n_clusters = 5  # 可以根据需要调整聚类数量
clustered_images = cluster_images(image_directory, n_clusters)
compress_grouped_images(clustered_images, output_directory)

# 结束时间和执行时间
end_time = time.time()
execution_time = end_time - start_time
print(f"程序执行时间: {execution_time} 秒")
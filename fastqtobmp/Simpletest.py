from PIL import Image, ImageFile
import glob
import subprocess
import os

def compress_image(image_path, output_path):
    # 直接压缩整个图像
    temp_image_path = 'temp_image.png'
    with Image.open(image_path) as img:
        img.save(temp_image_path, format='PNG')

    # 设置JPEG XL输出文件路径
    output_jxl_path = f"{output_path}.jxl"
    # 使用JPEG XL命令行工具压缩图像
    subprocess.run(['cjxl', temp_image_path, output_jxl_path])

    # 删除临时PNG文件
    os.remove(temp_image_path)

def compress_images_in_directory(input_directory, output_directory):
    # 确保输出目录存在
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # 获取输入目录中的所有图像文件
    image_paths = glob.glob(os.path.join(input_directory, '*.png'))

    for image_path in image_paths:
        output_base_path = os.path.join(output_directory, os.path.basename(image_path).split('.')[0])
        compress_image(image_path, output_base_path)

# 调整Pillow库的解压缩炸弹检查阈值
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

# 示例用法
input_directory = 'cache/change_to_gray'
output_directory = 'cache/compressed_images'
compress_images_in_directory(input_directory, output_directory)
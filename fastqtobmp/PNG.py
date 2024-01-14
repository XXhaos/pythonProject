import os
import subprocess

def convert_to_png_imagemagick(directory):
    compressed_directory = os.path.join(directory, 'compressed')
    if not os.path.exists(compressed_directory):
        os.makedirs(compressed_directory)

    for filename in os.listdir(directory):
        if filename.endswith('.tiff'):
            file_path = os.path.join(directory, filename)
            compressed_file_path = os.path.join(compressed_directory, filename.replace('.tiff', '.png'))

            # 使用ImageMagick进行转换
            subprocess.run(['convert', file_path, compressed_file_path])
            print(f"Compressed and saved: {compressed_file_path}")

directory_path = 'cache/change_to_gray'
convert_to_png_imagemagick(directory_path)
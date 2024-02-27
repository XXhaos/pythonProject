import tifffile as tiff

# 假设图片文件名为'image_file.tiff'，请替换为实际的文件路径
image_file = 'cache/change_to_gray/grayimage_base_1.tiff'

# 使用tifffile读取图片
with tiff.TiffFile(image_file) as img:
    # 获取图片的宽度和高度
    width, height = img.pages[0].shape[1], img.pages[0].shape[0]

print(f"图片的像素大小为：宽度 {width} 像素，高度 {height} 像素。")
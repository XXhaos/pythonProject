from PIL import Image
import sys

def compare_grayscale_images(image_path1, image_path2):
    # 打开两张灰度图像
    img1 = Image.open(image_path1).convert('L')
    img2 = Image.open(image_path2).convert('L')

    # 检查图片尺寸是否相同
    if img1.size != img2.size:
        print("两张图片的尺寸不同，无法比较每个像素点。")
        return

    # 将图像数据转换为像素值列表
    pixels1 = list(img1.getdata())
    pixels2 = list(img2.getdata())

    total_pixels = len(pixels1)
    different_pixels = []

    # 逐个像素比较
    for i in range(total_pixels):
        if pixels1[i] != pixels2[i]:
            y, x = divmod(i, img1.width)
            different_pixels.append((x, y))

    total_different = len(different_pixels)

    if total_different == 0:
        print("两张图片的每个像素都相同。")
    else:
        print(f"两张图片有 {total_different} 个不同的像素点。")
        print("不同的像素点坐标列表：")
        print(different_pixels)

if __name__ == "__main__":
    # 您提供的两张图片的路径
    image_path1 = r"C:\Users\hbxnlsy\Desktop\front_compressed\chunk_1_quality.tiff"
    image_path2 = r"D:\pythonProject\fastqtobmp\output\front_compressed\chunk_1_quality.tiff"

    compare_grayscale_images(image_path1, image_path2)

import os
import subprocess
import shutil

# 定义根目录路径
root_input_folder = r"D:\pythonProject\fastqtobmp\cache\change_to_gray"
root_output_folder = r"D:\pythonProject\fastqtobmp\cache\jugde"

# 确保输出根目录存在
os.makedirs(root_output_folder, exist_ok=True)

def compress_in_subfolders(input_folder, output_root):
    """
    遍历所有子目录并压缩其中的图像文件。
    """
    for dirpath, dirnames, filenames in os.walk(input_folder):
        for dirname in dirnames:
            subfolder_path = os.path.join(dirpath, dirname)
            output_folder1 = os.path.join(output_root, f"{dirname}/output_folder1")
            output_folder2 = os.path.join(output_root, f"{dirname}/output_folder2")

            os.makedirs(output_folder1, exist_ok=True)
            os.makedirs(output_folder2, exist_ok=True)

            for filename in os.listdir(subfolder_path):
                if filename.endswith(".tiff") or filename.endswith(".png"):
                    filepath = os.path.join(subfolder_path, filename)

                    compressed_filepath_lpaq8 = os.path.join(output_folder1, f"{filename}.lpaq8")
                    lpaq8_command = [r"D:\pythonProject\lpaq8\lpaq8.exe", "9", filepath, compressed_filepath_lpaq8]
                    result_method1 = subprocess.run(lpaq8_command, capture_output=True)

                    compressed_filepath_zpaq = os.path.join(output_folder2, f"{filename}.zpaq")
                    zpaq_command = [r"D:\pythonProject\zpaq715\zpaq.exe", "add", compressed_filepath_zpaq, filepath, "-method", "4"]
                    result_method2 = subprocess.run(zpaq_command, capture_output=True)

                    # 获取压缩后文件的大小
                    compressed_size_method1 = os.path.getsize(compressed_filepath_lpaq8)
                    compressed_size_method2 = os.path.getsize(compressed_filepath_zpaq)
                    print(compressed_size_method1)
                    print(compressed_size_method2)

                    print(f"文件 {filename} 使用lpaq8压缩后相对于zpaq的大小比: {compressed_size_method1 / compressed_size_method2:.2%}")

                    if compressed_size_method1 < compressed_size_method2:
                        shutil.copy(filepath, os.path.join(output_folder1, filename))
                    else:
                        shutil.copy(filepath, os.path.join(output_folder2, filename))

# 调用函数处理根输入目录下的所有子目录
compress_in_subfolders(root_input_folder, root_output_folder)

print("压缩文件大小比较完成。")

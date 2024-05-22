# import os
# import subprocess
# import shutil
# import logging
#
# # 定义根目录路径
# root_input_folder = r"D:\pythonProject\fastqtobmp\cache\change_to_gray"
# root_output_folder = r"D:\pythonProject\fastqtobmp\cache\judge"
# archive_folder = os.path.join(root_input_folder, "archive")
#
# # 设置日志文件和日志级别
# logging.basicConfig(filename="compression_log.log", level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')
#
# def compress_in_subfolders(input_folder, output_root):
#     """
#     遍历所有子目录并压缩其中的图像文件，将处理完成的目录移动到归档目录，并将压缩文件保存到指定的输出文件夹。
#     """
#     for dirpath, dirnames, filenames in os.walk(input_folder):
#         # 在dirnames中排除 'archive' 文件夹
#         dirnames[:] = [d for d in dirnames if d != 'archive']
#
#         for dirname in dirnames:
#             subfolder_path = os.path.join(dirpath, dirname)
#             print(f"开始处理文件夹：{dirname}")
#
#             files_better_with_method1 = []
#             files_better_with_method2 = []
#
#             for filename in os.listdir(subfolder_path):
#                 if filename.endswith(".tiff"):
#                     filepath = os.path.join(subfolder_path, filename)
#
#                     compressed_filepath_lpaq8 = os.path.join(output_root, dirname, "lpaq8_compressed", f"{filename}.lpaq8")
#                     compressed_filepath_zpaq = os.path.join(output_root, dirname, "zpaq_compressed", f"{filename}.zpaq")
#
#                     os.makedirs(os.path.dirname(compressed_filepath_lpaq8), exist_ok=True)
#                     os.makedirs(os.path.dirname(compressed_filepath_zpaq), exist_ok=True)
#
#                     subprocess.run([r"D:\pythonProject\lpaq8\lpaq8.exe", "9", filepath, compressed_filepath_lpaq8], check=True)
#                     subprocess.run([r"D:\pythonProject\zpaq715\zpaq.exe", "add", compressed_filepath_zpaq, filepath, "-method", "4"], check=True)
#
#                     compressed_size_method1 = os.path.getsize(compressed_filepath_lpaq8)
#                     compressed_size_method2 = os.path.getsize(compressed_filepath_zpaq)
#
#                     if compressed_size_method1 < compressed_size_method2:
#                         files_better_with_method1.append(filename)
#                     else:
#                         files_better_with_method2.append(filename)
#
#             # 更新输出文件夹名称
#             original_folder_path = os.path.join(output_root, dirname)
#             output_folder_suffix = "(lpaq8)" if len(files_better_with_method1) > len(files_better_with_method2) else "(zpaq)"
#             updated_folder_path = original_folder_path + output_folder_suffix
#
#             if not os.path.exists(updated_folder_path):
#                 os.rename(original_folder_path, updated_folder_path)
#             else:
#                 logging.info(f"Target folder {updated_folder_path} already exists. Skipping renaming.")
#
#             # 移动处理完成的目录到归档
#             shutil.move(subfolder_path, os.path.join(archive_folder, dirname))
#             print(f"已完成并归档文件夹：{dirname}")
#
# # 调用函数处理根输入目录下的所有子目录
# compress_in_subfolders(root_input_folder, root_output_folder)


import os
import subprocess
import shutil

# 定义根目录路径
root_input_folder = r"D:\pythonProject\fastqtobmp\cache\change_to_gray"
root_output_folder = r"D:\pythonProject\fastqtobmp\cache\judge"

# 确保输出根目录存在
os.makedirs(root_output_folder, exist_ok=True)

def compress_in_subfolders(input_folder, output_root):
    """
    遍历所有子目录并压缩其中的图像文件。
    """
    for dirpath, dirnames, filenames in os.walk(input_folder):
        # 移除名为“archive”的文件夹
        if 'archive' in dirnames:
            dirnames.remove('archive')

        for dirname in dirnames:
            subfolder_path = os.path.join(dirpath, dirname)
            output_folder1 = os.path.join(output_root, f"{dirname}/lpaq8_compressed")
            output_folder2 = os.path.join(output_root, f"{dirname}/zpaq_compressed")

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
                    # print(compressed_size_method1)
                    # print(compressed_size_method2)
                    #
                    # print(f"文件 {filename} 使用lpaq8压缩后相对于zpaq的大小比: {compressed_size_method1 / compressed_size_method2:.2%}")

                    if compressed_size_method1 < compressed_size_method2:
                        shutil.copy(filepath, os.path.join(output_folder1, filename))
                    else:
                        shutil.copy(filepath, os.path.join(output_folder2, filename))

# 调用函数处理根输入目录下的所有子目录
compress_in_subfolders(root_input_folder, root_output_folder)

print("压缩文件大小比较完成。")
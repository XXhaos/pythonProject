import subprocess

# 定义输入和输出文件路径
input_image_path = "cache/change_to_gray/input_image.tiff"
output_image_path = "output_image.png"

# 构建命令列表
command = ["convert", input_image_path, output_image_path]

# 使用 subprocess 运行命令
subprocess.run(command)

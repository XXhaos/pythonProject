import brotli

def compress_file(input_file_path, output_file_path):
    # 读取文件内容
    with open(input_file_path, 'rb') as file:
        data = file.read()

    # 使用Brotli进行压缩，设置压缩级别为11（最高）
    compressed_data = brotli.compress(data, quality=11)

    # 保存压缩后的数据到新文件
    with open(output_file_path, 'wb') as compressed_file:
        compressed_file.write(compressed_data)

    print("压缩完成。压缩后文件大小:", len(compressed_data))

# 调用函数，压缩文件
input_path = 'input/G.txt'
output_path = 'input/G_compressed.br'
compress_file(input_path, output_path)
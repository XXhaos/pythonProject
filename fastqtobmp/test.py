import hashlib
import os
import sys

# 定义当前文件总长度
current_file_length = 300

# 定义预留空间的大小
reserved_space = 64

# 打开文件以读取和写入二进制数据
with open('your_file', 'w+b') as file:
    # 将文件指针移动到预留空间的位置
    file.seek(0)

    # 将当前文件总长度转换为字节形式
    total_length_bytes = current_file_length.to_bytes(reserved_space, byteorder='little')

    # 写入当前文件总长度到预留空间
    file.write(total_length_bytes)

# 读取写入的数据，验证是否正确写入
with open('your_file', 'rb') as file:
    file.seek(0)
    read_total_length = int.from_bytes(file.read(reserved_space), byteorder='little')


# print(f"文件总长度为：{read_total_length}")

def calculate_md5(file_path):
    # 创建一个 MD5 hash 对象
    md5_hash = hashlib.md5()

    # 以二进制模式打开文件
    with open(file_path, "rb") as file:
        # 逐块更新 MD5 hash
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)

    # 返回计算得到的 MD5 值的十六进制表示
    return md5_hash.hexdigest()


def test(destination1, destination2):
    if len(os.listdir(destination1)) == len(os.listdir(destination2)):
        print("文件数量校验成功")
    else:
        print("文件数量校验失败")

    for file1 in os.listdir(destination1):
        for file2 in os.listdir(destination2):
            if file1 == file2:
                print("文件名匹配，开始校验")
                md5_hash1 = calculate_md5(os.path.join(destination1, file1))
                md5_hash2 = calculate_md5(os.path.join(destination2, file2))
                if md5_hash1 == md5_hash2:
                    print(f"md5校验成功，当前检验的文件名：{file1}")
                else:
                    print(f"md5校验失败，当前检验的文件名：{file1}")
                    print("md5_hash1", md5_hash1)
                    print("md5_hash2", md5_hash2)


if __name__ == '__main__':
    # my_string = "Hello, 你好!"
    # my_bytes = my_string.encode('utf-8')
    # print("my_bytes", my_bytes)
    # my_string = my_bytes.decode('utf-8')
    # print("my_string", my_string)
    destination1 = os.path.join(os.getcwd(), "cache", "first_compressed")
    destination2 = os.path.join(os.getcwd(), "output", "first_compressed")

    test(destination1, destination2)

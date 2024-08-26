import hashlib
import os
import re
import sys
import time

from tqdm import tqdm

# 定义当前文件总长度
current_file_length = 300

# 定义预留空间的大小
reserved_space = 64

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

    all_success = True
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
                    all_success = False

    print(f"所有文件是否匹配成功:{all_success}")

def pattern_match():
    text = 'chunk_11_base_g_prime.lpaq8'
    pattern = re.compile(r"^chunk_(\d+)_base_g_prime.lpaq8$")

    # 在示例字符串中查找匹配
    matches = pattern.findall(text)

    # 输出匹配到的内容
    for match in matches:
        print("Found:", match)


if __name__ == '__main__':

    # destination1 = os.path.join(os.getcwd(), "output", "back_compressed")
    # destination2 = os.path.join(os.getcwd(), "output", "second_compressed")

    # destination1 = os.path.join(os.getcwd(), "cache", "new", "front_compressed")
    # destination2 = os.path.join(os.getcwd(), "output", "front_compressed")
    # test(destination1, destination2)
    with tqdm(total=100, file=sys.stdout, colour='red', bar_format='{l_bar}{bar}| {n:.3f}/{total_fmt} [{elapsed}<{remaining}, ' '{rate_fmt}{postfix}]') as pbar:
        for i in range(100):
            # 模拟任务执行
            # tqdm.write(str(i))
            time.sleep(0.01)
            pbar.update(0.6705)

        pbar.update(pbar.total - pbar.n)

    # destination1 = os.path.join(os.getcwd(), "output", "temp_input.lpaq8")
    # destination2 = os.path.join(os.getcwd(), "cache", "old", "second_compressed", "chunk_1_id_regex.lpaq8")
    # md5_hash1 = calculate_md5(destination1)
    # md5_hash2 = calculate_md5(destination2)
    # print(md5_hash1 == md5_hash2)

    # with open(os.path.join(os.getcwd(), "input", "SRR554369"), "ab+") as output_file:
    #     output_file.write(b"%eof%")


    # start = 0
    # end = 9467




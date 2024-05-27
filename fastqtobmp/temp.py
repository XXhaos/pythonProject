import os

# 定义两个文件夹的路径
folder1 = r"D:\pythonProject\fastqtobmp\input\Z"
folder2 = r"D:\pythonProject\fastqtobmp\input\decell2"

# 获取文件夹中的所有文件
files1 = sorted([f for f in os.listdir(folder1) if os.path.isfile(os.path.join(folder1, f))])
files2 = sorted([f for f in os.listdir(folder2) if os.path.isfile(os.path.join(folder2, f))])

all_same = True  # 标记所有文件是否相同

# 确保文件名是相对应的
if files1 != files2:
    print("两个文件夹中的文件名不匹配")
else:
    for file_name in files1:
        file_path1 = os.path.join(folder1, file_name)
        file_path2 = os.path.join(folder2, file_name)

        # 比较两个文件
        with open(file_path1, 'r') as file1, open(file_path2, 'r') as file2:
            content1 = file1.read()
            content2 = file2.read()

            if content1 == content2:
                print(f"{file_name} 完全相同")
            else:
                print(f"{file_name} 不相同")
                all_same = False

    if all_same:
        print("全部相同")
    else:
        print("存在不同")
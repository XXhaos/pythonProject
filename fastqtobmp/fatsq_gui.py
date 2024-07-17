import numpy as np
from collections import defaultdict
from itertools import product
from PIL import Image
from Bio import SeqIO
import time

import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import gzip
import lzma
import shutil
import tarfile

class FastQCompressorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("FastQ Compressor")
        self.root.geometry("600x400")

        self.fastq_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.lpaq8_exe_path = tk.StringVar(value="E:\\1\\compress\\Ipaq8.exe")  # 默认路径
        self.compression_method = tk.StringVar(value="lpaq8")

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # FastQ 文件选择
        ttk.Label(frame, text="选择 FastQ 文件:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(frame, textvariable=self.fastq_path, width=50).grid(row=0, column=1, padx=10, pady=10)
        ttk.Button(frame, text="浏览", command=self.browse_fastq_file).grid(row=0, column=2, padx=10, pady=10)

        # 输出文件夹选择
        ttk.Label(frame, text="选择输出文件夹:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(frame, textvariable=self.output_path, width=50).grid(row=1, column=1, padx=10, pady=10)
        ttk.Button(frame, text="浏览", command=self.browse_output_folder).grid(row=1, column=2, padx=10, pady=10)

        # lpaq8.exe 文件路径
        ttk.Label(frame, text="选择 lpaq8.exe 路径:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        ttk.Entry(frame, textvariable=self.lpaq8_exe_path, width=50).grid(row=2, column=1, padx=10, pady=10)
        ttk.Button(frame, text="浏览", command=self.browse_lpaq8_exe).grid(row=2, column=2, padx=10, pady=10)

        # 压缩方法选择
        ttk.Label(frame, text="选择压缩方法:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        ttk.Radiobutton(frame, text="LPAQ8", variable=self.compression_method, value="lpaq8").grid(row=3, column=1, padx=10, pady=10, sticky="w")
        ttk.Radiobutton(frame, text="LZMA", variable=self.compression_method, value="lzma").grid(row=3, column=2, padx=10, pady=10, sticky="w")
        ttk.Radiobutton(frame, text="GZIP", variable=self.compression_method, value="gzip").grid(row=3, column=3, padx=10, pady=10, sticky="w")

        # 处理按钮
        ttk.Button(frame, text="压缩文件", command=self.process_and_compress).grid(row=4, column=0, columnspan=4, padx=10, pady=10)

        # 显示压缩前后文件大小
        ttk.Label(frame, text="压缩前大小:").grid(row=5, column=0, padx=10, pady=10, sticky="e")
        self.before_size_label = ttk.Label(frame, text="0 B")
        self.before_size_label.grid(row=5, column=1, padx=10, pady=10, sticky="w")

        ttk.Label(frame, text="压缩后大小:").grid(row=6, column=0, padx=10, pady=10, sticky="e")
        self.after_size_label = ttk.Label(frame, text="0 B")
        self.after_size_label.grid(row=6, column=1, padx=10, pady=10, sticky="w")

    def browse_fastq_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("FastQ Files", "*.fastq"), ("All Files", "*.*")])
        if file_path:
            self.fastq_path.set(file_path)

    def browse_output_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.output_path.set(folder_path)

    def browse_lpaq8_exe(self):
        lpaq8_exe_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")])
        if lpaq8_exe_path:
            self.lpaq8_exe_path.set(lpaq8_exe_path)

    def process_and_compress(self):
        fastq_file = self.fastq_path.get()
        output_folder = self.output_path.get()
        lpaq8_exe = self.lpaq8_exe_path.get()
        compression_method = self.compression_method.get()

        if not fastq_file:
            messagebox.showerror("错误", "请选择一个 FastQ 文件")
            return

        if not output_folder:
            messagebox.showerror("错误", "请选择一个输出文件夹")
            return

        if compression_method == "lpaq8" and not os.path.exists(lpaq8_exe):
            messagebox.showerror("错误", f"找不到 lpaq8.exe 文件，请检查路径: {lpaq8_exe}")
            return

        self.process_fastq(fastq_file, output_folder)

        if compression_method == "lpaq8":
            output_file = self.compress_with_lpaq8(output_folder, lpaq8_exe)
        elif compression_method == "lzma":
            output_file = self.compress_with_lzma(output_folder)
        elif compression_method == "gzip":
            output_file = self.compress_with_gzip(output_folder)

        self.update_sizes(output_file)
        messagebox.showinfo("完成", f"文件已成功压缩为 {output_file}")

    def process_fastq(self, fastq_file, output_folder):
        # 调用你的 fastq_to_g_prime 函数来处理 fastq 文件
        # fastq_to_g_prime(fastq_file, output_folder)
        pass

    def compress_with_lpaq8(self, output_folder, lpaq8_exe):
        tar_path = os.path.join(output_folder, "output.tar")
        with tarfile.open(tar_path, "w") as tar:
            for tiff_file in os.listdir(output_folder):
                if tiff_file.endswith(".tiff"):
                    tiff_file_path = os.path.join(output_folder, tiff_file)
                    tar.add(tiff_file_path, arcname=tiff_file)
        compressed_file = tar_path + ".lpaq8"
        subprocess.run([lpaq8_exe, tar_path, compressed_file])
        return compressed_file

    def compress_with_lzma(self, output_folder):
        tar_path = os.path.join(output_folder, "output.tar.xz")
        with tarfile.open(tar_path, "w:xz") as tar:
            for tiff_file in os.listdir(output_folder):
                if tiff_file.endswith(".tiff"):
                    tiff_file_path = os.path.join(output_folder, tiff_file)
                    tar.add(tiff_file_path, arcname=tiff_file)
        return tar_path

    def compress_with_gzip(self, output_folder):
        tar_path = os.path.join(output_folder, "output.tar.gz")
        with tarfile.open(tar_path, "w:gz") as tar:
            for tiff_file in os.listdir(output_folder):
                if tiff_file.endswith(".tiff"):
                    tiff_file_path = os.path.join(output_folder, tiff_file)
                    tar.add(tiff_file_path, arcname=tiff_file)
        return tar_path

    def update_sizes(self, output_file):
        input_folder = self.output_path.get()
        total_input_size = sum(os.path.getsize(os.path.join(input_folder, f)) for f in os.listdir(input_folder) if f.endswith(".tiff"))
        self.before_size_label.config(text=self.get_file_size(total_input_size))

        if os.path.exists(output_file):
            self.after_size_label.config(text=self.get_file_size(os.path.getsize(output_file)))

    def get_file_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0

if __name__ == "__main__":
    root = tk.Tk()
    app = FastQCompressorGUI(root)
    root.mainloop()


    def fastq_to_g_prime(self, fastq_path, output_path, block_size=256 * 1024 * 1024):
        """
        将 FASTQ 文件分批读取并转换为预测后的 g_prime 矩阵，每批的大小接近给定的 block_size。

        参数：
        fastq_path：FASTQ 文件的路径。
        output_path：输出路径。
        block_size：每个图像块的目标大小（以字节为单位），默认为 256MB。
        """
        start_time = time.time()

        # 创建输出目录
        os.makedirs(output_path, exist_ok=True)

        # 定义碱基到灰度值的映射
        base_to_gray = {'A': 32, 'T': 64, 'G': 192, 'C': 224, 'N': 0}

        # 使用 SeqIO.parse() 预读取第一个 read 来确定 read 长度
        with open(fastq_path, 'r') as file:
            first_record = next(SeqIO.parse(file, "fastq"))
            read_length = len(first_record.seq)

        # 计算每个read所需的字节数（DNA序列和质量分数各占一半）
        bytes_per_read = read_length * 2

        # 根据block_size和bytes_per_read计算每个图像块应包含的reads数目
        reads_per_block = block_size // bytes_per_read

        read_count = 0
        block_count = 0
        base_image_block = []
        quality_image_block = []

        # 定义可能的元素列表
        elements = [0, 32, 64, 192, 224]
        # 定义规则表
        rule_table = []

        # 添加所有可能的规则到规则库
        values = [0, 32, 64, 192, 224]
        combinations = list(product(values, repeat=4))

        for combination in combinations:
            rule_table.append(combination)

        # 初始化规则字典，记录规则的使用次数
        rules_dict = defaultdict(int)

        # 使用 SeqIO.parse() 函数逐条读取 FASTQ 文件
        with open(fastq_path, 'r') as file:
            for record in SeqIO.parse(file, "fastq"):
                base_gray_values = [base_to_gray.get(base, 0) for base in record.seq]
                base_image_block.append(base_gray_values)

                quality_gray_values = [min(q * 2, 255) for q in record.letter_annotations["phred_quality"]]
                quality_image_block.append(quality_gray_values)

                read_count += 1

                # 当达到指定的 reads_per_block 时，处理图像块
                if len(base_image_block) == reads_per_block:
                    block_count += 1
                    self.process_block(np.array(base_image_block, dtype=np.uint8), output_path, block_count, rules_dict)
                    self.save_quality_image(np.array(quality_image_block, dtype=np.uint8), output_path, block_count)
                    print(f"图像块 {block_count} 已处理。")

                    base_image_block = []
                    quality_image_block = []

        # 处理最后一个图像块（如果有剩余）
        if base_image_block:
            block_count += 1
            self.process_block(np.array(base_image_block, dtype=np.uint8), output_path, block_count, rules_dict)
            self.save_quality_image(np.array(quality_image_block, dtype=np.uint8), output_path, block_count)
            print(f"最后的图像块 {block_count} 已处理。")

        end_time = time.time()
        print(f"代码执行时间: {end_time - start_time} 秒")

        return read_count, reads_per_block, block_count

    def process_block(self, G, output_path, block_count, rules_dict):
        # 初始化G_prime为与G相同大小的零矩阵
        G_prime = np.zeros_like(G)

        # 按照规则表进行预测并生成G_prime矩阵
        for i in range(0, G.shape[0]):
            for j in range(0, G.shape[1]):
                center = G[i, j]
                if i == 0:
                    up = 0
                else:
                    up = G[i - 1, j]
                if j == 0:
                    left = 0
                else:
                    left = G[i, j - 1]
                if i != 0 and j != 0:
                    left_up = G[i - 1, j - 1]
                else:
                    left_up = 0
                matched_rule = (up, left_up, left, center)
                matched_rule1 = (up, left_up, left, 32)
                matched_rule2 = (up, left_up, left, 224)
                matched_rule3 = (up, left_up, left, 192)
                matched_rule4 = (up, left_up, left, 64)
                matched_rule5 = (up, left_up, left, 0)

                matched_rules = [matched_rule1, matched_rule2, matched_rule3, matched_rule4, matched_rule5]
                max_freq = -1
                top_rule = None

                for rule in matched_rules:
                    freq = rules_dict[rule]
                    if freq > max_freq:
                        max_freq = freq
                        top_rule = rule

                # 如果规则中心与当前元素相同，则将G_prime[i, j]赋值为1，否则赋值为当前元素
                G_prime[i, j] = 1 if top_rule[3] == center else center
                # 更新规则字典中该规则的频率
                rules_dict[matched_rule] += 1

        # 构建输出文件路径
        output_name = f"chunk_{block_count}_base"
        g_prime_file_path = os.path.join(output_path, f'{output_name}_g_prime.tiff')

        # 将G_prime矩阵转换为图像并保存为TIFF文件
        g_prime_img = Image.fromarray(G_prime)
        g_prime_img.save(g_prime_file_path)

        print(f"G_prime图像块 {block_count} 已保存。")

    def save_quality_image(self, Q, output_path, block_count):
        output_name = f"chunk_{block_count}_quality"
        quality_file_path = os.path.join(output_path, f'{output_name}_quality.tiff')
        quality_img = Image.fromarray(Q)
        quality_img.save(quality_file_path)

        print(f"质量分数图像块 {block_count} 已保存。")

    def compress_with_lpaq8(self, output_path):
        for root, _, files in os.walk(output_path):
            for file in files:
                if file.endswith(".tiff"):
                    tiff_file = os.path.join(root, file)
                    compressed_file = tiff_file + ".lpaq8"
                    lpaq8_exe = "E:\\1\\compress\\Ipaq8.exe"
                    subprocess.run([lpaq8_exe, tiff_file, compressed_file])
                    print(f"{tiff_file} 已压缩为 {compressed_file}")



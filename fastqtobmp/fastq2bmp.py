import argparse
import os

from Lossy import main as lossy
from LossLess import main as lossLess

if __name__ == '__main__':
    lpaq8_path = f"{os.getcwd()}\lpaq8.exe"

    # 命令行解析
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='fastq compress')

    # 添加参数
    parser.add_argument('--compressor', type=str, default='Lossy', help='Lossy or LossLess?')
    parser.add_argument('--save', type=str, default='False', help='save (default: False)')
    parser.add_argument('--input_path', type=str, required=True, help='input_path')
    parser.add_argument('--output_path', type=str, required=True, help='output_path')
    parser.add_argument('--mode', type=str, required=True, help='mode')
    parser.add_argument('--save', type=str, default='False', help='save (default: False)')

    # 解析参数
    args = parser.parse_args()

    # 执行主函数
    if args.compressor == 'Lossy' or args.compressor == 'lossy':
        lossy(args.mode, args.input_path, args.output_path, lpaq8_path, args.save, None)

    elif args.compressor == 'LossLess' or args.compressor == 'lossLess':
        lossLess(args.mode, args.input_path, args.output_path, lpaq8_path, args.save, None)

    else:
        print("错误：没有指定正确的压缩器")
        exit(1)
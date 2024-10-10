import os
import time
from tkinter import filedialog, Tk

import gradio as gr

from LossLess import main

lpaq8_path = f"{os.getcwd()}\lpaq8.exe"


def compress(input_path, output_path, mode, save, progress=gr.Progress()):
    if input_path is None:
        return "输入路径必填"
    if output_path is None:
        return "输出路径必填"
    if mode is None:
        return "模式必填"
    if save is None:
        return "save必填"

    if mode == '压缩':
        _mode = "compress"
    elif mode == '解压':
        _mode = "decompress"
    else:
        return "mode不符合规则"

    if save == '保存':
        _save = True
    elif save == '不保存':
        _save = False
    else:
        return "save不符合规则"

    output = main(_mode, input_path, output_path, lpaq8_path, _save, progress)
    return output


def clear(input_file, output_file):
    pass

def browse_file():
    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    filename = filedialog.askopenfilename()
    if filename:
        if os.path.isfile(filename):
            root.destroy()
            return str(filename)
        else:
            filename = "Files not seleceted"
            root.destroy()
            return str(filename)


def browse_folder():
    root = Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    filename = filedialog.askdirectory()
    if filename:
        if os.path.isdir(filename):
            root.destroy()
            return str(filename)
        else:
            root.destroy()
            return str(filename)
    else:
        filename = "Folder not seleceted"
        root.destroy()
        return str(filename)


with gr.Blocks() as demo:
    with gr.Row():
        gr.HTML("""
                <div style="text-align: center; max-width: 1200px; margin: 20px auto;">
                <h1 style="font-weight: 900; font-size: 3rem; margin: 0rem">
                    fastq压缩器
                </h1>
                </dir>
                """)
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Row():
                input_file = gr.Textbox(label="输入路径", scale=5, interactive=False)
                image_browse_btn = gr.Button("Browse", min_width=1)
                image_browse_btn.click(fn=browse_file, outputs=input_file, show_progress="hidden")
            with gr.Row():
                output_file = gr.Textbox(label="输出路径", scale=5, interactive=False)
                image_browse_btn = gr.Button("Browse", min_width=1)
                image_browse_btn.click(fn=browse_folder, outputs=output_file, show_progress="hidden")

            mode = gr.Radio(["压缩", "解压"], label="模式")
            save = gr.Radio(["保存", "不保存"], label="是否保存中间文件")
        with gr.Column(scale=1):
            text = gr.TextArea()
    with gr.Row():
        clear_btn = gr.Button("clear")
        clear_btn.click(fn=clear, inputs=[input_file, output_file])
        compress_btn = gr.Button("Run compress")
        compress_btn.click(fn=compress, inputs=[input_file, output_file, mode, save], outputs=[text])
    demo.launch()
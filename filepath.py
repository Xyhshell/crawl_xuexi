
import tkinter as tk
from tkinter import filedialog
from webbrowser import open


def openpath():
    root = tk.Tk()
    root.withdraw()
    print('> 选择保存文件夹！')
    folf_path = filedialog.askdirectory()  # 获取文件夹
    # file_path = filedialog.askopenfilename()  # 获取文件
    if folf_path != '':
        open('https://www.xuexi.cn/xxqg.html?id=17d65f9df71b49e19d07bd10e0c91faf')
        print(folf_path + '/')
        return folf_path
    else:
        print('> 未获取文件夹，程序退出中...')
        exit()


if __name__ == '__main__':
    print(openpath())

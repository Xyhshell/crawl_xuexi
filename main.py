# -*- coding: utf-8 -*-

import json
import os
import sys
import re
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing

import requests
import DownloadProgress
import user_agent
import filepath

# from webbrowser import open

s = requests.Session()


def get_video_links(url):
    video = s.get(url=url).content.decode("utf8")
    pattern = r'https://video.xuexi.cn/[^,"]*mp4'
    link = re.findall(pattern, video, re.I)
    link.reverse()
    return link


def downloadVideo(url, file_name):
    '''
    下载视频
    :param url: 下载url路径
    :return: 文件
     '''
    headers = {
        "Sec-Fetch-Dest": "video",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "Referer": "https://www.xuexi.cn/"
    }
    with closing(s.get(url=url, stream=True, headers=headers)) as response:
        chunk_size = 1024
        content_size = int(response.headers['content-length'])
        file_D = this_path + file_name + '.mp4'
        # file_D = './Video/' + file_name + '.mp4'
        if (os.path.exists(file_D) and os.path.getsize(file_D) == content_size):
            print('跳过' + file_name)
        else:
            progress = DownloadProgress.DownloadProgress(file_name, total=content_size, unit="KB",
                                                         chunk_size=chunk_size,
                                                         run_status="正在下载", fin_status="下载完成")
            with open(file_D, "wb") as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    progress.refresh(count=len(data))


def crawl(url):
    pool = ThreadPoolExecutor(max_workers=10)  # 创建一个最大可容纳10个task的线程池
    if (url.startswith("https://www.xuexi.cn/lgpage/detail/index.html")):
        lessonList = getLessonListByLgPage(url)
        mlData = json.loads(lessonList)
        for i in range(len(mlData["sub_items"])):
            frst_name = mlData["sub_items"][i]["title"].replace(" ", "")
            for j in range(len(mlData["sub_items"][i]["videos"][0]["video_storage_info"])):
                res = mlData["sub_items"][i]["videos"][0]["video_storage_info"][j]["normal"]
                if ".mp4" in res:
                    break
            pool.submit(downloadVideo, res, frst_name)
    else:
        lessonList = getLessonList(url)
        mlData = json.loads(lessonList)
        print("已配置10个线程下载")
        for i in range((len(mlData["fpe1ki18v228w00"]))):
            frst_name = mlData["fpe1ki18v228w00"][i]["frst_name"].replace(
                '\t', ' ')
            static_page_url = mlData["fpe1ki18v228w00"][i]["static_page_url"]
            # 打开 mp4 视频网页链接
            resData = s.get(static_page_url).content.decode("utf8")
            preUrl = static_page_url.split("/")[3]
            pattern = r'src="./data(.*?)"></script>'
            url = "https://www.xuexi.cn/" + preUrl + \
                "/data" + re.findall(pattern, resData, re.I)[0]
            res = get_video_links(url)[0]
            print("已解析第 %s 个视频的下载地址：%s" % (i, res))
            pool.submit(downloadVideo, res, frst_name)  # 往线程池里面加入一个task


def getLessonListByLgPage(url):
    '''
    针对新格式 url 解析视频
    '''
    newUrl = r"https://boot-source.xuexi.cn/data/app/" + url[49:] + ".js"
    resData = s.get(url=newUrl).content.decode("utf8")
    print("已解析视频列表数据...")
    return resData[9:-1]

def getLessonList(url):
    resData = s.get(url=url).content.decode("utf8")
    print("已解析视频列表数据...")
    pattern = r'src="./data(.*?)"></script>'
    preUrl = url.split("/")[3]
    jsonUrl = "https://www.xuexi.cn/" + preUrl + \
        "/data" + re.findall(pattern, resData, re.I)[0]
    resData2 = s.get(url=jsonUrl).content.decode("utf8")
    print("已请求视频列表数据...")
    return resData2[14:-1]


if __name__ == '__main__':
    print(" | " + '-'*56)
    print(" |  1.程序正常情况不会闪退，理论无Bug")
    print(" |  2.程序可多开，每个程序工作时附带10个线程，请依主机性能使用")
    print(" |  4.程序二改于：https://github.com/jianboy/crawl_xuexi -*侵删*-")
    print(" |  3.程序仅供测试，请合理化使用，请勿用于灰产")
    print(" |  5.学习强国，YYDS!")
    print(" | " + '-'*56 + '\n')

    start_time = time.time()
    this_path = filepath.openpath() + '/'

    if len(sys.argv) == 2:
        url = sys.argv[1]
    else:
        url = input(
            "> 推荐输入“学习慕课”界面下的视频链接：\n\r（eg：https://www.xuexi.cn/9f584b49d8a7386a4cf248ce16f5e667/9b0f04ec6509904be734f5f609a3604a.html）\n\r> :")
    crawl(url)
    print("last time: {} s".format(time.time() - start_time))
    print("\n\r> 全部视频下载完成，回车退出！")
    input('')

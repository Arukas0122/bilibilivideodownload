import json
import re
import subprocess
import time
import requests

headers = {'cookie': 'SESSDATA=#这里填自己的',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER',
           "Referer": "https://www.bilibili.com/"}


def send_request(url):
    # 请求数据
    response = requests.get(url=url, headers=headers)
    return response


def get_video_data(html_data, vn1):
    # 解析视频数据
    # 提取视频标题
    print("开始解析视频...")
    title = re.findall('<h1 title="(.*?)" class="video-title">', html_data)[0]
    sets = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in title:
        if char in sets:
            title = title.replace(char, '')
    a = ''.join(title.split())
    b = f'{a}p{vn1}'
    print("解析成功，视频标题为：", b)
    # 提取视频对应的json数据
    json_data = re.findall('<script>window\.__playinfo__=(.*?)</script>', html_data)[0]
    json_data = json.loads(json_data)
    # pprint.pprint(json_data)
    # 提取音频URL地址
    audio_url = json_data['data']['dash']['audio'][0]['backupUrl'][0]
    # print('解析到的音频地址：', audio_url)
    # 提取视频URL地址
    video_url = json_data['data']['dash']['video'][0]['backupUrl'][0]
    # print('解析到的音频地址：', video_url)
    video_data = [b, audio_url, video_url]
    return video_data


def save_data(file_name, audio_url, video_url, bv):
    # 请求数据
    print('正在请求音频数据')
    audio_data = send_request(audio_url).content
    print('正在请求视频数据')
    video_url = send_request(video_url).content
    with open((bv) + file_name + '.mp3', mode='wb')as f:
        f.write(audio_data)
        print('正在保存音频数据')
    with open((bv) + file_name + '.mp4', mode='wb')as f:
        f.write(video_url)
        print('正在保存视频数据')


def merge_data(video_name, bv):
    # 数据的合并
    print('音频与视频合并开始：', video_name)
    COMMAND = f'ffmpeg -i {bv}{video_name}.mp4 -i {bv}{video_name}.mp3 -vcodec copy -acodec copy ({bv}){video_name}.mkv'
    p = subprocess.Popen(COMMAND, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print('视频合并结束：', video_name)


def uid_download():
    uid = input("输入用户的uid：")
    yema = int(input("输入视频总页数："))
    for j in range(1, yema + 1):
        html = 'https://api.bilibili.com/x/space/arc/search?mid=%s&ps=30&tid=0&pn=%s&keyword=&order=pubdate&jsonp=jsonp' % (
            uid, j)
        html_data = send_request(html).text
        for i in range(0, 30):
            bv_data = json.loads(html_data)
            bv = bv_data['data']['list']['vlist'][i]['bvid']
            video_html = 'https://www.bilibili.com/video/%s' % (bv)
            video_html_data = send_request(video_html).text
            p = re.findall('<span class="cur-page">(.*?)</span>', video_html_data)
            if p != []:
                pv = p[0]
                vn = int(pv.split('/')[1].split(')')[0])
                print('该BV号共有%s个视频' % (vn))
            else:
                print("该BV号只有一个视频")
                vn = 1
            for vn1 in range(1, vn + 1):
                video_html = 'https://www.bilibili.com/video/%s?p=%s' % (bv, vn1)
                print(video_html)
                video_html_data = send_request(video_html).text
                video_data = get_video_data(video_html_data, vn1)
                save_data(video_data[0], video_data[1], video_data[2], bv)
                merge_data(video_data[0], bv)
    time.sleep(1)


def bv_download():
    bvnumber = input("输入BV号：")
    video_html = 'https://www.bilibili.com/video/%s' % (bvnumber)
    video_html_data = send_request(video_html).text
    p = re.findall('<span class="cur-page">(.*?)</span>', video_html_data)
    if p != []:
        pv = p[0]
        vn = int(pv.split('/')[1].split(')')[0])
        print('共有%s个视频' % (vn))
    else:
        print("该BV号只有一个视频")
        vn = 1
    for vn1 in range(1, vn + 1):
        video_html = 'https://www.bilibili.com/video/%s?p=%s' % (bvnumber, vn1)
        print(video_html)
        video_html_data = send_request(video_html).text
        video_data = get_video_data(video_html_data, vn1)
        ps = 'p%s' % (vn1)
        save_data(video_data[0], video_data[1], video_data[2], bvnumber)
        merge_data(video_data[0], bvnumber)
        time.sleep(1)


def showInfo():
    print("-" * 30)
    print("    B站视频下载  alpha v1.22 ")
    print(" 1.根据用户UID与视频页数下载")
    print(" 2.根据BV号下载")
    print(" 3.退出系统")
    print(" 122更新日志\n"
          "修复多P下载\n"
          "代码优化\n"
          "下载速度优化\n"
          "更改最终合成视频格式为mp4文件\n"
          "移除了him\n")
    print('-' * 30)


while True:
    showInfo()
    key = int(input("输入所需的功能："))
    if key == 1:
        uid_download()
    elif key == 2:
        bv_download()
    elif key == 3:
        break
    else:
        print("输入有误！请重新输入。")

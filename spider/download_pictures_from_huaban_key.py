# 批量下载花瓣网图片
# 使用方法：
# 1. 安装python
# 2. 安装依赖包BeautifulSoup/json等，（终端输入：pip install xxxx，再按回车）
# 3. 运行文件 python download_pictures_from_huaban_key.py
# 4. 按命令对话指引，先输入下载图片的关键字，多个关键字用“+”连接，再输入各关键字和分类需要下载的图片张数

import sys
from bs4 import BeautifulSoup
import requests
import os
import uuid
import threading
import re
import json


def startRequest(url):
    print("【提示】正在抓取 - %s " % url)

    res = requests.get(url)
    
    if res.status_code == 200:
        
        res_html = res.content.decode()

        settings_pattern = re.compile(r'.*app\["settings"\]\s?=\s?([^\n]+).*', re.S|re.M)
        
        settings = returnJsonFromStr(res_html, settings_pattern)

        categories = settings['categories']

        if categories is None:
                return
        else:
            for item in categories:
                startCategoryRequest(item, url)
    else:
        print("【文档获取失败】【状态为%s】 - %s，" % (url, res.status_code))

def startCategoryRequest(item, url):
    category_url = url + '&category=' +item['id']
    category = nameEncode(item['name'])
    
    print("【提示】正在抓取 - %s " % url)
    res = requests.get(category_url)
    
    if res.status_code == 200:
        
        res_html = res.content.decode()
        
        page_pattern = re.compile(r'.*app\.page\["query"\]\s?=\s?([^\n]+).*', re.S|re.M)
        pin_pattern = re.compile(r'.*app\.page\["pins"\]\s?=\s?([^\n]+).*', re.S|re.M)

        query = returnJsonFromStr(res_html, page_pattern)
        pins = returnJsonFromStr(res_html, pin_pattern)

        avatar = query['text'] + '/' + category

        path_str_mk = pathBase('./huaban/'+avatar)

        if path_str_mk is None:
                return
        else:
            for item in pins:
                getContent(item, path_str_mk)
    else:
        print("【文档获取失败】【状态为%s】 - %s，" % (url, res.status_code))


def getContent(item, path_str_mk):
    title = item['raw_text']
    author = item['user']['username']
    href = 'http://img.hb.aicdn.com/' + item['file']['key']
    pic_type = item['file']['type']
    if title is not None:
        print("%s - 【%s】- %s" % (title, author, href))
        downloadImg(href, path_str_mk, pic_type)
    else:
        print("【文档获取失败】【href为%s】" % (href))

def pathBase(file_path):
    file_name_s = file_path.split("/")
    lenx = len(file_name_s)
    for i in range(0, lenx):
      path = "/".join(file_name_s[:i+1])
      if not os.path.exists(path):
          print(path)
          os.mkdir(path)
    return path

def downloadImg(url, path, pic_type):
    z_url = url.split("@")[0]
    z_hz = pic_type.split("/")[1]
    res = requests.get(z_url)
    if res.status_code == 200:
        img_down_path = path + "/" + str(uuid.uuid1()) + "." + z_hz
        f = open(img_down_path, 'wb')
        f.write(res.content)
        f.close()
        print("【下载成功】 -  %s" % img_down_path)
    else:
        print("【IMG下载失败】【状态为%s】 - %s，" % (z_url, res.status_code))

def returnJsonFromStr(str, pattern):
    remove_end_semicolon_pattern = re.compile(r'^(.*);\s*$')

    str_temp = pattern.match(str).group(1)
    str_res= remove_end_semicolon_pattern.match(str_temp).group(1)
    return json.loads(str_res)

def nameEncode(file_name):
    file_stop_str = ['\\', '/', '*', '?', ':', '"', '<', '>', '|']
    for item2 in file_stop_str:
        file_name = file_name.replace(item2, '-')
    return file_name

if __name__ == '__main__':
    threads = []

    key_work = input('关键字是：')
    count = input('最大张数：')

    if key_work is not '':
      keys = key_work.split('+')
      for key in keys:
        url = 'http://huaban.com/search/?q='+key + '&page=0&per_page=' + count
        threads.append(threading.Thread(target=startRequest, args={url}))

      for item in threads:
        item.start()
    else:
      exit()


            
        
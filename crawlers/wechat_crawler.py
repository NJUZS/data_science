import requests
import logging
import time
import json
import re


def weChat_spider(new_url, new_cookie):
    url = new_url
    headers = {'Cookie': new_cookie}
    logging.captureWarnings(True)

    r = requests.get(url, headers=headers, verify=False)
    content = r.json()

    temp = []

    for comment in content['elected_comment']:
        c_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment['create_time']))
        nick_name = comment['nick_name']
        content = re.sub('<[^<]+?>', '', comment['content']).replace('\n', '').strip()
        like_times = comment['like_num']
        print('评论时间:' + c_time + '    ' + nick_name + ":      " + content + "    点赞数:" + str(like_times) + " 次")
        tmp = {
            '评论': content,
            '点赞数': like_times,
            '昵称': nick_name,
            '评论时间': c_time
        }
        temp.append(tmp)
    return temp


def writeJson(temp, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(temp,f,ensure_ascii=False,indent=4)
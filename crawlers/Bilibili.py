import requests
import json
import re
import time


def crawlerOne(oid):
    result = []
    p=1
    while True:
        url='https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn={}&type=1&oid={}&sort=2'.format(p,oid)
        p += 1
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
        }
        res = requests.get(url, headers=headers).content.decode('utf-8')
        time.sleep(0.5)
        jsonfile = json.loads(res)
        data = jsonfile['data']
        pages = data['page']['count']/data['page']['size']
        pages = int(pages)
        if (p - 1) >= pages:
            return result
        replies = data['replies']
        for i in replies:
            created_time = i['ctime']
            timeArray = time.localtime(created_time)
            created_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            tmp = {
                '评论': i['content']['message'].replace('\n', '。').strip(),
                '点赞数': i['like'],
                '评论时间': created_time,
                '原视频av号': oid
            }
            result.append(tmp)
        print("{}/{}".format(p - 1, pages))


def writeJson(result, extra):
    result = json.dumps(result, ensure_ascii=False, indent=4)
    with open(r'../Result/bilibili/bilibili_{}.json'.format(extra), 'w', encoding='utf-8') as f:
        f.write(result)


def crawlers(oids, extra):
    results = []
    for i in range(0, len(oids)):
        results = results + crawlerOne(oids[i])
    writeJson(results, extra)


if __name__ == '__main__':
    # 一阶段(林晨武汉情况、人传人)
    # crawlers(["84495207", "84324588"], "1")

    # 二阶段(封城、李文亮医生去世)
    # crawlers(["84850049", "87432359"], "2")

    # 三阶段(全国支援、武汉封城20+天)
    # crawlers(["88497943", "88575746"], "3")

    # 四阶段(有序复工、武汉解封)
    crawlers(["327586498", "98263559", "370206659"], "4")
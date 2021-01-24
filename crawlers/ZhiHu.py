import re
import time
import requests
import json

def crawlerOne(type, id):
    i=0
    result = []
    if type == "articles":
        base_url = "https://zhuanlan.zhihu.com/p/{}".format(id)
    else:
        base_url = "https://www.zhihu.com/{}/{}".format(type[:-1], id)
    while True:
        url='https://www.zhihu.com/api/v4/{}/{}/root_comments?order=normal&limit=20&offset={}&status=open'.format(type,id,i)
        i+=20
        print(f'正在打印第{i/20}页')
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "Refer": "https://www.zhihu.com/"
        }
        res=requests.get(url,headers=headers).content.decode('utf-8')
        time.sleep(1)
        jsonfile=json.loads(res)
        try:
            next_page=jsonfile['paging']['is_end']
            print(next_page)
            for data in jsonfile['data']:
                # id=data['id']
                content=data['content']
                content = re.sub('<[^<]+?>', '', content).replace('\n', '').strip()
                # author=data['author']['member']['name']
                vote_count = data['vote_count']
                created_time = data['created_time']
                timeArray = time.localtime(created_time)
                created_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
                # print(true_time)
                # print(id,content,author)
                print(content)
                print("点赞数: {}".format(vote_count))
                print(created_time)
                tmp = {
                    '评论': content,
                    '点赞数': vote_count,
                    '评论时间': created_time,
                    '原文章或回答地址': base_url
                }
                # json_str = json.dumps(tmp, ensure_ascii=False, indent=4)
                result.append(tmp)
            if next_page==True:
                return result
        except:
            print("Something Wrong Happened!")
            print(jsonfile)
            exit(-1)


def writeJson(result, extra):
    result = json.dumps(result, ensure_ascii=False, indent=4)
    with open(r'../Result/zhihu/zhihu_{}.json'.format(extra), 'w', encoding='utf-8') as f:
        f.write(result)


def crawlers(type, id, extra):
    results = []
    if len(type) != len(id):
        print("Wrong Input!")
        return
    for i in range(0, len(type)):
        results = results + crawlerOne(type[i], id[i])
    writeJson(results, extra)


if __name__ == '__main__':
    # 总历程回顾
    # crawlers(["articles"], ["103691078"], "0_allReview")

    # 一阶段: 发现、人传人
    # crawlers(["questions", "answers"], ["363894293", "957302834"], "1_find")
    # crawlers(["questions", "answers"], ["367219889", "981345913"], "1_p2p")

    # 二阶段: 火神山雷神山、吹哨人去世、武汉封城
    # crawlers(["questions", "answers"], ["367638640", "984124605"], "2_hospital")
    # crawlers(["articles", "questions", "answers"], ["105509165", "369545723", "998673515"], "2_worsen")
    # crawlers(["questions", "answers", "answers"], ["367539143", "983360954", "983191869"], "2_lockdown")

    # 三阶段: 严控、支援
    # crawlers(["answers"], ["1027280218"], "3_control")
    # crawlers(["answers"], ["1045578387"], "3_help")

    # 四阶段: 防控、转折点(领导摘口罩)、武汉解封
    # crawlers(["answers"], ["1133585364"], "4_prevention")
    # crawlers(["answers", "answers"], ["1098250833", "1102378555"], "4_inflectionPoint")
    crawlers(["questions", "answers", "answers"], ["382039679", "1118536602", "1128094034"], "4_endLockdown")
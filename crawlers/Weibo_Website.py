import re
import time
import json
import urllib
import requests
from lxml import etree


def get_ajax_url(user):
    url = 'https://weibo.com/%s?&page=1&is_all=1'%user
    res = requests.get(url, headers=headers,cookies=cookies)
    html  = res.text
    page_id = re.findall("CONFIG\['page_id'\]='(.*?)'",html)[0]
    domain = re.findall("CONFIG\['domain'\]='(.*?)'",html)[0]
    start_ajax_url1 = 'https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=%s&is_all=1&page={0}&pagebar=0&pl_name=Pl_Official_MyProfileFeed__20&id=%s&script_uri=/%s&pre_page={0}'%(domain,page_id,user)
    start_ajax_url2 = 'https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=%s&is_all=1&page={0}&pagebar=1&pl_name=Pl_Official_MyProfileFeed__20&id=%s&script_uri=/%s&pre_page={0}'%(domain,page_id,user)
    return start_ajax_url1,start_ajax_url2


def parse_home_url(url):
    res = requests.get(url, headers=headers,cookies=cookies)
    response = res.content.decode().replace("\\", "")
    every_id = re.compile('name=(\d+)', re.S).findall(response) # 获取次级页面需要的id
    home_url = []
    for id in every_id:
        base_url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&id={}&from=singleWeiBo'
        url = base_url.format(id)
        home_url.append(url)
    return home_url


def get_home_url(user,startPage, endPage, keywords):
    start_url = 'https://weibo.com/%s?is_search=1&page={}&is_all=1&key_word={}' % user
    start_ajax_url1,start_ajax_url2 = get_ajax_url(user)
    all_url = []
    for i in range(startPage, endPage):
        home_url = parse_home_url(start_url.format((i + 1), keywords)) # 获取每一页的微博
        # 默认设置关键词查询后符合条件的微博数不大于15
        if keywords != '':
            all_url += home_url
            print('第%d页解析完成' % (i + 1))
            continue
        ajax_url1 = parse_home_url(start_ajax_url1.format(i + 1)) # ajax加载页面的微博
        ajax_url2 = parse_home_url(start_ajax_url2.format(i + 1)) # ajax第二页加载页面的微博
        all_url = home_url + ajax_url1 + ajax_url2
        print('第%d页解析完成'%(i+1))
    return all_url


def parse_comment_info(data_json):
    html = etree.HTML(data_json['data']['html'])
    name = html.xpath("//div[@class='list_li S_line1 clearfix']/div[@class='WB_face W_fl']/a/img/@alt")
    info = html.xpath("//div[@node-type='replywrap']/div[@class='WB_text']/text()")
    info = "".join(info).replace(" ", "").split("\n")
    info.pop(0)
    likes = html.xpath("//span[@node-type='like_status']/em[last()]")
    comment_time = html.xpath("//div[@class='WB_from S_txt2']/text()") # 评论时间
    name_url = html.xpath("//div[@class='WB_face W_fl']/a/@href")
    name_url = ["https:" + i for i in name_url]
    ids = html.xpath("//div[@node-type='root_comment']/@comment_id")
    try:
        next_url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&from=singleWeiBo&'+html.xpath('/html/body/div/div/div[%d]/@action-data'%(len(name)+1))[0]+'&__rnd='+str(int(time.time()*1000))
    except:
        try:
            next_url = 'https://weibo.com/aj/v6/comment/big?ajwvr=6&from=singleWeiBo&'+html.xpath('/html/body/div/div/a/@action-data')[0]+'&__rnd='+str(int(time.time()*1000))
        except:
            next_url = ''
    comment_info_list = []
    for i in range(len(name)):
        item = {}
        # item["id"] = ids[i]
        item["用户名称"] = name[i] # 存储评论人的网名
        item["评论"] = info[i][1:]# 存储评论的信息
        # print(item["comment_info"])
        item["点赞数"] = likes[i].text # 存储点赞数
        if likes[i].text == '赞':
            item["点赞数"] = "0"
        item["评论时间"] = comment_time[i] # 存储评论时间
        # item["评论url"] = name_url[i] # 存储评论人的相关主页
        comment_info_list.append(item)
    return comment_info_list,next_url


def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = 'utf8'
        return r.text
    except:
        return ""

def getUID(name):
    try:
        url = "https://s.weibo.com/user?q=%s&Refer=SUer_box" % name
        html = getHTMLText(url)

        plt = re.findall('class="s-btn-c" uid=([1-9][0-9]{9})', html)
        if len(plt) >= 1:
            return plt[0]
        return ""
    except:
        return ""


if "__main__" == __name__:
    # 设置相应参数
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
    }
    cookies = {
        'cookie': ""
    } # 设置微博cookies
    userid = getUID('澎湃新闻')  # 需要爬取的微博用户ID
    keywords = "复工复产 企业" # 设置关键词用于搜索符合条件微博
    startPage = 0     # 爬取的起始页数
    endPage = 1     # 爬取的截止页数
    # 开始爬取
    all_urls = get_home_url(userid,startPage, endPage, keywords)
    comment_info_list = []
    for index in range(len(all_urls)):
        print("{}/{}".format((index+1), len(all_urls)))
        url = all_urls[index]
        print(url)
        print('开始获取第%d个微博评论...'%(index+1))
        res = requests.get(url, headers=headers, cookies=cookies)
        time.sleep(2)
        data_json = res.json()
        count = data_json['data']['count']
        comment_info,next_url = parse_comment_info(data_json)
        comment_info_list.extend(comment_info)
        print('已经获取%d条'%len(comment_info_list))
        while True:
            if next_url == '':
                break
            try:
                res = requests.get(next_url,headers=headers,cookies=cookies)
                time.sleep(0.75)
                data_json = res.json()
                comment_info,next_url = parse_comment_info(data_json)
                comment_info_list.extend(comment_info)
                print('已经获取%d条'%len(comment_info_list))
                if len(comment_info_list) == 189:
                    break
            except:
                break
    with open(r'../Result/微博评论{}.json'.format(keywords), 'w', encoding='utf-8') as f:
        f.write(json.dumps(comment_info_list, ensure_ascii=False, indent=4))

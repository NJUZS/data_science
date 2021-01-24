import csv
import json
from pyhanlp import *


# 将爬取后保存的json文件转换为具体数据并加入平台，阶段信息
def json2str(filepath):
    platforms = ["bilibili", "zhihu", "weibo", "weChat"]
    periods = ["1","2","3","4"]
    fromP = ""
    period = ""
    for p in periods:
        if "weChat" in filepath:
            if "202001" in filepath:
                period = 1
            elif "202002" in filepath:
                period = 2
            elif "202003" in filepath:
                period = 3
            else:
                period = 4
        if ("_"+p) in filepath or (p+"_") in filepath:
            period = p
    for p in platforms:
        if p in filepath:
            fromP = p
    data = []
    # print(filepath)
    with open(filepath, 'r', encoding='utf-8') as file:
        try:
            tmp = json.load(file)
            for comment in tmp:
                if comment['评论'] != '该评论已删除' and comment['评论'] != '':
                    res = [comment['评论'], comment['点赞数'], fromP, period]
                    data.append(res)
        except:
            print("Error: "+filepath)
    return data


# 获取目录下全部结果json文件
def findAllJson(fileDir):
    res = []
    for filex in os.walk(fileDir):
        res.extend([filex[0] + '\\' + target for target in filex[2] if 'json' in target])
    return res


# 将所有json文件整合写入csv，作为原始数据集
def writeCSV(files):
    data = []
    data.extend([["Comment", "Likes", "Platform", "Period", "TF", "TF_IDF", "Sentiment", "Cuts"]])
    for filepath in files:
        res = json2str(filepath)
        data.extend(res)
    # print(data)
    with open("./Resources/originData.csv", 'w', newline='', encoding='utf-8-sig') as csvFile:
        writer = csv.writer(csvFile)
        for row in data:
            writer.writerow(row)
        csvFile.close()
    print("成功写入CSV文件！")
    exit(1)


# 生成词表用以关键词提取
def wordList():
    filepath = "./test.json"
    with open(filepath, 'r', encoding='utf-8') as file:
        tmp = json.load(file)
        file.close()
    with open("./wordList.txt", 'w', encoding='utf-8') as file:
        for x in tmp:
            x = list(x.keys())[0]
            file.writelines(x + "\n")
    exit(2)


if "__main__" == __name__:
    # 生成词表
    # wordList()

    results = {}
    fileDir = "./Result"
    files = findAllJson(fileDir)
    # 暂不处理格式不同且包含大量无意义数据的新浪新闻及助教微博数据
    del files[0]
    del files[0]
    del files[0]
    del files[0]

    # 将所有爬取的json文件整合写入csv
    writeCSV(files)

    # 生成按词频排序的关键词表
    # 初始化自带的停用词表
    CoreStopWordDictionary = JClass('com.hankcs.hanlp.dictionary.stopword.CoreStopWordDictionary')
    for filepath in files:
        print("正在处理: " + filepath)
        str_list = json2str(filepath)
        for comment in str_list:
            comment = comment[0]
            data = HanLP.segment(comment)
            # 启用自带的停用词表
            CoreStopWordDictionary.apply(data)
            for x in data:
                # 去除通常不具情感态度的名词
                if '/n' not in str(x):
                    keyword = str(x)[0:str(x).rfind('/')]
                    if keyword in results:
                        results[keyword] += 1
                    else:
                        results[keyword] = 1
    results = sorted(results.items(), key=lambda item: item[1], reverse=True)
    res = []
    for tmp in results:
        tmp_dict = {}
        tmp = list(tmp)
        tmp_dict[tmp[0]] = tmp[1]
        res.append(tmp_dict)
    print(res)
    with open(r'./test.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(res, ensure_ascii=False, indent=4))
    print("finished!")


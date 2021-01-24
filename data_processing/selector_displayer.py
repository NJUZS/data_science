import json
import re
import jieba
import os
import jieba.analyse
import jieba.posseg
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def getCommentsFromOneFile(path):
    with open(path, 'r', encoding='utf-8') as load_f:
        load_list = json.load(load_f)
    comments = []
    stopwords = [line.strip() for line in open('stopword.txt', encoding='UTF-8').readlines()]
    for comment in load_list:
        item = comment['评论']
        item = re.sub(u'\\[.*?]', '', item)
        item = re.sub(u'[^\u4e00-\u9fa5]', '', item)
        list = jieba.posseg.cut(item)
        for word in list:
            if word.word not in stopwords and (word.flag is 'v' or word.flag is 'a') and len(word.word) > 1 :
                comments.append(word.word)
    return comments

def getComments(path):
    out = []
    filepath = os.listdir(path)
    for files in filepath:
        comments = getCommentsFromOneFile(path + files)
        out += comments
    return out


def getTFIDFWords(list):
    text_split_no_str = ' '.join(list)
    keywords = []
    for x, w in jieba.analyse.extract_tags(text_split_no_str, topK=200, withWeight=True):
        keywords.append(x)  # 前200关键词组成的list
    keywords = ' '.join(keywords)  # 转为str
    print(keywords)
    return keywords


def display(keywords):
    wordcloud = WordCloud(font_path="C:/Windows/Fonts/simfang.ttf",
                          background_color="white", width=1000, height=880).generate(keywords)  # keywords为字符串类型
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.show()
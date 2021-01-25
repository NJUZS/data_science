import csv
import json
import random
import re
import time
import pandas as pd
import numpy as np
from pyhanlp import *
from sklearn import metrics
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline


# 实现对每条评论打情感值标签，并计算TF_IDF及返回分词结果储存备用
def makeLabels(comments):
    # 初始化自带的停用词表
    CoreStopWordDictionary = JClass('com.hankcs.hanlp.dictionary.stopword.CoreStopWordDictionary')
    res = []
    TFs = []
    TF_IDFs = []
    Cuts = []
    for i in range(len(comments)):
        comment = comments[i]
        data = HanLP.segment(comment)
        # 启用自带的停用词表
        CoreStopWordDictionary.apply(data)
        words = []
        cutComment = ""
        for word in data:
            # 去除词性
            word = str(word)[0:str(word).rfind('/')]
            word = re.sub("[A-Za-z0-9]", "", word)
            words.append(word)
            cutComment += word + ' '
        Cuts.append(cutComment)

        tmp = sentiment_calculate(words)
        # 规范情感取值以适应机器学习模型
        senti = int(tmp[0]) # 两种中立均规范为0
        senti = standard_sentiment(senti) # 其余情感值规范
        # senti = tmp[0]
        res.append(str(senti))
        TFs.append(tmp[1])
        TF_IDFs.append(tmp[2])
        # print(str(sentiment_calculate(words)))
        print(r"处理进度: {}/{}".format(i+1, len(comments)))
    return [res, TFs, TF_IDFs, Cuts]


# 判断是否在对应词典中
def isKeyword(word):
    if word in level:
        return 4
    elif word in deny:
        return -4
    elif word in positive_1:
        return 1
    elif word in positive_2:
        return 2
    elif word in positive_3:
        return 3
    elif word in negative_1:
        return -1
    elif word in negative_2:
        return -2
    elif word in negative_3:
        return -3
    else:
        return 0


# 计算每条评论情感词
def sentiment_calculate(words):
    res = 0
    countK = 0
    TF_IDFs = {}
    TF = {}
    frequency = 0
    try:
        frequency = 1/len(words)
        frequency = round(frequency, 5)
    except:
        print("空!")
    for i in range(len(words)):
        x = isKeyword(words[i])
        if x != 0:
            # 该条评论关键词数+1
            countK += 1
            if words[i] in TF:
                TF[words[i]] += frequency
            else:
                TF[words[i]] = frequency
            TF_IDFs[words[i]] = round(TF[words[i]] * IDFs[words[i]], 5)
        # 否定词检测后一个词，若是情感词则权重取反
        if x == -4 and i < len(words)-1:
            res -= 2*isKeyword(words[i+1])
        # 程度副词检测后一个词，若是情感词则权重加倍
        elif x == 4 and i < len(words)-1:
            res += isKeyword(words[i+1])
        # 否定词且后一个词不是情感词
        elif x == -4:
            res -= 0.5
        # 其余情感词加减相应权重
        elif x != 0:
            res += x
        else:
            pass
    if res == 0 and countK > 0:
        res = random.random()/1000 # 出现了关键情感词但最终权重为0，表示中立Ⅱ，同中立Ⅰ(冷漠无感)区分
    return [res, TF, TF_IDFs]


# 规范化情感值
def standard_sentiment(senti):
    # 正负Ⅲ级
    if senti >= 5:
        senti = 5
    elif senti <= -5:
        senti = -5
    # 正负Ⅱ级
    elif senti >= 2.5:
        senti = 3
    elif senti <= -2.5:
        senti = -3
    # 正负Ⅰ级
    elif senti < 0:
        senti = -1
    elif senti > 0:
        senti = 1

    return senti


def IDF_calculate(word):
    # 初始设定为1，相当于避免分母为0做平滑处理，其后公式中总数+1同为平滑处理
    countI = 1
    for comment in comments:
        if word in comment:
            countI += 1
    countI = (len(comments)+1)/countI
    countI = np.log(countI) + 1
    return countI


# 计算八个词典中所有词IDF并保存为json文件
def write_IDF():
    data = []
    IDFs = {}
    data.extend(positive_1)
    data.extend(positive_2)
    data.extend(positive_3)
    data.extend(negative_1)
    data.extend(negative_2)
    data.extend(negative_3)
    data.extend(level)
    data.extend(deny)
    for i in data:
        tmp = {
            i : IDF_calculate(i)
        }
        IDFs.update(tmp)
    result = json.dumps(IDFs, ensure_ascii=False, indent=4)
    with open(r'.\Resources\wordList\IDFs.json', 'w', encoding='utf-8') as f:
        f.write(result)
    exit(5)


# 获取IDF值字典
def getIDFs():
    with open(r'.\Resources\wordList\IDFs.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        f.close()
    return data


# 读取TXT
def readTXT(filepath):
    res = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for i in file.readlines():
            res.append(i.strip('\n'))
        file.close()
    return res


# 清洗数据
def cleanData(data):
    tmp = []
    for i in range(len(data)):
        if data[i][1] == 0 and not data[i][4]:
            tmp.append(data[i])
            pass
        else:
            tmp.append(data[i])
    data = [["Comment", "Likes", "Platform", "Period", "TF", "TF_IDF", "Sentiment", "Cuts"]]
    data.extend(tmp)
    print("清洗结束，剩余{}条".format(len(data) - 1))
    return data


def testsForCut():
    df = pd.read_csv("./Resources/dataTest.csv", encoding="utf-8")
    comments = df['Comment']
    data = df.values.tolist()
    # 初始化自带的停用词表
    CoreStopWordDictionary = JClass('com.hankcs.hanlp.dictionary.stopword.CoreStopWordDictionary')
    for i in range(1,len(data)):
        comment = comments[i]
        res = HanLP.segment(comment)
        # 启用自带的停用词表
        CoreStopWordDictionary.apply(res)
        cutComment = ""
        for word in res:
            # 去除词性
            word = str(word)[0:str(word).rfind('/')]
            word = re.sub("[A-Za-z0-9]", "", word)
            cutComment += word + ' '
        data[i][2] = cutComment
    res = [["Comment", "Sentiment", "Cuts"]]
    res.extend(data)
    with open("./Resources/dataTest.csv", 'w', newline='', encoding='utf-8-sig') as csvFile:
        writer = csv.writer(csvFile)
        for row in res:
            writer.writerow(row)
        csvFile.close()
    print("分词完成！")



# 训练模型
def train_model():
    df = pd.read_csv("./Resources/tmpData.csv", encoding = "utf-8")
    X = df['Cuts']
    X.fillna('', inplace=True)
    y = df['Sentiment']
    # print(X.head())
    # print(y.head())

    max_df = 0.7  # 在超过这一比例的文档中出现的关键词（过于平凡），去除
    min_df = 10  # 在低于这一数量的文档中出现的关键词（过于独特），去除
    vector = CountVectorizer(max_df=max_df,
                           min_df=min_df)
    # 训练集测试集比例3：2
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=66)
    # print(X_train.head())
    # print(y_train.head())
    # print(X_train.shape)
    # print(y_train.shape)
    # print(X_test.shape)
    # print(y_test.shape)
    term_matrix = pd.DataFrame(vector.fit_transform(X_train).toarray(), columns=vector.get_feature_names())
    print(term_matrix.head())
    # 数据量不算大，选用朴素贝叶斯模型
    nb = MultinomialNB()
    pipe = make_pipeline(vector, nb)
    res = cross_val_score(pipe, X_train, y_train, cv=5, scoring='accuracy').mean()
    print(res)
    # 输出测试集准确率
    pipe.fit(X_train, y_train)
    # pipe.predict(X_test)
    y_pred = pipe.predict(X_test)
    res = metrics.accuracy_score(y_test, y_pred)
    print(res)
    # 输出混淆矩阵
    res = metrics.confusion_matrix(y_test, y_pred)
    print(res)

    testsForCut()
    dt = pd.read_csv("./Resources/dataTest.csv", encoding = "utf-8")
    z = dt['Cuts']
    z.fillna('', inplace=True)
    res = pipe.predict(z)
    data = dt.values.tolist()
    for i in range(len(data)):
        data[i][1] = res[i]
    res = [["Comment","Sentiment","Cuts"]]
    res.extend(data)
    with open("./Resources/dataTest.csv", 'w', newline='', encoding='utf-8-sig') as csvFile:
        writer = csv.writer(csvFile)
        for row in res:
            writer.writerow(row)
        csvFile.close()
    print("预测已写入！")
    exit(2)


if "__main__" == __name__:
    # train_model()
    df = pd.read_csv("./Resources/originData.csv", encoding = "utf-8")
    # print(df.head())
    # print(df.shape)

    start = time.time()
    # 词典初始化
    positive_1 = readTXT("./Resources/wordList/positive_1.txt")
    positive_2 = readTXT("./Resources/wordList/positive_2.txt")
    positive_3 = readTXT("./Resources/wordList/positive_3.txt")
    negative_1 = readTXT("./Resources/wordList/negative_1.txt")
    negative_2 = readTXT("./Resources/wordList/negative_2.txt")
    negative_3 = readTXT("./Resources/wordList/negative_3.txt")
    deny = readTXT("./Resources/wordList/negator.txt")
    level = readTXT("./Resources/wordList/level_plus.txt")
    IDFs = getIDFs()

    comments = list(df['Comment'])
    # write_IDF()
    result = makeLabels(comments)
    Cuts = result[3]
    TFs = result[1]
    TF_IDFs = result[2]
    Sentiment = result[0]
    res = np.array(df).tolist()
    for i in range(len(res)):
        print("更新进度: {}/{}".format(i, len(res)))
        res[i][1] = np.log10(res[i][1] + 1)
        res[i][4] = TFs[i]
        res[i][5] = TF_IDFs[i]
        res[i][6] = Sentiment[i]
        res[i][7] = Cuts[i]
    data = cleanData(res)
    # 写入csv
    with open("./Resources/tmpData.csv", 'w', newline='', encoding='utf-8-sig') as csvFile:
        writer = csv.writer(csvFile)
        for row in data:
            writer.writerow(row)
        csvFile.close()
    print("成功写入CSV文件！")
    end = time.time()
    print(end-start)
    # exit(1)
    # 写入json
    x = []
    for i in range(1, len(data)):
        tmp = {}
        tmp['Comment'] = data[i][0]
        tmp['Likes'] = data[i][1]
        tmp['Platform'] = data[i][2]
        tmp['Period'] = data[i][3]
        tmp['TF'] = data[i][4]
        tmp['TF_IDF'] = data[i][5]
        tmp['Sentiment'] = data[i][6]
        tmp['Cuts'] = data[i][7]
        x.append(tmp)
    endd = time.time()
    result = json.dumps(x, ensure_ascii=False, indent=4)
    with open(r'./Resources/data.json', 'w', encoding='utf-8') as f:
        f.write(result)
        f.close()
    print("成功写入JSON文件！")
    print(endd-start)

from snownlp import SnowNLP
import snownlp
import json
import requests
import jieba
import pandas as pd


def SNOW_NLP_ORIGIN_TEST(path):
    # 调用SNOW_NLP进行情感预测
    total_num = 0
    correct_num = 0
    with open(path, 'r') as f:
        data = pd.read_csv(f)

    for index, row in data.iterrows():
        nlp = SnowNLP(row['content'])

        if abs(float(nlp.sentiments) - float(row['sentiment'])) <= 0.5:
            correct_num = correct_num + 1
        total_num = total_num + 1
        print("{}/{}".format(correct_num, total_num))

    print("训练集大小：{}, 正确率：{}".format(total_num, correct_num / total_num))


def Hanlp_ORIGIN_TEST(path):
    # 调用Hanlp进行预测
    total_num = 0
    correct_num = 0
    with open(path, 'r') as f:
        data = pd.read_csv(f)

    for index, row in data.iterrows():
        if Hanlp(row['content']) == row['sentiment']:
            correct_num = correct_num + 1
        total_num = total_num + 1
        print("{}/{}".format(correct_num, total_num))

    print("训练集大小：{}, 正确率：{}".format(total_num, correct_num / total_num))


def Hanlp(txt):
    headers = {'token': "8ff8c22edc774d25a52003d6b51d62061609061981838token"}
    data = {'text': txt}
    response = requests.post("http://comdo.hanlp.com/hanlp/v1/textAnalysis/sentimentAnalysis", data=data, headers=headers)
    s = response.content.decode('utf-8')
    if "情感极性是 【正面】" in s:
        return 1
    else:
        return 0


if __name__ == "__main__":
    Hanlp_ORIGIN_TEST('../../dataSets/sina/样本/新浪所有新闻评论训练集.CSV')
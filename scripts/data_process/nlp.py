from snownlp import SnowNLP
import snownlp
import json
import requests
import jieba
import pandas as pd
import numpy as np
from gensim.models.word2vec import Word2Vec
from sklearn.externals import joblib
from sklearn.model_selection import cross_val_score
from sklearn.svm import SVC
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
import gensim
from sklearn.model_selection import cross_val_score
from sklearn import neighbors
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn import metrics
from sklearn import tree
from sklearn.linear_model import LogisticRegression
from sklearn.linear_model import Perceptron            #感知机算法
from sklearn.linear_model import SGDClassifier         #梯度下降分类
from sklearn.ensemble import RandomForestClassifier    #随机森林
from keras.models import Sequential
from keras.layers import Dense
import keras
import csv
import pickle
import jieba.analyse
from sklearn.neighbors import KNeighborsClassifier


def Hanlp(url, token, txt):
    # 调用Hanlp进行情感预测
    headers = {'token': token}
    data = {'text': txt}
    response = requests.post(url, data=data, headers=headers)
    s = response.content.decode('utf-8')
    print(s)
    if "情感极性是 【正面】" in s:
        print("正面")
        return 1
    else:
        print('负面')
        return 0


def train_word2vec_model(dimension):
    '''
    训练word2vec模型
    :param dimension:维度
    :return:
    '''
    with open('../../dataSets/sina/新浪语料库.csv', 'r', encoding='utf-8') as f:
        total = pd.read_csv(f, quoting=csv.QUOTE_NONE)
    with open('../../dataSets/bilibili/样本/bilibili弹幕全集.csv', 'r', encoding='utf-8') as f:
        bilibili = pd.read_csv(f)
    total['content'] = total['content'].apply(lambda x: jieba.lcut(str(x)))
    bilibili['content'] = bilibili['content'].apply(lambda x: jieba.lcut(str(x)))
    total = np.concatenate((total['content'], bilibili['content']))
    # 初始化高维空间
    w2v = Word2Vec(size=dimension)
    w2v.build_vocab(total)
    # 训练模型
    w2v.train(total, total_examples=w2v.corpus_count, epochs=w2v.iter)
    # 保存模型
    w2v.save('../../model/nlp/w2v_{}维_560万语料库.w2v'.format(dimension))


def train_nlp_model(train_model, dimension, word2vec_model):
    """
    传入要训练的模型，设定训练集向量化维度并开始训练
    :param train_model: 要训练的模型
    :param dimension: 训练集向量化的维度
    :return:
    """

    def total_vec(words, dim):
        vec = np.zeros(dim).reshape((1, dim))
        for word in words:
            try:
                vec += w2v.wv[word].reshape((1, dim))
            except KeyError:
                continue
        return vec

    with open('../../dataSets/sina/样本/新浪所有新闻评论训练集-正面.CSV', 'r') as f:
        pos = pd.read_csv(f)

    with open('../../dataSets/sina/样本/新浪所有新闻评论训练集-负面.CSV', 'r') as f:
        neg = pd.read_csv(f)

    # with open('../../dataSets/bilibili/样本/bilibili弹幕训练集-正面.csv', 'r') as f:
    #     pos = pd.read_csv(f)
    #
    # with open('../../dataSets/bilibili/样本/bilibili弹幕训练集-负面.csv', 'r') as f:
    #     neg = pd.read_csv(f)

    # 分词
    neg['content'] = neg['content'].apply(lambda x: jieba.lcut(x))
    pos['content'] = pos['content'].apply(lambda x: jieba.lcut(x))

    # 合并训练集
    x = np.concatenate((pos['content'], neg['content']))
    # 标签集
    y = np.concatenate((np.ones(len(pos)), np.zeros(len(neg))))

    w2v = word2vec_model

    # 获得向量训练集
    all_vec = np.concatenate([total_vec(words, dimension) for words in x])
    train_vec, test_vec, train_y, test_y = train_test_split(all_vec, y, test_size=0.1)

    # 初始模型并训练
    print("开始训练模型")
    model = train_model.fit(train_vec, train_y)
    clf = model

    # 测试
    # scores = cross_val_score(clf, all_vec, y, cv=5)
    # print(scores)
    test_predict = model.predict(test_vec)
    train_predict = model.predict(train_vec)

    print("测试集报告：")
    print(metrics.classification_report(test_y, test_predict, digits=3))
    print("训练集报告：")
    print(metrics.classification_report(train_y, train_predict, digits=3))
    # 保存模型
    # joblib.dump(model, '../../model/nlp/bilibili_nlp_model.joblib')


def test_nlp_model(model, dimension, word2vec_model):
    w2v = word2vec_model

    def total_vec(words, dim):
        vec = np.zeros(dim).reshape((1, dim))
        for word in words:
            try:
                vec += w2v.wv[word].reshape((1, dim))
            except KeyError:
                continue
        return vec
    with open('../../dataSets/bilibili/样本/bilibili弹幕训练集-labeled.csv', 'r', errors='ignore') as f:
        test_data = pd.read_csv(f)
    test_data['content'] = test_data['content'].apply(lambda x: jieba.lcut(x))
    x = test_data['content']
    y = test_data['sentiment']

    x_vec = np.concatenate([total_vec(words, dimension) for words in x])
    test_predict = model.predict(x_vec)
    print(metrics.classification_report(y, test_predict, digits=3))


def toVec(words, dim, word2vec):
    # 将字符串转化为高维向量
    words = jieba.lcut(words)
    vec = np.zeros(dim).reshape((1, dim))
    for word in words:
        try:
            vec += word2vec.wv[word].reshape((1, dim))
        except KeyError:
            continue
    return vec


def model_predict(words, dim, model, word2vec):
    # 利用SVM模型判断情感
    return model.predict(toVec(words, dim, word2vec))


def predict():
    # 使用训练好的模型预测数据
    w2v = Word2Vec.load('../../model/nlp/w2v_300维_560万语料库.w2v')
    model = joblib.load('../../model/nlp/sina_nlp_model.joblib')

    with open('../../dataSets/sina/新浪所有新闻.json', 'r', encoding='utf-8') as f:
        sina_news = json.load(f)

    new_sina_news = []
    count = 0

    for news in sina_news:
        hot_comment_list = []
        comment_list = []
        for comment in news['hot_comment_list']:
            count += 1
            content = comment['content']
            try:
                s = model_predict(str(content), 300, model, w2v)[0]
                comment['sentiment'] = s
                hot_comment_list.append(comment)
                print(count)
            except:
                print("错误！")
                s = 'NaN'
                comment['sentiment'] = s
                hot_comment_list.append(comment)
                continue

        for comment in news['comment_list']:
            count += 1
            content = comment['content']
            try:
                s = model_predict(str(content), 300, model, w2v)[0]
                comment['sentiment'] = s
                comment_list.append(comment)
                print(count)
            except:
                print("错误！")
                s = 'NaN'
                comment['sentiment'] = s
                comment_list.append(comment)
                continue
        news['hot_comment_list'] = hot_comment_list
        news['comment_list'] = comment_list
        new_sina_news.append(news)

    with open('../../dataSets/sina/新浪所有新闻-predicted.json', 'w', encoding='utf-8') as f:
        json.dump(new_sina_news, f)


if __name__ == "__main__":
    # string = "中国必胜！"
    # result = SVM_predict(string, 300)
    # print(result)
    # 随机森林
    # train_model = RandomForestClassifier(max_depth=12)
    # 线性支持向量机
    # train_model = LinearSVC()
    # train_model = SVC()
    # 决策树
    # train_model = tree.DecisionTreeClassifier(max_depth=8)
    # knn
    # train_model = KNeighborsClassifier()
    # 贝叶斯
    # train_model = GaussianNB()
    # 感知机
    # train_model = Perceptron()
    # 神经网络
    train_model = MLPClassifier(hidden_layer_sizes=(50, ), activation='logistic', solver='adam', max_iter=4000)
    # 逻辑回归
    # train_model = LogisticRegression()
    train_nlp_model(train_model=train_model, dimension=300, word2vec_model=Word2Vec.load('../../model/nlp/w2v_300维_560万语料库.w2v'))

    # model = Word2Vec.load('../../model/nlp/w2v_300.w2v')
    # print(model.most_similar('', topn=20))
    # train_word2vec_model(200)
    # predict()




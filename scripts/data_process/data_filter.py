import jieba
import json
from jieba import analyse
from wordcloud import WordCloud
import pandas as pd
from bs4 import BeautifulSoup
import requests


def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()  # 如果状态不是200，引发HTTPError异常
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "产生异常"


def sina_filter(keywords):
    """
    根据关键词过滤
    :param keywords:关键词
    :return:
    """
    with open('../../dataSets/sina/sina_top_click_news.json', 'r') as f:
        sina_top_click_news = json.load(f)
    with open('../../dataSets/sina/sina_top_comment_news.json', 'r') as f:
        sina_top_comment_news = json.load(f)

    filter_sina_top_click_news = []
    filter_click_count = 0
    filter_sina_top_comment_news = []
    filter_comment_count = 0

    # 点击量新闻过滤
    for item in sina_top_click_news:
        words = jieba.lcut(item['title'])
        isMatch = False
        for word in words:
            if word in keywords:
                isMatch = True
                break
        if isMatch:
            filter_sina_top_click_news.append(item)
            filter_click_count = filter_click_count + 1
            continue
        for key in item['keywords']:
            if key in keywords:
                isMatch = True
                break
        if isMatch:
            filter_sina_top_click_news.append(item)
            filter_click_count = filter_click_count + 1
    # 评论量新闻过滤
    for item in sina_top_comment_news:
        words = jieba.lcut(item['title'])
        isMatch = False
        for word in words:
            if word in keywords:
                isMatch = True
                break
        if isMatch:
            filter_sina_top_comment_news.append(item)
            filter_comment_count = filter_comment_count + 1
            continue
        for key in item['keywords']:
            if key in keywords:
                isMatch = True
                break
        if isMatch:
            filter_sina_top_comment_news.append(item)
            filter_comment_count = filter_comment_count + 1

    print("新浪点击量排行新闻:{}".format(filter_click_count))
    print("新浪评论量排行新闻:{}".format(filter_comment_count))
    with open('../../dataSets/sina/新浪点击量排行新闻.json', 'w') as f:
        json.dump(filter_sina_top_click_news, f)
    with open('../../dataSets/sina/新浪评论量排行新闻.json', 'w') as f:
        json.dump(filter_sina_top_comment_news, f)


def bilibili_filter(base_keywords):

    uid_map = {"共青团中央": "20165629", "央视新闻": "456664753", "小央视频": "222103174", "中国日报": "21778636", "新华社":
            "473837611","人民网": "33775467", "央视频": "433587902", "光明日报": "404414222", "央视网快看": "451320374",
                   "观察者网": "10330740", "观视频工作室": "54992199", "环球时报": "10303206", "人民视频": "386265385",
               "广东共青团": "330383888", "浙江共青团": "384298638", "河南共青团": "323194278",
               "安徽共青团": "268810504", "湖南共青团": "43563506", "福建共青团": "28897026", "重庆共青团": "212375551",
               "四川共青团": "483940995", "贵州共青团": "452215100", "江西共青团": "109586062", "江苏共青团": "543191732",
               "云南共青团": "285216473"}
    for key in uid_map:
        print("开始筛选{}".format(key))

        with open("../../dataSets/bilibili/{}.json".format(key), 'r') as f:
            data = json.load(f)
        new_data = []
        pass_num = 0
        for item in data:
            bv = item['bvid']
            html = getHTMLText("https://www.bilibili.com/video/{}?".format(bv))

            soup = BeautifulSoup(html, 'html.parser')
            raw_keywords = soup.find('meta', {'itemprop': 'keywords', 'name': 'keywords'})
            keywords = []
            if raw_keywords != None:
                keywords = raw_keywords.get_attribute_list('content')

            item['keywords'] = keywords
            print('{}: 时间：{}, title: {}, keywords: {}'.format(key, item['created'], item['title'], item['keywords']))
            fit = False
            for word in jieba.lcut(item['title']):
                if word in base_keywords:
                    fit = True
                    break
            if fit:
                new_data.append(item)
                pass_num = pass_num + 1
                print("符合！通过！{}".format(pass_num))
                continue

            for word in item['keywords']:
                for w in jieba.lcut(word):
                    if w in base_keywords:
                        fit = True
                        break
                if fit:
                    break

            if fit:
                new_data.append(item)
                pass_num = pass_num + 1
                print("符合！通过！{}".format(pass_num))
                continue

            for word in jieba.lcut(item['description']):
                if word in base_keywords:
                    fit = True
                    break
            if fit:
                new_data.append(item)
                pass_num = pass_num + 1
                print("符合！通过！{}".format(pass_num))
                continue

        with open("../../dataSets/bilibili/{}.json".format(key), 'w') as f:
            json.dump(new_data, f)
            print("{}保存成功！".format(key))


def sina_language_corpus():
    # 建立新浪语料库
    with open('../../dataSets/sina/sina_top_click_news.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    txt = "content\n"
    count = 0
    for news in data:
        for comment in news['hot_comment_list']:
            txt = txt + comment['content'].replace('\n', ' ').replace(',', '，') + '\n'
            count += 1
        for comment in news['comment_list']:
            txt = txt + comment['content'].replace('\n', ' ').replace(',', '，') + '\n'
            count += 1
        print(count)
    with open('../../dataSets/sina/sina_top_comment_news.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    for news in data:
        for comment in news['hot_comment_list']:
            txt = txt + comment['content'].replace('\n', ' ').replace(',', '，') + '\n'
            count += 1
        for comment in news['comment_list']:
            txt = txt + comment['content'].replace('\n', ' ').replace(',', '，') + '\n'
            count += 1
        print(count)
    with open('../../dataSets/sina/新浪语料库.csv', 'w', encoding='utf-8') as f:
        f.write(txt)


if __name__ == "__main__":
    # 用于过滤的关键词
    keywords = ['疫情', '防控', '复工', '复产', '肺炎', '确诊', '病例', '新冠',
                '防控', '病毒', '抗疫',  '防疫', '疫苗', '抗体', '冠状', '口罩'
                '世卫', '冠状病毒',  '新冠肺炎', '钟南山']
    # sina_filter(keywords)
    bilibili_filter(keywords)
    jieba.analyse.extract_tags()


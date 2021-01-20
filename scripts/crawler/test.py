import requests
from bs4 import BeautifulSoup
import json
import datetime


def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status() # 如果状态不是200，引发HTTPError异常
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "产生异常"


if __name__ == "__main__":
    with open('../../dataSets/sina/新浪所有新闻.json', 'r') as f:
        data = json.load(f)
    comment_count = 0
    txt = "time,content,agree,sentiment\n"
    for item in data:

        for i in item['hot_comment_list']:
            txt = txt + item['create_date'] + ',' + i['content'].replace(',', '，').replace('\n', ' ') + ',' + i['agree']\
                  + ',' + 'NaN\n'
            comment_count = comment_count + 1
            print(comment_count)

        for i in item['comment_list']:
            txt = txt + item['create_date'] + ',' + i['content'].replace(',', '，').replace('\n', ' ') + ',' + i['agree'] \
                  + ',' + 'NaN\n'
            comment_count = comment_count + 1
            print(comment_count)

    print("评论数：{}".format(comment_count))
    with open('../../dataSets/sina/样本/新浪所有新闻评论全集.csv', 'w', encoding='utf-8') as f:
        f.write(txt)




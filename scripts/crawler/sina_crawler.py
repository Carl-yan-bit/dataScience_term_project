import requests
from bs4 import BeautifulSoup
import json
import datetime
import re
import jieba
from jieba import analyse
import time


def getTOP_COMMENT_NEWS_URL(year, month, day, count):
    """
    获取新浪新闻某天评论数前count个的新闻的js的url
    :param year:年份
    :param month:月份
    :param day:日期
    :param count:数量
    :return:新浪新闻某天评论数前count个的新闻的js的url
    """
    return "http://top.news.sina.com.cn/ws/GetTopDataList.php?top_type=day&top_cat=qbpdpl&top_time={}{}{}&" \
           "top_show_num={}&top_order=DESC&js".format(year, month, day, count)


def getTOP_CLICK_NEWS_URL(year, month, day, count):
    """
        获取新浪新闻某天点击量前count个的新闻的js的url
        :param year:年份
        :param month:月份
        :param day:日期
        :param count:数量
        :return:新浪新闻某天点击量前count个的新闻的js的url
        """
    return "http://top.news.sina.com.cn/ws/GetTopDataList.php?top_type=day&top_cat=www_www_all_suda_suda&top_time=" \
           "{}{}{}&top_show_num={}&top_order=DESC&js".format(year, month, day, count)


def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()  # 如果状态不是200，引发HTTPError异常
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "产生异常"


def getTOP_COMMENT_NEWS(from_date, to_date, count):
    """
    获取时间一定时间跨度的每日评论数前count个新闻
    :param from_date: 开始时间
    :param to_date: 结束时间
    :param count:
    :return: 返回news列表
    """
    day_counts = (to_date - from_date).days  # 跨越天数
    now_date = from_date
    one_day = datetime.timedelta(days=1)
    news = []
    for i in range(0, day_counts + 1):
        year = now_date.strftime('%Y-%m-%d')[0:4]
        month = now_date.strftime('%Y-%m-%d')[5:7]
        day = now_date.strftime('%Y-%m-%d')[8:]
        url = getTOP_COMMENT_NEWS_URL(year, month, day, str(count))
        text = json.loads(getHTMLText(url)[11:].replace(';', ''))

        for item in text['normal']:
            news.append(item)
        now_date = now_date + one_day
    return news


def getTOP_CLICK_NEWS(from_date, to_date, count):
    """
    获取时间一定时间跨度的每日点击量前count个新闻
    :param from_date: 开始时间，必须为datetime.datetime对象
    :param to_date: 结束时间，必须为datetime.datetime对象
    :param count: 每日搜集新闻数量
    :return: 返回news的json文件格式的字符串
    """
    day_counts = (to_date - from_date).days  # 跨越天数
    now_date = from_date
    one_day = datetime.timedelta(days=1)
    news = []
    for i in range(0, day_counts + 1):
        year = now_date.strftime('%Y-%m-%d')[0:4]
        month = now_date.strftime('%Y-%m-%d')[5:7]
        day = now_date.strftime('%Y-%m-%d')[8:]
        url = getTOP_CLICK_NEWS_URL(year, month, day, str(count))
        text = json.loads(getHTMLText(url)[11:].replace(';', ''))

        for item in text['normal']:
            news.append(item)
        now_date = now_date + one_day
    return news


def getHOT_COMMENT(channel, news_id):
    """
    根据news_id返回热门评论
    :param channel: 频道
    :param news_id: 新闻id
    :return: 返回热闹评论list
    """
    url = 'http://comment.sina.com.cn/page/info?version=1&format=json&channel={}&newsid={}&group=0&compress=0&ie=gbk&' \
          'oe=gbk&page=1&page_size=100&t_size=3&h_size=100&thread=1&uid=unlogin_user'.format(channel, news_id)
    t = requests.get(url)
    comment = json.loads(t.text)['result']
    if 'hot_list' in comment:
        cmnt = []
        t = {}
        for c in comment['hot_list']:
            t['agree'] = c['agree']
            t['area'] = c['area']
            t['channel'] = c['channel']
            t['content'] = c['content']
            t['nick'] = c['nick']
            t['newsid'] = c['newsid']
            cmnt.append(t)
        return cmnt
    return []


def get_COMMENT(channel, news_id):
    # { "nick": "\u7528\u62377252512274", "newsid": "comos-ihnzhfz9458815"
    """
        根据news_id返回评论
        :param news_id: 新闻id
        :return: 返回热闹评论list
        """
    url = 'http://comment.sina.com.cn/page/info?version=1&format=json&channel={}&newsid={}&group=0&compress=0&ie=gbk&' \
          'oe=gbk&page=1&page_size=100&t_size=3&h_size=100&thread=1&uid=unlogin_user'.format(channel, news_id)
    t = requests.get(url)
    comment = json.loads(t.text)['result']
    if 'cmntlist' in comment:
        cmnt = []
        t = {}
        for c in comment['cmntlist']:
            t['agree'] = c['agree']
            t['area'] = c['area']
            t['channel'] = c['channel']
            t['content'] = c['content']
            t['nick'] = c['nick']
            t['newsid'] = c['newsid']
            cmnt.append(t)
        return cmnt
    return []


def get_Article(url):
    h = getHTMLText(url)
    txt = ""
    try:
        h1 = BeautifulSoup(h, 'html.parser')
        txt = h1.find('div', {'id': re.compile('.*article.*')}).get_text().replace("\n", "")
    except:
        print("错误！")
    return txt


if __name__ == "__main__":
    channels = ['gn', 'gj', 'live', 'cj', 'yl', 'mp', 'sh', 'ty', 'kj', 'survey']
    # hot_comment_count = 158966
    # comment_count = 627770
    # news_count = 18500
    # for item in news[18500:]:
    #     news_count = news_count + 1
    #     url = item['url']
    #
    #     left, right = re.search('/(doc|zl)-i.*', url).span()
    #     news_id = "comos-" + url[left + 6:right-6]
    #     hot_comment_list = []
    #     comment_list = []
    #     for channel in channels:
    #         hot_comment_list = getHOT_COMMENT(channel, news_id)
    #         if len(hot_comment_list) != 0:
    #             break
    #     hot_comment_count = hot_comment_count + len(hot_comment_list)
    #     for k in range(0, len(hot_comment_list)):
    #         hot_comment = hot_comment_list[k]
    #         hot_comment_list[k] = {'agree': hot_comment['agree'], 'area': hot_comment['area'], 'channel': hot_comment['channel'],
    #                        'content': hot_comment['content'], 'nick': hot_comment['nick'], 'newsid': hot_comment['newsid']}
    #     item['hot_comment_list'] = hot_comment_list
    #
    #     for channel in channels:
    #         comment_list = get_COMMENT(channel, news_id)
    #         if len(comment_list) != 0:
    #             break
    #     comment_count = comment_count + len(comment_list)
    #     for k in range(0, len(comment_list)):
    #         comment = comment_list[k]
    #         comment_list[k] = {'agree': comment['agree'], 'area': comment['area'], 'channel': comment['channel'],
    #                        'content': comment['content'], 'nick': comment['nick'], 'newsid': comment['newsid']}
    #     item['comment_list'] = comment_list
    #
    #     print("完成{}/19533, 热门评论{}, 其他评论{}".format(news_count, hot_comment_count, comment_count))
    #     # 每完成250存储一次
    #     if news_count % 250 == 0:
    #         print("存储成功！")
    #         with open('../../dataSets/sina/sina_top_click_news.json', 'w') as f:
    #             json.dump(news, f)

    # with open('../../dataSets/sina/sina_top_click_news.json', 'w') as f:
    #     json.dump(news, f)
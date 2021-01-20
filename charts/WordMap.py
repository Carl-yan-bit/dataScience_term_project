import json
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import cv2


def load_files(path):
    with open(path, 'r') as f:
        return json.load(f)


def divide_by_date(news):
    news_keywords = []
    for new in news:
        news_keywords += new['keywords']
    if len(news_keywords) == 0:
        return "no data"
    news_keywords = word_format(news_keywords)
    return news_keywords


def word_format(words):
    res = list(words)
    for word in words:
        if str(word).isdigit():
            res.remove(word)
        elif str(word).isascii():
            res.remove(word)
    return res


def draw(keywords, date, mas):
    text = " ".join(keywords)
    try:
        text = text.replace("新浪", "")
        text = text.replace("新闻", "")
    except:
        pass
    cloud = WordCloud(
        background_color='white',
        # 设置背景宽
        width=1920,
        font_path="HGKT_CNKI.TTF",
        # 设置背景高
        height=1080,
        mode='RGBA',
        mask=mas
    )
    word_cloud = cloud.generate(text)
    word_cloud.to_file("picture/" + date + ".png")


def show_me(new):
    print('----------')
    print(new['title'])
    print(new['hot_comment_list'])
    print(new['keywords'])


def arrange(news):
    daily = dict()
    monthly = dict()
    news_list = {"daily": daily, "monthly": monthly}
    for year in range(2019, 2021):
        for month in range(1, 13):
            mon = tostr(year) + "-" + tostr(month)
            monLst = []
            for day in range(1, 32):
                date = tostr(year) + "-" + tostr(month) + "-" + tostr(day)
                lst = []
                for new in news:
                    if new["create_date"] == date:
                        lst.append(new)
                        monLst.append(new)
                if len(lst) != 0:
                    daily[date] = lst
            if len(monLst) != 0:
                monthly[mon] = monLst
    return news_list


def tostr(num):
    st = str(num)
    if len(st) == 1:
        st = "0" + st
    return st


def numMap(mode):
    news = arrange(data)
    x_data = news.get(mode).keys()
    y_data = []
    x = []
    for i in x_data:
        y_data.append(len(news.get(mode).get(i)))
        x.append(i[5:])
    plt.figure(figsize=(90, 40))
    plt.plot(x, y_data)
    plt.savefig("picture/" + mode + ".png")


def newsWord(data):
    mask = cv2.imread("picture/mask.png")
    news = arrange(data).get("daily")
    for i in news.keys():
        keywords = divide_by_date(news.get(i))
        if keywords != "no data":
            draw(keywords, i, mask)


def parseComment():
    str = []
    with open("bilibili/bilibili弹幕全集-predicted.csv", 'r', encoding='utf-8') as f:
        temp = f.readline()
        while temp != "":
            temp = temp[:-1]
            str.append(temp)
            temp = f.readline()
    for i in range(0, len(str)):
        str[i] = str[i].split(",")
    return str


def getDailyComment(comments,limit,kind):
    daily = dict()
    if kind == 'b':
        for year in range(2019, 2021):
            month = 1
            while month <= 12:
                day = 1
                while day <= 31:
                    date = tostr(year) + "-" + tostr(month) + "-" + tostr(day)
                    idx = date
                    for i in range(0, limit):
                        lst = []
                        for comment in comments:
                            if comment[0] == date:
                                lst.append(comment)
                        if len(lst) != 0:
                            daily[idx] = lst
                        day += 1
                        date = tostr(year) + "-" + tostr(month) + "-" + tostr(day)
                    if day > 31:
                        month += 1
                        if month > 12:
                            break
                        day -= 31
                        date = tostr(year) + "-" + tostr(month) + "-" + tostr(day)
                    print(date)
        return daily
    for year in range(2019, 2021):
        month = 1
        while month <= 12:
            day = 1
            while day <= 31:
                date = str(year) + "/" + str(month) + "/" + str(day)
                idx = date
                for i in range(0, limit):
                    lst = []
                    for comment in comments:
                        if comment[0] == date:
                            lst.append(comment)
                    if len(lst) != 0:
                        daily[idx] = lst
                    day += 1
                    date = str(year) + "/" + str(month) + "/" + str(day)
                if day > 31:
                    month += 1
                    if month > 12:
                        break
                    day -= 31
                    date = str(year) + "/" + str(month) + "/" + str(day)
                print(date)
    return daily


def getValue(lst, mode, kind):
    sum = 0.0
    times = 0.0
    if kind == 'b':
        if mode == 1:
            mode = 0
        tar = 2
    else:
        tar = 3
    if mode == 0:
        for i in lst:
            if not i[tar].__contains__("."):
                print(i[tar])
                continue
            sum += float(i[tar])
            times += 1
    else:
        for i in lst:
            if not i[2].__contains__("."):
                print(i[2])
                continue
            if not i[3].__contains__("."):
                print(i[2])
                continue
            sum += float(i[3])*max(float(i[2]), 1)
            times += max(float(i[2]), 1)
    return sum/times


def parseMood(dic, mode, limit):
    x_data = dic.keys()
    y_data = []
    print(x_data)
    x = []
    for i in x_data:
        x.append(i[5:])
        y_data.append(getValue(dic.get(i), mode, 'b'))
    plt.figure(figsize=(90, 40))
    plt.plot(x, y_data)
    plt.savefig("picture/" + str(limit) + "commentMood" + str(mode) + ".png")

def comment():
    lst = parseComment()
    day = getDailyComment(lst, 30, 'b')
    print(day.get('2020-03-29'))
    parseMood(day, 0, 30)


if __name__ == '__main__':
    data = load_files(path="sina/新浪所有排行新闻.json")
    mask = cv2.imread("picture/mask.png")
    keywords = []
    for new in data:
        for i in new['keywords']:
            keywords.append(i)
    draw(keywords, 'all', mask)

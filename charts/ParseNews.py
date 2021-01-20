import json

from pyecharts.charts import Pie
from pyecharts import options
from pyecharts.charts import Page
from pyecharts.charts import Bar
from pyecharts.charts import Line
from pyecharts.charts import Bar3D
from pyecharts.faker import Faker


def load_files(path):
    with open(path, 'r') as f:
        return json.load(f)


def arrangeByTime(news):
    daily = dict()
    monthly = dict()
    days = dict()
    news_list = {"daily": daily, "monthly": monthly, "days": days}
    times = 0
    day3 = []
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
                        day3.append(new)
                times += 1
                if times == 3:
                    if len(day3) != 0:
                        days[date] = day3
                    day3 = []
                    times = 0
                if len(lst) != 0:
                    daily[date] = lst
            if len(monLst) != 0:
                monthly[mon] = monLst
    return news_list


def arrangeByChannel(news):
    channel = dict()
    for new in news:
        if new['channel'] not in channel.keys():
            channel[new['channel']] = []
            channel[new['channel']].append(new)
        else:
            channel[new['channel']].append(new)
    return channel


def tostr(num):
    st = str(num)
    if len(st) == 1:
        st = "0" + st
    return st


def trans(labels):
    for i in range(0, len(labels)):
        labels[i] = tran(labels[i])
    return labels


def tran(key):
    dic = {'gn': '国内', 'sh': '社会', 'ty': '体育', 'mp': '看点', 'live': '直播', 'cj': '财经', 'kj': '科技', 'gj': '国际'
        , 'yl': '娱乐', 'jc': '军事', 'js': '江苏', 'jilin': '吉林', 'video': '视频'}
    return dic.get(key)


def drawCycle(dic):
    # page = Page()
    pie = Pie()
    pie.set_global_opts(title_opts=options.TitleOpts(title="新浪新闻主题", pos_top='55'))
    a = []
    for i in dic.keys():
        a.append((tran(i), len(dic.get(i))))
    pie.add('总数', a)
    # page.add(pie)
    # page.page_title = "新浪新闻主题分布"
    # page.render("NewPage/主题分布.html")
    return pie


def divideComment(news):
    comment = []
    for new in news:
        comment += new['hot_comment_list']
    return comment


def getMood(comments, mode):
    mood = dict()
    for i in comments.keys():
        sum = 0
        times = 0
        if len(comments.get(i)) == 0:
            continue
        for j in comments.get(i):
            if mode == 0:
                temp = str(j['sentiment'])
                if not temp.__contains__("."):
                    continue
                times += 1
                sum += float(temp)
            else:
                temp = str(j['sentiment'])
                if not temp.__contains__("."):
                    continue
                agree = str(j['agree'])
                if not agree.isdigit():
                    continue
                times += max(int(agree), 1)
                sum += float(temp) * max(int(agree), 1)
        mood[i] = str.format("{:.3f}", sum / times)
    return mood


def numMap(data):
    x_data = data.keys()
    y_data = []
    for i in x_data:
        y_data.append(data.get(i))
    bar = Bar()
    bar.add_xaxis(trans(list(x_data)))
    bar.add_yaxis("评论情感", y_data)
    # bar.render("NewPage/评论平均情感.html")
    bar.set_global_opts(title_opts=options.TitleOpts(title="评论平均情感", pos_top='55'))
    return bar


def drawChannelMotion(news):
    comment_channel = dict()
    for i in news.keys():
        comment_channel[i] = divideComment(news.get(i))
    numMap(getMood(comment_channel, 0))


def drawDailyNewsNum(news, mode):
    line = Line()
    line.add_xaxis(list(news.get(mode).keys()))
    y = []
    for i in news.get(mode).keys():
        y.append(len(news.get(mode).get(i)))
    line.add_yaxis("新闻数量", y_axis=y)
    # line.render("NewPage/新闻每月数.html")
    line.set_global_opts(title_opts=options.TitleOpts(title=titleTransform("新浪新闻" + str(mode) + "数量"), pos_top='55'))
    return line


def parseComment(path):
    str = []
    with open(path, 'r', encoding='utf-8') as f:
        temp = f.readline()
        while temp != "":
            temp = temp[:-1]
            str.append(temp)
            temp = f.readline()
    for i in range(0, len(str)):
        str[i] = str[i].split(",")
    return str


def getDailyComment(comments, limit, kind):
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
            sum += float(i[3]) * max(float(i[2]), 1)
            times += max(float(i[2]), 1)
    return str.format("{:.3f}", sum / times)


def parseMood(dic, mode, limit, port):
    x_data = dic.keys()
    y_data = []
    print(x_data)
    x = []
    for i in x_data:
        x.append(i[5:])
        y_data.append(getValue(dic.get(i), mode, port))
    line = Line()
    if port == 'b':
        port = 'B站'
    else:
        port = '新浪'
    line.add_xaxis(x).add_yaxis("情感变化", y_data, )
    # line.render("NewPage/" + str(mode) + "评论情感每" + str(limit) + "天.html")
    line.set_global_opts(title_opts=options.TitleOpts(title=titleTransform(port+"评论情感每" + str(limit) + "天"), pos_top='55'))
    return line


def bilibili_comment():
    lst = parseComment("bilibili/bilibili弹幕全集-predicted.csv")
    # for j in range(0, 2):
    pie = []
    for i in [1, 3, 7, 30]:
        day = getDailyComment(lst, i, 'b')
        pie.append(parseMood(day, 0, i, 'b'))
    return pie

def sina_all_comment():
    lst = parseComment("sina/新浪所有排行新闻评论全集-predicted.csv")
    pie = []
    for i in [1, 3, 7, 30]:
        day = getDailyComment(lst, i, 's')
        pie.append(parseMood(day, 1, i, 's'))
    return pie


def sina_comment(data, mode, time):
    line = Line()
    temp = list(arrangeByTime(data).get(time).keys())
    line.add_xaxis(temp)
    data = arrangeByChannel(data)  # 按频道分
    news = dict()
    for i in data.keys():
        news[i] = arrangeByTime(data.get(i)).get(time)
    value = dict()
    comment_channel = dict()
    for i in news.keys():
        comment_channel[i] = dict()
        value[i] = dict()
        for j in news[i].keys():
            comment_channel[i][j] = divideComment(news[i].get(j))
        value[i] = getMood(comment_channel[i], mode)
    for i in value.keys():
        y = []
        for j in temp:
            if j in value.get(i).keys():
                y.append(value.get(i).get(j))
            else:
                y.append(None)
        if i not in ['js', 'jilin', 'video', 'live']:
            line.add_yaxis(tran(i), y, is_connect_nones=True, is_symbol_show=(time == 'monthly'))
    # line.render("NewPage/无权每月评论.html")
    line.set_global_opts(title_opts=options.TitleOpts(title=titleTransform("新浪新闻评论"+str(mode) + str(time) + "评论情感分析"), pos_top='55'))
    return line


def commentChannel(data, time):
    line = Line()
    temp = list(arrangeByTime(data).get(time).keys())
    line.add_xaxis(temp)
    data = arrangeByChannel(data)  # 按频道分
    news = dict()
    for i in data.keys():
        news[i] = arrangeByTime(data.get(i)).get(time)
    comment_channel = dict()
    for i in news.keys():
        comment_channel[i] = dict()
        for j in news[i].keys():
            comment_channel[i][j] = divideComment(news[i].get(j))
    for i in comment_channel.keys():
        y = []
        for j in temp:
            if j in comment_channel.get(i).keys():
                y.append(len(comment_channel.get(i).get(j)))
            else:
                y.append(None)
        if i not in ['js', 'jilin', 'video', 'live']:
            line.add_yaxis(tran(i), y, is_connect_nones=True, is_symbol_show=(time == 'monthly'))
    # line.render("NewPage/无权每月评论.html")
    line.set_global_opts(title_opts=options.TitleOpts(title=titleTransform("新浪新闻评论"+str(time) + "评论数量"), pos_top='55'))
    return line


def titleTransform(title):
    title = str(title)
    title = title.replace("daily", "每天").replace("days", "每十二天").replace("monthly", "每月").replace("1天", "天").replace("30天", "月").replace("0", "无点赞权重").replace("1", "")
    return title


def drawThreeD(data, mode, time):
    bar3d = Bar3D()
    temp = list(arrangeByTime(data).get(time).keys())
    res = []
    data = arrangeByChannel(data)  # 按频道分
    news = dict()
    for i in data.keys():
        news[i] = arrangeByTime(data.get(i)).get(time)
    value = dict()
    comment_channel = dict()
    for i in news.keys():
        comment_channel[i] = dict()
        value[i] = dict()
        for j in news[i].keys():
            comment_channel[i][j] = divideComment(news[i].get(j))
        value[i] = getMood(comment_channel[i], mode)
    for i in value.keys():
        if i in ['js', 'jilin', 'video', 'live']:
            continue
        if len(value.get(i))==0:
            continue
        for j in temp:
            if j in value.get(i).keys():
                res.append((tran(i), j, value.get(i).get(j)))
            else:
                res.append((tran(i), j, None))
    bar3d.add(
        "",
        [[d[1], d[0], d[2]] for d in res],
    ).set_global_opts(
        visualmap_opts=options.VisualMapOpts(max_=1),
        title_opts=options.TitleOpts(title="时间、维度与新浪评论情感总图"),
    )
    return bar3d

    #for i in value.keys():
    #    y = []
    #    for j in temp:
    #        if j in value.get(i).keys():
    #            y.append(value.get(i).get(j))
    #        else:
    #            y.append(None)
    #    if i not in ['js', 'jilin', 'video', 'live']:
    #        line.add_yaxis(tran(i), y, is_connect_nones=True, is_symbol_show=(time == 'monthly'))
    ## line.render("NewPage/无权每月评论.html")
    #line.set_global_opts(
    #    title_opts=options.TitleOpts(title=titleTransform("新浪新闻评论" + str(mode) + str(time) + "评论情感分析"), pos_top='55'))
    #return line


if __name__ == '__main__':
    data = load_files(path="sina/新浪所有新闻-predicted.json")
    page = Page()
    news = arrangeByTime(data)  # 按时间分
    news1 = arrangeByChannel(data)  # 按频道分
    # ----------  以上是固定代码
    page.add(drawCycle(news1))
    page.add(drawDailyNewsNum(news, 'daily'))
    page.add(drawDailyNewsNum(news, 'monthly'))
    #page.add(sina_comment(data, 0, 'daily'))
    page.add(sina_comment(data, 1, 'daily'))
    #page.add(sina_comment(data, 0, 'monthly'))
    page.add(sina_comment(data, 1, 'monthly'))
    #page.add(sina_comment(data, 0, 'days'))
    page.add(sina_comment(data, 1, 'days'))
    page.add(commentChannel(data, 'monthly'))
    page.add(commentChannel(data, 'daily'))
    temp = bilibili_comment()
    for i in temp:
        page.add(i)
    for i in page:
        i.width = "1800px"
    temp = sina_all_comment()
    for i in temp:
        page.add(i)
    page.add(drawThreeD(data, 1, 'monthly'))
    for i in page:
        i.width = "1800px"
    page.render()


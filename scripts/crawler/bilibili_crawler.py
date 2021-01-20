import requests
from bs4 import BeautifulSoup
import json
import datetime
import time


def getHTMLText(url):
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()  # 如果状态不是200，引发HTTPError异常
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "产生异常"


def getComment_Interface_url(page, oid):
    """
    给定页码，视频av号，返回视频评论接口
    :param page: 页码
    :param oid: av号
    :return: 视频评论接口url
    """
    return "https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn={}&type=1&oid={}&sort=2".format(page, oid)


def getUP_VIDEO_Interface_url(UID, page, ps):
    """
    给定UP主UID,页码，每页显示数视频数
    :param UID:UP主UID
    :param page:页码
    :param ps:每页显示视频数
    :return:UP主投稿视频接口url
    """
    return "https://api.bilibili.com/x/space/arc/search?mid={}&pn={}&ps={}".format(UID, page, ps)


def tickToDate(time_tick):
    """
    将时间戳转换为年月日
    :param time_tick: 时间戳字符串
    :return: 日期 例：2020-11-06
    """
    time_array = time.localtime(int(time_tick))
    return time.strftime("%Y-%m-%d", time_array)


def getVideo_and_Comment(from_date, to_date, uid):
    """
    爬取uid对应UP主从from_date到to_date投稿的视频的链接和评论
    :param from_date: 起始日期
    :param to_date: 终止日期
    :param uid: UP主uid
    :return: 数据
    """
    data_sets = []  # 存储数据集
    vide_count = 0
    hots_comment_count = 0
    comment_count = 0
    page = 1
    while True:
        # 循环增加
        up_video_list = json.loads(getHTMLText(getUP_VIDEO_Interface_url(uid, page, 100)))["normal"]["list"]["vlist"]
        if len(up_video_list) == 0:
            print("UP没有视频了！")
            break
        for video in up_video_list:
            pub_time = datetime.datetime.strptime(tickToDate(video['created']), "%Y-%m-%d")
            if pub_time < from_date:
                print("超过指定日期范围！自动结束！")
                return data_sets
            if from_date <= pub_time <= to_date:  # 在指定日期内
                # 爬取评论
                comment_url = getComment_Interface_url(1, video['aid'])
                try:
                    t1 = json.loads(getHTMLText(comment_url))
                except:
                    print("错误！")
                    continue
                if 'normal' in t1:
                    print("有数据")
                    t = t1['normal']
                else:
                    print("没有数据")
                    continue
                hots_comment_list = t['hots']
                if hots_comment_list is None:
                    hots_comment_list = []
                hots_comment_count = hots_comment_count + len(hots_comment_list)
                comment_list = t['replies']
                if comment_list is None:
                    comment_list = []
                comment_count = comment_count + len(comment_list)
                # 清理无用数据项
                for i in range(0, len(hots_comment_list)):
                    t = hots_comment_list[i]
                    hots_comment_list[i] = {'rcount': t['rcount'], 'ctime': t['ctime'], 'like': t['like'], 'message':
                        t['content']['message']}
                for i in range(0, len(comment_list)):
                    t = comment_list[i]
                    comment_list[i] = {'rcount': t['rcount'], 'ctime': t['ctime'], 'like': t['like'], 'message':
                        t['content']['message']}
                video['hots_comment_list'] = hots_comment_list
                video['comment_list'] = comment_list

                # 将评论加入video
                video = {'comment': video['comment'], 'play': video['play'], 'description': video['description'],
                         'title': video['title'], 'author': video['author'], 'created': tickToDate(video['created']),
                         'aid': video['aid'], 'bvid': video['bvid'], 'hots_comment_list': video['hots_comment_list'],
                         'comment_list': video['comment_list']}
                data_sets.append(video)
                vide_count = vide_count + 1
                print("视频数：{}, 热门评论数：{}, 评论数：{}, 日期：{}, 视频名称：{}".format(vide_count, hots_comment_count, comment_count,
                                                                        pub_time, video['title']))
        page = page + 1
    return data_sets


def getVIDEO_CID(aid):
    try:
        url = "https://www.bilibili.com/widget/getPageList?aid={}".format(aid)
        res = json.loads(getHTMLText(url))
        return res[0]['cid']
    except:
        print('返回cid失败!')
        return "error"


def static_count(uid_map):
    """
    统计爬取数据
    :param uid_map: 传入uid_map
    :return:
    """
    total_video_count = 0
    total_hot_comment_count = 0
    total_comment_count = 0

    for key in uid_map:
        with open('../../dataSets/bilibili/{}.json'.format(key), 'r') as f:
            data_sets = json.load(f)
            video_count = len(data_sets)
            hot_comment_count = 0
            comment_count = 0
            for item in data_sets:
                hot_comment_count = hot_comment_count + len(item['hots_comment_list'])
                comment_count = comment_count + len(item['comment_list'])
            print("{}: 视频数：{}, 热门评论数：{}, 评论数: {}".format(key, video_count, hot_comment_count, comment_count))
            total_video_count = total_video_count + video_count
            total_hot_comment_count = total_hot_comment_count + hot_comment_count
            total_comment_count = total_comment_count + comment_count
    print("全部：视频数：{}，热门评论数：{}, 评论数: {}".format(total_video_count, total_hot_comment_count, total_comment_count))


def getBullet_Comment(cid):
    """
    给定cid,返回弹幕的.xml文件
    :param cid: 视频cid
    :return: .xml文件
    """
    res = getHTMLText("http://comment.bilibili.com/{}.xml".format(cid))
    return res


def crawler(uid_map):
    total_bullet_count = 0
    for key in uid_map:
        bullet_count = 0
        print("正在获取{}-账号的弹幕".format(key))
        with open('../../dataSets/bilibili/{}.json'.format(key), 'r') as f:
            data = json.load(f)
        for i in range(0, len(data)):
            time.sleep(2)
            item = data[i]
            print("正在获取{}的弹幕 {}".format(item['title'], item['created']))
            cid = getVIDEO_CID(item['aid'])
            if cid == "error":
                continue
            raw_bullet_comment = getBullet_Comment(cid)
            soup = BeautifulSoup(raw_bullet_comment, 'xml').find_all('d')
            bullet_comments = []
            for c in soup:
                bullet_comments.append(c.get_text())
            item['bullet_comments'] = bullet_comments
            bullet_count = bullet_count + len(bullet_comments)
            total_bullet_count = total_bullet_count + len(bullet_comments)
            print("搜集弹幕{}, 累计{}".format(len(bullet_comments), total_bullet_count))
            data[i] = item

        print("{}共搜集弹幕{}, 累计{}".format(key, bullet_count, total_bullet_count))
        with open('../../dataSets/bilibili/{}.json'.format(key), 'w') as f:
            json.dump(data, f)
    print("弹幕总计：{}".format(total_bullet_count))


if __name__ == "__main__":
    uid_map = {"共青团中央": "20165629", "央视新闻": "456664753", "小央视频": "222103174", "中国日报": "21778636", "新华社":
        "473837611", "人民网": "33775467", "央视频": "433587902", "光明日报": "404414222", "央视网快看": "451320374",
               "观察者网": "10330740", "观视频工作室": "54992199", "环球时报": "10303206", "人民视频": "386265385",
               "广东共青团": "330383888", "浙江共青团": "384298638", "河南共青团": "323194278",
               "安徽共青团": "268810504", "湖南共青团": "43563506", "福建共青团": "28897026", "重庆共青团": "212375551",
               "四川共青团": "483940995", "贵州共青团": "452215100", "江西共青团": "109586062", "江苏共青团": "543191732",
               "云南共青团": "285216473"}  # UP主UID

    # from_date = datetime.datetime.strptime("2019-12-08", "%Y-%m-%d")
    # to_date = datetime.datetime.strptime("2020-6-20", "%Y-%m-%d")

    # for key in uid_map:
    #     # print("正在搜集{}视频".format(key))
    #     # data_sets = getVideo_and_Comment(from_date, to_date, uid_map[key])
    #     with open('../../dataSets/bilibili/{}.json'.format(key), 'r') as f:
    #         normal = json.load(f)
    #
    #
    #     with open('../../dataSets/bilibili/{}.json'.format(key), 'w') as f:
    #         json.dump(data_sets, f)
    #     print("{}视频搜集完成！".format(key))

    # print(getVIDEO_CID("498617621"))
    # static_count(uid_map)

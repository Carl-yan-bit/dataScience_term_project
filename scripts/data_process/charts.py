import json


if __name__ == "__main__":
    with open('../../dataSets/sina/新浪所有新闻-predicted.json', 'r') as f:
        sina_news = json.load(f)

    date = []
    keywords = {}
    for news in sina_news:
        if news['create_date'] not in date:
            date.append(news['create_date'])
        for keyword in news['keywords']:
            if keyword not in keywords:
                keywords[keyword] = 1
            else:
                keywords[keyword] += 1

    csv_file = "关键词,"
    for d in date:
        csv_file += d + ','
    csv_file = csv_file[0: -1]
    csv_file += '\n'
    count = 0
    filter_keywords = {}
    for i in keywords:
        if keywords[i] >= 100 and not i.isdigit() and not i == "责任编辑" and not i == 'SINA' or i == '2020':
            # count += 1
            print("{}:{}".format(i, keywords[i]))
            filter_keywords[i] = {}

    # print("统计{}".format(count))
    # print(len(filter_keywords))

    for news in sina_news:
        for k in filter_keywords:
            if news['create_date'] not in filter_keywords[k]:
                filter_keywords[k][news['create_date']] = 0

        for keyword in news['keywords']:
            if keyword in filter_keywords:
                filter_keywords[keyword][news['create_date']] += 1

    for word in filter_keywords:
        # print(word)
        csv_file += word + ','
        for date in filter_keywords[word]:
            # print("{}:{}".format(date, filter_keywords[word][date]))
            total_count = 0
            for d in filter_keywords[word]:
                if d != date:
                    total_count += filter_keywords[word][d]
                else:
                    total_count += filter_keywords[word][d]
                    break
            csv_file += str(total_count) + ','
        csv_file = csv_file[0: -1]
        csv_file += '\n'

    with open('../../dataSets/sina/关键词累计统计.csv', 'w') as f:
        f.write(csv_file)
import requests as rq
from bs4 import BeautifulSoup
import re
import datetime

html_list = []
title_list = []
content_list = []
date_list = []


def parse(keyword: list, ty: (datetime, datetime)):
    search_string = "https://www.chinatimes.com/search/"
    if_no_url = "NO_URL"
    if_no_context = "找不到相符結果"
    if keyword:
        for ele in keyword:
            search_string = search_string + ele + "%20"
        for i in range(1, 6):
            # get connect
            url = search_string + "?page" + str(i)
            response = rq.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            sel = soup.find("span", "search-result-count").text
            if sel == "00":
                break
            sel = soup.select("h3.title a")
            # get_html
            for ele in sel:
                html_list.append(ele["href"])

            # get date
            s = ""
            for ele in soup.select("span.date"):
                s += ele.text + " 00:00"
                date_list.append(s)
                s = ""

            # get_context
            sel = soup.select("p.intro")
            for ele in sel:
                content_list.append(ele.text)

            for j in range(0, len(date_list)):
                date = datetime.datetime.strptime(str(date_list[j]), '%Y/%m/%d %H:%M')
                if ty[0] <= date <= ty[1]:
                    content_list[j] = re.sub('[a-zA-Z]', '', content_list[j])
                    return [html_list[j], content_list[j].replace(u'\u3000', u' ').replace('\n', '')]
            if i == 1:
                if_no_url = html_list[0]
                content_list[0] = re.sub('[a-zA-Z]', '', content_list[j])
                if_no_context = content_list[0].replace(u'\u3000', u' ').replace('\n', '')
            html_list.clear()
            date_list.clear()
            content_list.clear()
    else:
        html_string = ""
        content_string = ""
        url = "https://www.chinatimes.com/hotnews/?chdtv"
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sel = soup.find_all("h3", "title", limit=3)
        for ele in sel:
            e = ele.find("a")
            html_string += e["href"]
            if ele != sel[-1]:
                html_string += "\n"
        sel = soup.find_all("p", "intro", limit=3)
        for ele in sel:
            content_string += ele.text.replace(u'\u3000', u' ').replace('\n', '')
            if ele != sel[-1]:
                content_string += "\n"
        content_string = re.sub('[a-zA-Z]', '', content_string)
        return [html_string, content_string]
    return [if_no_url, if_no_context]


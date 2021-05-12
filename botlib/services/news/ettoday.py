import requests as rq
from bs4 import BeautifulSoup
import re
import datetime

html_list = []
title_list = []
content_list = []
date_list = []


def parse(keyword: list, ty: (datetime, datetime)):
    if_no_url = "NO_URL"
    if_no_context = "找不到相符結果"
    search_string = "https://www.ettoday.net/news_search/doSearch.php?search_term_string="
    if keyword:
        for ele in keyword:
            search_string = search_string + ele + "+"
        for i in range(1, 6):
            # get connect
            url = search_string + "&page=" + str(i)
            response = rq.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            sel = soup.find("p", "info").text
            current_page = sel[1:sel.find("頁",0,len(sel))]
            total_page   = sel[sel.find("共",0,len(sel))+1:len(sel)-1]
            if int(total_page) == 0 or int(total_page) < int(current_page):
                break

            # get_html
            sel = soup.select("div.box_2 h2 a")
            for ele in sel:
                html_list.append(ele["href"])

            # get_date
            for ele in soup.select("span.date"):
                date_text = str(ele.text)
                date_text = date_text[date_text.find("/")+2:len(date_text)-1]
                date_list.append(date_text)

            # get_context
            for ele in soup.find_all("p", "detail"):
                w = ele.find("span").text
                content_list.append(ele.text[:len(ele.text)-len(w)])

            for j in range(0, len(date_list)):
                date = datetime.datetime.strptime(str(date_list[j]), '%Y-%m-%d %H:%M')
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
        url = "https://www.ettoday.net/news/hot-news.htm"
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sel = soup.find_all("div", "piece clearfix", limit=3)
        for ele in sel:
            e = ele.find("a")
            html_string += "https://www.ettoday.net" + e["href"]
            if ele != sel[-1]:
                html_string += "\n"
        sel = soup.find_all("p", "summary", limit=3)
        for ele in sel:
            content_string += ele.text.replace(u'\u3000', u' ').replace('\n', '')
            if ele != sel[-1]:
                content_string += "\n"
        content_string = re.sub('[a-zA-Z]', '', content_string)
        return [html_string, content_string]

    return [if_no_url, if_no_context]


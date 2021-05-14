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
    search_string = "https://search.ltn.com.tw/list?keyword="
    if keyword:
        for ele in keyword:
            search_string = search_string + ele + "+"
        for i in range(1, 6):
            # get connect
            url = search_string + "&page=" + str(i)
            response = rq.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            sel = soup.find("div", "mark").text
            sel = sel[sel.find("有", 0, len(sel))+2:sel.find("項", 0, len(sel))-1]
            if int(sel) == 0:
                break

            # get_html
            sel = soup.select("a.tit")
            for ele in sel:
                html_list.append(ele["href"])

            # get_date
            sel = soup.select("span.time")
            for ele in sel:
                date_text = ele.text
                if "分鐘" in date_text:
                    real_date = datetime.datetime.now().strftime('%Y/%m/%d %H:%M')
                elif "小時" in date_text:
                    now_time = date_text[0:date_text.find("小")]
                    real_date = (datetime.datetime.now() - datetime.timedelta(hours=float(now_time))).strftime('%Y/%m/%d %H:%M')
                elif "天" in date_text:
                    now_time = date_text[0:date_text.find("天")]
                    real_date = (datetime.datetime.now() - datetime.timedelta(days=float(now_time))).strftime('%Y/%m/%d %H:%M')
                else:
                    real_date = date_text + " 00:00"
                date_list.append(real_date)

            # get_context
            sel = soup.select("div.cont p")
            for ele in sel:
                content_list.append(ele.text)

            for j in range(0, len(date_list)):
                date = datetime.datetime.strptime(str(date_list[j]), '%Y/%m/%d %H:%M')
                if ty[0] <= date <= ty[1]:
                    content_list[j] = re.sub('[a-zA-Z]', '', content_list[j])
                    content_list[j] = content_list[j].replace(u'\u3000', u' ').replace('\n', '')
                    if content_list[j].find("。"):
                        content_list[j] = content_list[j][:content_list[j].find("。")]
                    elif len(content_list[j]) > 50:
                        content_list[j] = content_list[j][:50]
                    return [html_list[j], content_list[j]]
            if i == 1:
                if_no_url = html_list[0]
                content_list[0] = re.sub('[a-zA-Z]', '', content_list[0])
                if_no_context = content_list[0].replace(u'\u3000', u' ').replace('\n', '')
                if if_no_context.find("。"):
                    if_no_context = if_no_context[:if_no_context.find("。")]
                elif len(if_no_context) > 50:
                    if_no_context = if_no_context[:50]
            html_list.clear()
            date_list.clear()
            content_list.clear()
    else:
        html_string = ""
        content_string = ""
        url = "https://news.ltn.com.tw/list/breakingnews/popular"
        response = rq.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        sel = soup.find_all("a", "tit", limit=3)
        for ele in sel:
            te = ""
            html_string += ele["href"]
            url = ele["href"]
            response = rq.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            se = soup.select("div.text")
            for el in se:
                te += el.text
            te = te.replace(u'\u3000', u' ').replace('\n', '')
            if te.find("〔"):
                te = te[te.find("〔"):te.find("〔")+40]
            else:
                te = te[0:40]
            content_string += te
            if ele != sel[-1]:
                content_string += "\n"
                html_string += "\n"
        content_string = re.sub('[a-zA-Z]', '', content_string)
        return [html_string, content_string]

    return [if_no_url, if_no_context]

from enum import Enum
import datetime

# project libs
from botlib import BotConfig
from botlib.botlogger import BotLogger
from botlib.converter.datetime_converter import DatetimeConverter

# import crawler
from botlib.services.news import udn, chinatimes, ltn, tvbs, ettoday, ncku, setn



class AvailableMedia(Enum) :
    """
    Available Media Enumeration
    """
    NCKU = "成大新聞"
    LTN = "自由時報"
    CHINATIME = "中時電子報"
    TVBS = "TVBS新聞網"
    ETTODAY = "東森ETToday新聞雲"
    UDN = "聯合報"
    SETN = "三立新聞"


# ------------------------------------------------------------------------------------------------------------

def simplify_news_content( content: str ) -> str :
    # SAMPLE : use only first 30 words
    return content[:30]


def search_news( time_range: (datetime, datetime), keywords: list, media: AvailableMedia ) -> [str, str] :
    """

    :param time_range:
    :param keywords:
    :param media:
    :return: [url, text]
    """

    if media == AvailableMedia.UDN :
        result = udn.parse(keywords, time_range)
    elif media == AvailableMedia.LTN :
        result = ltn.parse(keywords, time_range)
    elif media == AvailableMedia.CHINATIME :
        result = chinatimes.parse(keywords, time_range)
    elif media == AvailableMedia.ETTODAY :
        result = ettoday.parse(keywords, time_range)
    elif media == AvailableMedia.TVBS :
        result = tvbs.parse(keywords, time_range)
    elif media == AvailableMedia.NCKU :
        result = ncku.parse(keywords, time_range)
    elif media == AvailableMedia.SETN :
        result = setn.parse(keywords, time_range)
    else :
        result = ["NO_URL", "無法判斷新聞媒體"]  # SAMPLE RESPONSE FORMAT

    BotLogger.debug(f""" Search News :
        Time Range  = {time_range.__str__()},
        Keywords    = {keywords.__str__()},
        Media       = {media.value}
        Result      = {result}""")

    return result


if __name__ == '__main__' :
    time_range = DatetimeConverter.extract_datetime("三天前的新聞")
    keywords = []

    res = search_news(time_range, keywords, AvailableMedia.CHINATIME)

    links = res[0].split("\n")
    texts = res[1].split("\n")

    print(links)
    print(texts)
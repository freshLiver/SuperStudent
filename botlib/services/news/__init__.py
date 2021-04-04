from enum import Enum
import datetime

# project libs
from botlib import BotConfig
from botlib.botlogger import BotLogger

# import crawler
from botlib.services.news import udn
from botlib.services.news import chinatimes
from botlib.services.news import ltn
from botlib.services.news import tvbs
from botlib.services.news import ettoday



class AvailableMedia(Enum) :
    """
    Available Media Enumeration
    """

    NCKU = "成大新聞",
    LTN = "自由時報",
    CHINATIME = "中時電子報",
    TVBS = "TVBS新聞網",
    ETTODAY = "東森ETToday新聞雲",
    UDN = "聯合報"


# ------------------------------------------------------------------------------------------------------------


def search_news( time_range: (datetime, datetime), keywords: list, media: AvailableMedia ) -> str :
    """
    
    :param time_range:
    :param keywords:
    :param media:
    :return:
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
    # DEBUG
    BotLogger.debug(time_range)
    BotLogger.debug(keywords.__str__())
    BotLogger.debug(media.value)

    # TODO call target news crawler and get result
    return result
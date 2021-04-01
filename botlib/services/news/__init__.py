from enum import Enum
import datetime

# project libs
from botlib import BotConfig
from botlib.botlogger import BotLogger



class AvailableMedia(Enum) :
    """
    Available Media Enumeration
    """

    NCKU = "成大新聞",
    LTN = "自由時報",
    CHINATIME = "中時電子報",
    TVBS = "TVBS新聞網",
    ETTODAY = "ETtoday新聞雲",
    UDN = "聯合報"


# ------------------------------------------------------------------------------------------------------------


def search_news( time_range: (datetime, datetime), keywords: list, media: AvailableMedia ) -> str :
    """
    
    :param time_range:
    :param keywords:
    :param media:
    :return:
    """

    # DEBUG
    BotLogger.debug(time_range)
    BotLogger.debug(keywords.__str__())
    BotLogger.debug(media.value)

    # TODO call target news crawler and get result
    return "查詢新聞"
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
    CHINATIME = "中時電子報"


# ------------------------------------------------------------------------------------------------------------


def find_news( time_range: (datetime, datetime), keywords: list, media: AvailableMedia ) -> str :
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
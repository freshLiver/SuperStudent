from enum import Enum
import datetime



class AvailableMedia(Enum) :
    """
    Available Media Enumeration
    """

    NCKU = 0,
    CHINATIME = 1


# ------------------------------------------------------------------------------------------------------------


def find_news( time_range: (datetime, datetime), keywords: list, media: AvailableMedia ) -> str :
    """
    
    :param time_range:
    :param keywords:
    :param media:
    :return:
    """

    # TODO call target news crawler and get result
    return "查詢新聞"
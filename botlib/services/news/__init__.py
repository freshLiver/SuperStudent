from enum import Enum


class AvailableMedia(Enum) :
    """
    Available Media Enumeration
    """

    NCKU = 0,
    CHINATIME = 1


def find_news( datetime: str, keywords: list, media: AvailableMedia ) -> str :
    """
    
    :param datetime:
    :param keywords:
    :param media:
    :return:
    """

    # TODO call target news crawler and get result
    return "Find News()"
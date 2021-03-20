from enum import Enum

# project libs
from botlib.botlogger import BotLogger
from botlib.services import news, database


class Services(Enum) :
    UNKNOWN = -1
    NEWS = 0
    ACTIVITY = 1


# ------------------------------------------------------------------------------------------------------------

def __parse_datetime( datetime: list ) -> str or None :
    # TODO combine all datetime info to str
    return ""


def __choose_media( proper_nouns: list ) -> news.AvailableMedia :
    """
    Find Media From pnList From NER Result
    
    :param proper_nouns: pnList from ner info
    :return: news.AvailableMedia (default media is news.AvailableMedia.NCKU)
    """

    # TODO find available media from pn List
    if "中時" in proper_nouns :
        return news.AvailableMedia.CHINATIME

    return news.AvailableMedia.NCKU


def service_matching( analyzer: 'SemanticAnalyer' ) -> str :
    """
    Choose Service Via Semantic Analyzed Result Info
    
    :param analyzer: Semantic Analyzer
    :return: request response
    """

    # choose target service with analyzer.target_service
    if analyzer.target_service == Services.UNKNOWN :
        BotLogger.log_info("Unknown Request")
        return "非常抱歉，我聽不懂您的需求"

    elif analyzer.target_service == Services.NEWS :

        # convert raw ner info into news service info
        datetime = __parse_datetime(analyzer.service_info['Datetime'])
        keywords = analyzer.service_info
        media = __choose_media(analyzer.service_info['ProperNouns'])

        BotLogger.log_info("News Request")
        return news.find_news(datetime, keywords, media)

    elif analyzer.target_service == Services.ACTIVITY :

        BotLogger.log_info("Activity Request")

    else :
        BotLogger.log_critical("Service Matching Error. Should Not Be Here.")
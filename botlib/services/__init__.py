from enum import Enum

# project libs
from botlib.botlogger import BotLogger
from botlib.services import news, activity



class Services(Enum) :
    UNKNOWN = -1
    NEWS = 0
    ACTIVITY = 1


# ------------------------------------------------------------------------------------------------------------


def __extract_media( proper_nouns: list ) -> news.AvailableMedia :
    """
    Find Media From pnList From NER Result
    
    :param proper_nouns: pnList from ner info
    :return: news.AvailableMedia (default media is news.AvailableMedia.NCKU)
    """

    # TODO find available media from pn List
    if "中時" in proper_nouns :
        return news.AvailableMedia.CHINATIME

    # default NCKU news
    return news.AvailableMedia.NCKU


def service_matching( analyzer: 'SemanticAnalyzer' ) -> str :
    """
    Choose Service Via Semantic Analyzed Result Info
    
    :param analyzer: Semantic Analyzer
    :return: request response
    """

    # choose target service with analyzer.target_service
    if analyzer.target_service == Services.UNKNOWN :
        BotLogger.info("Unknown Request")
        return "非常抱歉，我聽不懂您的需求"


    elif analyzer.target_service == Services.NEWS :
        # convert raw ner info into news service param format
        time_range = analyzer.time_range
        keywords = analyzer.obj_list
        available_media = __extract_media(analyzer.pn_list)

        BotLogger.info("News Request")
        return news.find_news(time_range, keywords, available_media)


    elif analyzer.target_service == Services.ACTIVITY :
        # convert raw ner info into activity param format
        people = analyzer.pn_list
        events = analyzer.events
        time_range = analyzer.time_range
        location = analyzer.locations

        # TODO : find activity or create activity
        BotLogger.info("Activity Request")
        return activity.find_activity(people, events, time_range, location)

    else :
        BotLogger.critical("Service Matching Error. Should Not Be Here.")
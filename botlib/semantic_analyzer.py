# project libs
import re, json

from botlib.api.hanlpapi import HanlpApi, NerCatalogs
from botlib.api.labapi import LabApi
from botlib.botlogger import BotLogger
from botlib.converter.datetime_converter import DatetimeConverter
from botlib.services import Services, news
from botlib.botresponse import BotResponseLanguage



class SemanticAnalyzer :
    """
    Semantic Analyze Input Speech Text
    This Class Try To Find Out These Info With NER:
    1. Target Service
    2. pnList, Events, Datetime Range, Locations
    """


    def __init__( self, speech_text: str ) :

        # should parse and rm language specification part to avoid keywords mismatching
        self.speech_text, self.response_language = self.__change_response_language(speech_text)

        # must pass
        self.parsed_content = DatetimeConverter.standardize_datetime(self.speech_text)
        self.time_range = DatetimeConverter.extract_datetime(self.parsed_content)

        # information that extract from user speech
        self.people = []
        self.organizations = []
        self.date = []
        self.time = []
        self.locations = []

        self.keywords = []

        # media extract from speech text
        self.media = news.AvailableMedia.NCKU

        # result types
        self.service = Services.UNKNOWN


    # ------------------------------------------------------------------------------------------------------------
    @staticmethod
    def __change_response_language( speech_text ) -> (str, BotResponseLanguage) :
        """
        extract and rm language specification part from speech text to avoid keywords mismatching

        :return: tuple of  (speech text without language specification parts, BotResponseLanguage obj)
        """

        # extract language specification part from speech text
        chinese_rule = "(以|用)(中文|國語)((告訴|回答|回覆)我?|說)"
        taiwanese_rule = "(以|用)(閩南語|台語|臺語)((告訴|回答|回覆)我?|說)"

        if re.search(chinese_rule, speech_text) is not None :
            speech_text = re.sub(chinese_rule, "", speech_text)
            return speech_text, BotResponseLanguage.CHINESE

        if re.search(taiwanese_rule, speech_text) is not None :
            speech_text = re.sub(taiwanese_rule, "", speech_text)
            return speech_text, BotResponseLanguage.TAIWANESE

        return speech_text, BotResponseLanguage.CHINESE


    def __extract_keywords( self, ws_pos_ner: dict ) :

        # stupidly rm repeat items
        tmp_list = HanlpApi.extract_keywords(ws_pos_ner["WS"], ws_pos_ner["POS"])
        tmp_list += self.people + self.organizations + self.locations
        tmp_list = list(set(tmp_list))

        # rm useless keywords
        self.keywords = []

        for keyword in tmp_list :
            # rm single word
            if len(keyword) < 2 :
                continue
            elif keyword in ["新聞", "報導", "活動"] :
                continue
            # rm media keyword
            elif SemanticAnalyzer.__extract_media(keyword) is not None :
                continue

            self.keywords.append(keyword)

        BotLogger.info(f"Extract keywords : {self.keywords}")


    @staticmethod
    def __extract_media( cht_text: str ) -> news.AvailableMedia or None :
        """
        Find Media From pnList From NER Result

        :param cht_text: pnList from ner info
        :return: news.AvailableMedia, None for no media Found
        """

        # find available media from pn List
        if re.search("自由時報", cht_text) :
            return news.AvailableMedia.LTN
        if re.search("(中國時報|中時(電子報)?)", cht_text) :
            return news.AvailableMedia.CHINATIME
        if re.search("TVBS", cht_text, re.IGNORECASE) :
            return news.AvailableMedia.TVBS
        if re.search("(東森|ETTODAY|新聞雲)", cht_text, re.IGNORECASE) :
            return news.AvailableMedia.ETTODAY
        if re.search("(UDN|聯合報)", cht_text, re.IGNORECASE) :
            return news.AvailableMedia.UDN
        if re.search("(成大|成功大學)", cht_text) :
            return news.AvailableMedia.NCKU

        return None


    # ------------------------------------------------------------------------------------------------------------


    def parse_content( self ) -> None :
        """
        do NER on input speech text vis Lab API
        and determine target Service base on NER result
        
        :return: None
        """

        # parse modified user speech
        BotLogger.info(f"Parsing Sentence : {self.parsed_content}")
        ws_pos_ner = HanlpApi.parse_sentence(self.parsed_content)
        BotLogger.info(BotLogger.prettify_dict_log(ws_pos_ner, "Parse Result : \n"))

        #
        if ws_pos_ner is not None :
            # classify common ner types into dict
            catalogs = HanlpApi.classify_common_words(ws_pos_ner["NER"])
            BotLogger.info(BotLogger.prettify_dict_log(catalogs, "Catalogs Dict : \n"))

            self.people = catalogs[NerCatalogs.PERSON.value]
            self.organizations = catalogs[NerCatalogs.ORGANIZATION.value]
            self.date = catalogs[NerCatalogs.DATE.value]
            self.time = catalogs[NerCatalogs.TIME.value]
            self.locations = catalogs[NerCatalogs.LOCATION.value]
            self.locations.sort(key = len)

            # generate keyword list from ws, pos, ner results
            self.__extract_keywords(ws_pos_ner)

        # extract media from speech text
        media = SemanticAnalyzer.__extract_media(self.speech_text)
        if media is not None :
            self.media = media

        # determine service type
        if self.is_search_news() :
            self.service = Services.SEARCH_NEWS

        elif self.is_activity() :
            if self.is_search_activity() :
                self.service = Services.SEARCH_ACTIVITY
            elif self.is_create_activity() :
                self.service = Services.CREATE_ACTIVITY
            else :
                self.service = Services.SEARCH_ACTIVITY

        else :
            self.service = Services.UNKNOWN
            BotLogger.info("Unknown Service")

        BotLogger.debug("Parsing Speech Text Done.")


    def is_search_news( self ) -> bool :
        """
        user request a news searching service or not

        :return: is a news searching request
        """
        for kw in ["新聞", "報導"] :
            if kw in self.parsed_content :
                return True
        return False


    def is_activity( self ) -> bool :
        """
        user request a activity searching or creating service or not

        :return: is a activity request
        """
        for kw in ["活動", "考試", "展", "演講"] :
            if kw in self.parsed_content :
                return True
        return False


    def is_search_activity( self ) -> bool :
        """
        user request a activity searching service or not

        :return: is a activity searching request
        """
        for keyword in ["查詢", "什麼", "想知道", "哪些"] :
            if keyword in self.parsed_content :
                return True
        return False


    def is_create_activity( self ) -> bool :
        """
        user request a activity creating service or not

        :return: is a activity searching request
        """
        for keyword in ["有", "舉行", "舉辦"] :
            if keyword in self.parsed_content :
                return True
        return False
# project libs
import re

from botlib.api.hanlpapi import HanlpApi, NerCatalogs
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
    NEWS_SEARCH_KEYWORDS = ["新聞", "報導"]
    ACTIVITY_GENERAL_KEYWORDS = ["活動", "考試", "展", "演講", "遊行", "舉行", "舉辦", "會"]
    ACTIVITY_SEARCH_KEYWORDS = ["查詢", "什麼", "想知道", "哪些"]
    ACTIVITY_CREATE_KEYWORDS = ["有", "舉行", "舉辦", "開放", "加入"]


    def __init__( self, speech_text: str ) :

        # should parse and rm language specification part to avoid keywords mismatching
        self.speech_text_no_lang, self.response_language = SemanticAnalyzer.__change_response_language(speech_text)

        self.speech_text_no_abbr = SemanticAnalyzer.__remove_speech_abbreviation(self.speech_text_no_lang)

        # parse datetime description and extract datetime range
        self.parsed_content = DatetimeConverter.standardize_datetime(self.speech_text_no_abbr)
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


    def __str__( self ) :

        content = ""

        # check request mode
        if self.service == Services.SEARCH_NEWS :
            content += f"Search {self.media} News Request : \n"
        elif self.service == Services.SEARCH_ACTIVITY :
            content += f"Search Activity Request : \n"
        elif self.service == Services.CREATE_ACTIVITY :
            content += f"Create Activity Request : \n"
        else :
            return "Unknown Service"

        content += f"  * Parse Content  = {self.parsed_content} \n"
        content += f"  * Time Range     = {self.time_range}) \n"
        content += f"  * Keywords       = {self.keywords}"

        return content


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


    @staticmethod
    def __remove_speech_abbreviation( speech_text_no_lang: str ) -> str :

        result = speech_text_no_lang

        abbr_dict = {
            "台北101" : "台北101大樓", "北捷" : "台北捷運",
            "台大" : "台灣大學", "清大" : "清華大學", "交大" : "交通大學", "成大" : "成功大學"
        }

        for abbr in abbr_dict :
            result = result.replace(abbr, abbr_dict[abbr])

        return result


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
        if re.search("三立(新聞)?", cht_text) :
            return news.AvailableMedia.SETN
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
        custom_dict = {
            "自由時報" : "",
            "中國時報" : "",
            "成功大學" : "",
        }

        BotLogger.info(f"Parsing Sentence : {self.parsed_content}")
        ws_pos_ner = HanlpApi.parse_sentence(self.parsed_content, ws_custom_dict = custom_dict)
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
            self.locations = sorted(self.locations, key = len, reverse = True)

            # generate keyword list from ws, pos, ner results
            self.__extract_keywords(ws_pos_ner)

        # extract media from speech text
        media = SemanticAnalyzer.__extract_media(self.speech_text_no_abbr)
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
                self.service = Services.UNKNOWN

        else :
            self.service = Services.UNKNOWN
            BotLogger.info("Unknown Service")

        BotLogger.debug("Parsing Speech Text Done.")


    def is_search_news( self ) -> bool :
        """
        user request a news searching service or not

        :return: is a news searching request
        """
        for kw in SemanticAnalyzer.NEWS_SEARCH_KEYWORDS :
            if kw in self.parsed_content :
                return True
        return False


    def is_activity( self ) -> bool :
        """
        user request a activity searching or creating service or not

        :return: is a activity request
        """
        for kw in SemanticAnalyzer.ACTIVITY_GENERAL_KEYWORDS :
            if kw in self.parsed_content :
                return True
        return False


    def is_search_activity( self ) -> bool :
        """
        user request a activity searching service or not

        :return: is a activity searching request
        """
        for keyword in SemanticAnalyzer.ACTIVITY_SEARCH_KEYWORDS :
            if keyword in self.parsed_content :
                return True
        return False


    def is_create_activity( self ) -> bool :
        """
        user request a activity creating service or not

        :return: is a activity searching request
        """
        for keyword in SemanticAnalyzer.ACTIVITY_CREATE_KEYWORDS :
            if keyword in self.parsed_content :
                return True
        return False
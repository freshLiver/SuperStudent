# project libs
import datetime

from botlib.api.labapi import LabApi
from botlib.botlogger import BotLogger
from botlib.services import Services



class SemanticAnalyzer :
    """
    Semantic Analyze Input Speech Text
    This Class Try To Find Out These Info With NER:
    1. Target Service
    2. pnList, Events, Datetime Range, Locations
    """


    # ------------------------------------------------------------------------------------------------------------

    def __init__( self, speech_text: str ) :
        # text will be parsed
        self.speech_text = speech_text

        # info dict for target service
        self.obj_list = []
        self.pn_list = []
        self.events = []
        self.time_range = SemanticAnalyzer.__parse_time_range()
        self.locations = []

        # result types
        self.target_service = Services.UNKNOWN


    def parse_content( self ) -> None :
        """
        do NER on input speech text vis Lab API
        and determine target Service base on NER result
        
        :return: None
        """

        # parse speech text with NER
        ner_dict = LabApi.lab_ner_api(self.speech_text)
        BotLogger.debug(f"{{{self.speech_text}:{ner_dict}}}")

        # ner get nothing
        if ner_dict is None :
            BotLogger.info("NER Error.")

        # extract info from ner result (if result not None)
        else :
            # TODO : MUST IMPROVE THIS
            self.obj_list = ner_dict['objList']
            self.pn_list += list(ner_dict['pnList'])
            self.events += list(ner_dict['fullEventList'])
            self.time_range = SemanticAnalyzer.__parse_time_range(ner_dict['tList'])
            self.locations += list(ner_dict['locList'])

            # determine service
            if "新聞" in self.obj_list :
                self.target_service = Services.NEWS

            elif self.events != [] or "活動" in self.obj_list :

                # simply choose activity service type
                for search_kw in ["什麼", "想知道"] :
                    if search_kw in self.speech_text :
                        self.target_service = Services.SEARCH_ACTIVITY

                for create_kw in ["有", "舉行", "舉辦"] :
                    if create_kw in self.speech_text :
                        self.target_service = Services.CREATE_ACTIVITY

                # default activity service is SEARCH
                if self.target_service == Services.UNKNOWN :
                    self.target_service = Services.SEARCH_ACTIVITY

            # unknown request
            else :
                self.target_service = Services.UNKNOWN

            BotLogger.info("Parsing Speech Text Done.")


    @staticmethod
    def __parse_time_range( time_list = None ) -> (datetime, datetime) :
        """
        Parse Date Time Description List into Datetime Range (begin, finish) 
        
        :param time_list: Date Time Description List from NER
        :return: Datetime Range (begin, finish), default value is today's datetime range
        """

        # get today datetime range
        today_begin = datetime.datetime.combine(datetime.date.today(), datetime.time())
        today_finish = today_begin + datetime.timedelta(seconds = 86399)

        # TODO combine all datetime info to str
        if time_list is not None :
            pass

        # default datetime range is today
        return today_begin, today_finish
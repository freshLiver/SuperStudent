# project libs
from botlib.api.labapi import LabApi
from botlib.botlogger import BotLogger
from botlib.services import Services


class SemanticAnalyzer :
    """

    """
    
    
    # ------------------------------------------------------------------------------------------------------------
    
    def __init__( self, speech_text: str ) :
        # text will be parsed
        self.speech_text = speech_text
        
        # info dict for target service
        self.service_info = { }
        
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
        
        # ner get nothing
        if ner_dict is None :
            BotLogger.log_info("NER Error.")
        
        # extract info from ner result (if result not None)
        else :
            objects = ner_dict['objList']
            proper_nouns = ner_dict['pnList']
            events = ner_dict['fullEventList']
            datetime = ner_dict['tList']
            locations = ner_dict['locList']
            
            # determine service
            if "新聞" in objects :
                self.target_service = Services.NEWS
            elif events is not [] :
                self.target_service = Services.ACTIVITY
            else :
                self.target_service = Services.UNKNOWN
            
            # add service info
            self.service_info['ProperNouns'] = proper_nouns
            self.service_info['Events'] = events
            self.service_info['Datetime'] = datetime
            self.service_info['Locations'] = locations
            
            BotLogger.log_info("Parsing Speech Text Done.")
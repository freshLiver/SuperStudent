from enum import Enum



class BotResponseLanguage(Enum) :
    CHINESE = "CHINESE"
    TAIWANESE = "TAIWANESE"


class BotResponse :
    # Types of Responses
    NEWS = "NEWS"
    ACTIVITY = "ACTIVITY"
    INFORM = "INFORM"


    def __init__( self, language: BotResponseLanguage ) :
        self.url = ''
        self.text = ''
        self.location = ''
        self.language = language
        self.type = BotResponse.INFORM


    def __str__( self ) -> str :

        formatted_links = formatted_texts = ""
        for text in [text for text in self.text.split('\n') if text != ''] :
            formatted_texts += f"\t * {text}\n"
        for link in [link for link in self.url.split('\n') if link != ''] :
            formatted_links += f"\t * {link}\n"

        msg = ""
        msg += f"Type : {self.type}\n"
        msg += f"Text : \n{formatted_texts}"
        msg += f"Link : \n{formatted_links}"
        msg += f"Loc  : {self.location}\n"
        msg += f"Lang : {self.language.value}\n"
        return msg


    @staticmethod
    def make_news_response( url_text: [str, str], language: BotResponseLanguage ) -> 'BotResponse' :
        response = BotResponse(language)
        response.type = BotResponse.NEWS
        response.url = url_text[0]
        response.text = url_text[1]
        return response


    @staticmethod
    def make_activity_response( activity_content: str, location: str or None, language: BotResponseLanguage ) -> 'BotResponse' :
        response = BotResponse(language)
        response.type = BotResponse.ACTIVITY
        response.text = activity_content
        response.location = location
        return response


    @staticmethod
    def make_inform_response( inform_content: str, language: BotResponseLanguage ) -> 'BotResponse' :
        response = BotResponse(language)
        response.type = BotResponse.INFORM
        response.text = inform_content
        return response
class BotResponse :
    # Types of Responses
    NEWS = "NEWS"
    ACTIVITY = "ACTIVITY"
    INFORM = "INFORM"


    def __init__( self ) :
        self.type = BotResponse.INFORM
        self.text = "Default Inform Text"
        self.url = None


    def __str__( self ) -> str :
        return f"Type : {self.type}\nText : {self.text} \n URL : {self.url} \n"


    @staticmethod
    def make_news_response( news_content: str, news_url: str ) -> 'BotResponse' :
        response = BotResponse()
        response.type = BotResponse.NEWS
        response.text = news_content
        response.url = news_url
        return response


    @staticmethod
    def make_activity_response( activity_content: str ) -> 'BotResponse' :
        response = BotResponse()
        response.type = BotResponse.ACTIVITY
        response.text = activity_content
        return response


    @staticmethod
    def make_inform_response( inform_content: str ) -> 'BotResponse' :
        response = BotResponse()
        response.type = BotResponse.INFORM
        response.text = inform_content
        return response
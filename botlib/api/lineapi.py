from os import path
from pydub import AudioSegment

# project libs
from botlib.botlogger import BotLogger

# flask
from flask import request

# line sdk
from linebot import LineBotApi
from linebot.models import AudioSendMessage, TextSendMessage


class LineApi :
    """
    Simplified LineAPIs
    """
    
    
    @staticmethod
    def send_text( channel_token, reply_token, msg: str ) -> None :
        """
        Simplified TextSendMessage Line api
        
        :param channel_token: line bot channel token
        :param reply_token: reply token
        :param msg: text message
        :return: None
        """
        api = LineBotApi(channel_access_token = channel_token)
        api.reply_message(reply_token, TextSendMessage(text = msg))
        
        BotLogger.log_info(f"successfully send text message : {msg}")
    
    
    @staticmethod
    def send_audio( channel_token, reply_token, file_path: str ) -> str :
        """
        Simplified AudioSendMessage Line api
        
        :param channel_token: line bot channel token
        :param reply_token: reply token
        :param file_path: Audio Message Source File
        :return: None
        """
        
        # get filename by os.path.basename
        filename = path.basename(file_path)
        
        try :
            # get audio file duration
            audio_url = path.join(request.host_url, "audio", filename).replace("http://", "https://")
            audio_duration = AudioSegment.from_file(file_path).duration_seconds * 1000
            
            # reply audio file with duration
            api = LineBotApi(channel_access_token = channel_token)
            api.reply_message(reply_token, AudioSendMessage(audio_url, duration = audio_duration))
            
            BotLogger.log_info(f"successfully reply audio file : {filename} ")
        
        except FileNotFoundError as fe :
            BotLogger.log_exception(f"{file_path} NotFound : {fe}")
        
        except TypeError as te :
            BotLogger.log_exception(f"{file_path} TypeError : {te}")
        
        return "OK"
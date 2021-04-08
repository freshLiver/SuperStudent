from os import path
from os.path import expanduser
from pathlib import Path
from pydub import AudioSegment

# project libs
from botlib import BotConfig
from botlib.botlogger import BotLogger
from botlib.converter.audio_converter import AudioConvert
from botlib.converter.text_to_speech import TextToSpeech

# flask
from flask import request

# line sdk
from linebot import LineBotApi
from linebot.models import AudioMessage, AudioSendMessage, TextSendMessage



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
        BotLogger.info(f"successfully send text message : {msg}")



    @staticmethod
    def send_audio( channel_token, reply_token, file_path: Path ) -> None :
        """
        Simplified AudioSendMessage Line api
        
        :param channel_token: line bot channel token
        :param reply_token: reply token
        :param file_path: Audio Message Source File Path Obj
        :return: None
        """

        try :
            # get audio file duration
            audio_duration = AudioSegment.from_file(file_path).duration_seconds * 1000

            # reply audio file (by url) with duration
            audio_url = path.join(request.host_url, "audio", file_path.name).replace("http://", "https://")
            api = LineBotApi(channel_access_token = channel_token)
            api.reply_message(reply_token, AudioSendMessage(audio_url, duration = audio_duration))

            BotLogger.info(f"Audio Message '{file_path}' Sent.")

        except FileNotFoundError as fe :
            BotLogger.exception(f"Send Audio Failed, {file_path} FileNotFound : {fe}")

        except TypeError as te :
            BotLogger.exception(f"Send Audio Failed, {file_path} TypeError : {te}")

        except Exception as e :
            BotLogger.exception(f"Send Audio Failed, {type(e).__name__} : {e}")



    @staticmethod
    def make_audio_message_and_send( channel_token, reply_token, userid: str, msg: str ) -> None :
        """
        Send a Audio Message Made By msg TTS To User

        :param channel_token: line bot channel token
        :param reply_token: reply token
        :param userid: user line id to determine tmp file name
        :param msg: text message that will be heard by user
        :return: None
        """

        # tts to wav file
        wav_tts_path = TextToSpeech.cht_to_taiwanese(userid, msg)

        # convert wav tts audio to m4a audio
        m4a_response_file_path = AudioConvert.wav_to_m4a(wav_tts_path)

        # reply this audio message
        LineApi.send_audio(channel_token, reply_token, m4a_response_file_path)

        BotLogger.info(f"Send Text {msg} As Audio File : {m4a_response_file_path}")



    # -------------------------------------------------------------------------------------------------------


    @staticmethod
    def save_audio_message_as_m4a( userid: str, audio_message: AudioMessage, line_bot_api: LineBotApi ) -> Path :
        """
        save audio message as wav file to audio input tmp dir
        and this audio message will be named after {userid}{postfix}
        
        :param userid: line user id
        :param audio_message: audio message received from user
        :param line_bot_api: line bot api create in app.py
        :return: full path of tmp wav audio file
        """

        # read audio message content(bin)
        audio_message_content = line_bot_api.get_message_content(audio_message.id)

        # where this audio should be saved
        m4a_tmp_path = BotConfig.file_path_from(BotConfig.get_audio_input_dir(), userid)

        # write audio message content to tmp file
        with open(m4a_tmp_path, 'wb') as tmp_file :
            for chunk in audio_message_content.iter_content() :
                tmp_file.write(chunk)

        BotLogger.info(f"Audio Message Saved as m4a At {m4a_tmp_path}.")

        # return full path of the input audio file
        return Path(expanduser(m4a_tmp_path))
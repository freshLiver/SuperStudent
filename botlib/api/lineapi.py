from os import path
from os.path import expanduser
from pathlib import Path
from pydub import AudioSegment

# project libs
from botlib import BotConfig
from botlib.api.geoapi import GeoApi
from botlib.botlogger import BotLogger
from botlib.botresponse import BotResponse, BotResponseLanguage
from botlib.converter.audio_converter import AudioConvert
from botlib.converter.text_to_speech import TextToSpeech

# flask
from flask import request

# line sdk
from linebot import LineBotApi, exceptions
from linebot.models import AudioMessage, AudioSendMessage, TextSendMessage, LocationMessage



class LineApi :
    """
    Simplified LineAPIs
    """


    @staticmethod
    def push_text( userid, channel_token, text_msg: str ) -> None :
        """
        以 push 的方式讓 bot 傳送文字訊息給 userid
        不同於 reply message, 不需要 reply token 所以沒有 timeout 以及只能 reply 一次的問題

        :param userid: 使用者聊天室的 id
        :param channel_token: bot channel token
        :param text_msg: message text content
        :return: nothing
        """

        try :
            api = LineBotApi(channel_access_token = channel_token)
            api.push_message(userid, TextSendMessage(text = text_msg))
            BotLogger.info(f"Text Message '{text_msg}' Pushed.")

        except Exception as e :
            BotLogger.exception(f"Push Audio Failed, {type(e).__name__} : {e}")


    @staticmethod
    def push_audio( userid, channel_token, w4a_audio_path: Path ) -> None :
        """
        以 push 的方式讓 bot 傳送 w4a 音訊訊息給 userid
        會先將 path 改以 https url 的形式呈現，然後再利用 url 建立音訊訊息傳給 user

        不同於 reply message, 不需要 reply token 所以沒有 timeout 以及只能 reply 一次的問題

        :param userid: 使用者聊天室的 id
        :param channel_token: bot channel token
        :param w4a_audio_path: w4a 音訊檔在本機的路徑
        :return: nothing
        """

        try :

            # get audio file duration
            audio_duration = AudioSegment.from_file(w4a_audio_path).duration_seconds * 1000

            # push audio file (by url) with duration
            audio_url = path.join(request.host_url, "audio", w4a_audio_path.name).replace("http://", "https://")

            api = LineBotApi(channel_token)
            api.push_message(userid, AudioSendMessage(audio_url, duration = audio_duration))

            BotLogger.debug(f"Audio Message '{w4a_audio_path}' Pushed.")

        except FileNotFoundError as fe :
            BotLogger.exception(f"Push Audio Failed, {w4a_audio_path} FileNotFound : {fe}")

        except TypeError as te :
            BotLogger.exception(f"Push Audio Failed, {w4a_audio_path} TypeError : {te}")

        except Exception as e :
            BotLogger.exception(f"Push Audio Failed, \n * {w4a_audio_path}\n * {type(e).__name__} : \n * {e}")


    @staticmethod
    def try_push_location( userid, channel_token, location: str or None ) -> None :
        """
        試著 Push 一個 LocationMessage

        if 'location' is :
            - None : do nothing
            - not str : TypeError, 只紀錄 log
            - str : 查詢地址以及座標，如果都有找到就傳送 LocationMessage

        :param userid: target user id
        :param channel_token: bot channel token
        :param location: target location string
        :return: None
        """

        try :
            # check location type
            if location is None :
                return

            if type(location) is not str :
                raise TypeError("Location Should Be A String.")

            # 查詢該地點的完整地址以及座標
            address = GeoApi.get_full_address(location)
            coordinate = GeoApi.get_coordinate(location)

            # 如果地址或座標其中一項找不到就不 Push LocationMessage
            if coordinate is None or address is None :
                raise ValueError(f"Cannot Find Address or Coordinate Of Location : {location}")

            log = f"Find {location} Address And Coordinate : \n\t"
            log += f"Full Address : {address}\n\t"
            log += f"Coordinate : {coordinate}\n"
            BotLogger.info(log)

            # 如果有找到地址以及座標就 Push LocationMessage
            api = LineBotApi(channel_access_token = channel_token)
            loc_msg = LocationMessage(title = location, address = address, latitude = coordinate[0], longitude = coordinate[1])
            api.push_message(to = userid, messages = loc_msg)

            BotLogger.info(f"LocationMessage of ({location}) Sent.")

        except (TypeError, ValueError) as e :
            BotLogger.exception(e.__str__())

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} : \n{e}")


    @staticmethod
    def make_audio_message( channel_token, userid, msg: str, language: BotResponseLanguage, seq = 0 ) -> None :
        """
        利用 TTS 將文字訊息傳換成對應語言（BotResponseLanguage）
        然後將產生的 w4a 音訊檔傳送（push）給 user

        :param channel_token: line bot channel token
        :param userid: user line id to determine tmp file name
        :param msg: text message that will be heard by user
        :param language: bot response audio language
        :param seq: audio message sequence number
        :return: None
        """

        try :
            # tts to wav file
            filename = f"{userid}_{seq}"
            if language == BotResponseLanguage.CHINESE :
                wav_tts_path = TextToSpeech.cht_to_chinese(audio_name = filename, cht_text = msg)
            else :
                wav_tts_path = TextToSpeech.cht_to_taiwanese(audio_name = filename, cht_text = msg)

            # convert wav tts audio to m4a audio
            m4a_response_file_path = AudioConvert.wav_to_m4a(wav_tts_path)

            # reply this audio message
            LineApi.push_audio(userid, channel_token, m4a_response_file_path)
            BotLogger.info(f"Push Text \n\t * {msg} \nAs Audio File : \n\t * {m4a_response_file_path}")

        except Exception as e :
            BotLogger.exception(f"{type(e).__name__} Happened When Sending Audio Message.\n\t => {e}")


    @staticmethod
    def send_response( userid, channel_token, response: BotResponse ) -> None :
        """
        依據 BotResponse 中設定的 response type 傳送（push）不同的回覆給 user

        :param userid: target user id
        :param channel_token: bot channel token
        :param response: BotResponse instance
        :return: nothing
        """

        # INFORM 類訊息，通常是用來傳送「錯誤訊息」、「成功新增活動」
        if response.type == BotResponse.INFORM :
            LineApi.push_text(userid, channel_token, response.text)

        # NEWS 類訊息，來回覆使用者查詢新聞的結果
        elif response.type == BotResponse.NEWS :

            # response 可能會有多則以 newline 區隔的新聞，所以需要先進行切割再分別發送
            links = [link for link in response.url.split('\n') if link != '']
            texts = [text for text in response.text.split('\n') if text != '']

            if len(links) != len(texts) :
                msg = "News Response Warning, links and texts have diff size.\n"
                msg += f"\t links size = {links.__len__()}, texts size = {texts.__len__()}"
                BotLogger.warning(msg)

            # 網址以一個文字訊息傳送
            LineApi.push_text(userid, channel_token, response.url)

            # 新聞簡介則分成多個音訊傳送
            for i, intro_text in enumerate(texts) :
                LineApi.make_audio_message(channel_token, userid, intro_text, response.language, i)

        # ACTIVITY 類訊息，通常是查詢活動的結果，包含活動位置等資訊
        elif response.type == BotResponse.ACTIVITY :
            # 根據 RESPONSE 的 LOCATION 查詢並傳送地點（如果沒找到地點就不傳送位置訊息）
            LineApi.try_push_location(userid, channel_token, response.location)
            # 傳送文字訊息讓 User 知道自己說了什麼
            LineApi.push_text(userid, channel_token, response.speech_text)
            # 將「搜尋活動的結果轉成語音」並以「語音訊息」回覆 User
            LineApi.make_audio_message(channel_token, userid, response.text, response.language)

        else :
            BotLogger.error("Error Response Type, Should Not Be Here.")

        # 將回覆內容格式化輸出作為 log
        BotLogger.info(f"send response : {response.__str__()}")


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
        m4a_tmp_path = BotConfig.file_path_from(BotConfig.AUDIO_INPUT_TMP_DIR, userid)

        # write audio message content to tmp file
        with open(m4a_tmp_path, 'wb') as tmp_file :
            for chunk in audio_message_content.iter_content() :
                tmp_file.write(chunk)

        BotLogger.debug(f"Audio Message Saved as m4a At {m4a_tmp_path}.")

        # return full path of the input audio file
        return Path(expanduser(m4a_tmp_path))
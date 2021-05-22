from __future__ import unicode_literals

import os, sys

# project libs
from botlib import BotConfig
from botlib.api.lineapi import LineApi
from botlib.botlogger import BotLogger
from botlib.botresponse import BotResponse, BotResponseLanguage
from botlib.converter.audio_converter import AudioConvert
from botlib.converter.speech_to_text import SpeechToText
from botlib.services import match_service
from botlib.semantic_analyzer import SemanticAnalyzer

# flask libs
from flask import abort, Flask, request, send_from_directory, make_response

# line bot apis
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, AudioMessage



# create global app instance
app = Flask(__name__)

line_bot_api = LineBotApi(channel_access_token = BotConfig.LINE_CHANNEL_TOKEN)
handler = WebhookHandler(channel_secret = BotConfig.LINE_CHANNEL_SECRET)
parser = WebhookParser(channel_secret = BotConfig.LINE_CHANNEL_SECRET)

sys.path.append(os.path.join(BotConfig.PROJECT_ROOT))


# 接收 http POST requests
@app.route("/post_message", methods = ['POST'])
def callback() :
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)
    BotLogger.info(f"Get Request Body done, \n=> {body}")

    # Parse Content
    try :
        events = parser.parse(body, signature)

        # 檢查各個 event
        for event in events :
            # event 必須是 MessageEvent
            if not isinstance(event, MessageEvent) :
                BotLogger.error("Not A MessageEvent, Ignored.")
                continue

            # MessageEvent 的 message 需要是 Audio Message
            if isinstance(event.message, AudioMessage) :

                # get userid, reply_token, channel_token
                userid = event.source.user_id
                reply_token = event.reply_token
                channel_token = BotConfig.LINE_CHANNEL_TOKEN

                # 將 User 傳送的 Audio Message 轉存為 m4a 音檔
                m4a_tmp_path = LineApi.save_audio_message_as_m4a(userid, event.message, line_bot_api)

                # 必須將 m4a 轉成 wav 才能進行 STT(語音辨識)
                wav_tmp_path = AudioConvert.m4a_to_wav(m4a_tmp_path)

                # STT, 將 audio 的內容辨識成中文
                speech_text = SpeechToText.duo_lang_to_cht(wav_tmp_path)

                # STT 發生問題, 傳送 INFORM RESPONSE
                if speech_text is None :
                    response = BotResponse.make_inform_response("語音辨識失敗，請再說一遍", BotResponseLanguage.CHINESE)
                    LineApi.send_response(userid, channel_token, response)
                    BotLogger.info("Speech Text Is None.")
                    continue

                # 根據語音辨識內容進行對應工作，並回覆結果給 User
                else :
                    # 將辨識內容進行語意辨識
                    analyzer = SemanticAnalyzer(speech_text)
                    analyzer.parse_content()

                    # 根據語意辨識結果進行對應服務並獲得結果（RESPONSE）
                    response = match_service(analyzer = analyzer)

                    # 如果 RESPONSE 不為 None（不應為 None） 就根據 response 進行回應
                    if response is not None :
                        LineApi.send_response(userid, channel_token, response)
                    else :
                        BotLogger.error(f"Match Service Return None, Request : {speech_text}")


    # 其他錯誤
    except InvalidSignatureError as e :
        BotLogger.exception(f"InvalidSignatureError : {e}")
        abort(400)

    return "OK"


@app.route("/audio/<path:filename>")
def audio( filename ) :
    """
    用來獲取 output audio 的 http interface

    :param filename: request 檔名
    :return:
    """
    try :
        BotLogger.info(f"Audio Request : audio/{filename}")
        return send_from_directory(BotConfig.AUDIO_OUTPUT_TMP_DIR, filename)

    except Exception as e :
        BotLogger.exception(f"Getting Audio File Error : {type(e).__name__} \n{e}")
        return None


@app.route("/", methods = ["GET"])
def home() :
    res = make_response("Home Route Of My Line Bot.")
    res.mimetype = "text/plain"
    return res


if __name__ == "__main__" :
    app.run(host = '0.0.0.0', port = BotConfig.PORT, debug = True)
from __future__ import unicode_literals

import os, sys

# project libs
from botlib import BotConfig
from botlib.api.lineapi import LineApi
from botlib.botlogger import BotLogger
from botlib.botresponse import BotResponse, BotResponseLanguage
from botlib.converter.audio_converter import AudioConvert
from botlib.converter.speech_to_text import SpeechToText
from botlib.services import match_service, Services
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
                c2c_result, t2c_result = SpeechToText.duo_lang_to_cht(wav_tmp_path)


                def parse_content_and_match_service( stt_text: str, default_lang: BotResponseLanguage ) -> BotResponse :
                    # 將辨識內容進行語意辨識
                    analyzer = SemanticAnalyzer(stt_text, default_lang)
                    analyzer.parse_content()

                    # 根據語意辨識結果進行對應服務並獲得結果（RESPONSE）
                    return match_service(analyzer = analyzer)


                # check if c2c result meaningful
                c2c_response = t2c_response = None
                c2c_meaningful = t2c_meaningful = False

                if c2c_result is not None :
                    c2c_response = parse_content_and_match_service(c2c_result, BotResponseLanguage.CHINESE)
                    c2c_meaningful = not c2c_response.is_unknown_service

                # if c2c result not meaningful, check t2c result
                if t2c_result is not None and c2c_meaningful == False :
                    t2c_response = parse_content_and_match_service(t2c_result, BotResponseLanguage.TAIWANESE)
                    t2c_meaningful = not t2c_response.is_unknown_service

                # 兩種語言都辨識失敗（Unknown Service）
                if c2c_meaningful == t2c_meaningful == False :
                    err_msg = f"非常抱歉，我聽不懂你的需求，請再說一遍"
                    speech_text = f"\n中文：({c2c_result})\n台語：({t2c_result}\n)"
                    response = BotResponse.make_inform_response(speech_text, err_msg, BotResponseLanguage.CHINESE)

                # 中文或台語辨識成功
                else :
                    response = c2c_response if c2c_meaningful else t2c_response

                # 傳送 response
                LineApi.send_response(userid, channel_token, response)


    except InvalidSignatureError as e :
        BotLogger.exception(f"InvalidSignatureError : {e}")
        abort(400)

    # 其他錯誤
    except Exception as e :
        BotLogger.error(f"ERROR {type(e).__name__} \n\t=> {e}")

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
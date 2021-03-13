from __future__ import unicode_literals

# project libs
from botlib.botconfig import BotConfig
from botlib.botlogger import BotLogger
from botlib.api.lineapi import LineApi

# flask libs
from flask import abort, Flask, request

# line bot apis
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage



# create global app instance
app = Flask(__name__)

line_bot_api = LineBotApi(channel_access_token = BotConfig.get_channel_token())
handler = WebhookHandler(channel_secret = BotConfig.get_channel_secret())
parser = WebhookParser(channel_secret = BotConfig.get_channel_secret())


# receive line message event
@app.route("/post_message", methods = ['POST'])
def callback() :
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)
    BotLogger.log_debug(f"Get Request Body done, \n=> {body}")
    
    # parse webhook body
    events = None
    try :
        events = parser.parse(body, signature)
        BotLogger.log_debug("signature parse done")

    # parse bot event failed
    except InvalidSignatureError as e :
        BotLogger.log_exception(f"InvalidSignatureError : {e}")
        abort(400)
    
    # if event is MessageEvent and message is TextMessage
    for event in events :
        # should be message event
        if not isinstance(event, MessageEvent) :
            BotLogger.log_error("not message event, ignore")
            continue
        
        # check message type
        if isinstance(event.message, TextMessage) :
            LineApi.send_text(BotConfig.get_channel_token(), event.reply_token, event.message.text)
    
    return "OK"


if __name__ == "__main__" :
    app.run(port = BotConfig.get_flask_app_port(), debug = True)
# built in libs
from __future__ import unicode_literals

# flask libs
from flask import abort, Flask, request
# line bot apis
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# create global app instance
app = Flask(__name__)

channel_access_token = "ML02QDbg6nl3ovKrrt3cT0SZ6EbLT+oVJ1/TT9AjbD2Z26OYHSwSVnn0Ie1TlUYviRQJA9G6zOoXluwwPLN9GS" \
                       "+N0iSeXi8wcBcr82mH4dS3PMU7cmQzZxo3XpzQ8TXSp/babmAhYaEoz30IY/J0nAdB04t89/1O/w1cDnyilFU="
channel_secret = "51c50b8d2dc082cff2b074a26f5fede3"

line_bot_api = LineBotApi(channel_access_token = channel_access_token)
handler = WebhookHandler(channel_secret = channel_secret)
parser = WebhookParser(channel_secret = channel_secret)


# receive line message event
@app.route("/post_message", methods = ['POST'])
def callback() :
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text = True)
    
    # parse webhook body
    events = None
    try :
        events = parser.parse(body, signature)
    
    except InvalidSignatureError as ise :
        abort(400)
    
    # if event is MessageEvent and message is TextMessage
    for event in events :
        
        # should be message event
        if not isinstance(event, MessageEvent) :
            continue
        
        # check message type
        if isinstance(event.message, TextMessage) :
            line_apt = LineBotApi(channel_access_token = channel_access_token)
            line_apt.reply_message(event.reply_token, TextSendMessage(event.message.text))
    
    return "OK"


if __name__ == "__main__" :
    app.run(port = 7777, debug = True)
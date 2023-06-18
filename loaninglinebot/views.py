from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import pyrebase
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

 
config={
    "apiKey": "AIzaSyB8OegD2oZlw22bygSdzHoeaCDntXd4hq8",
    "authDomain": "mylinebot-4fbee.firebaseapp.com",
    "databaseURL": "https://mylinebot-4fbee-default-rtdb.firebaseio.com",
    "projectId": "mylinebot-4fbee",
    "storageBucket": "mylinebot-4fbee.appspot.com",
    "messagingSenderId": "594262413594",
    "appId": "1:594262413594:web:512dfbbb257f3c617d5ca3"
}
firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
db=firebase.database()

@csrf_exempt
def callback(request):
 
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                
                line_bot_api.reply_message(  # 回復傳入的訊息文字
                    event.reply_token,
                    TextSendMessage(text=event.message.text+db.child("user1").child("name").get().val())#
                )
                #db.push({"content":'買菜'})
                print(event.message.text)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import pyrebase
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
 
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
mylist = ["開始","查看","記帳","刪除","結束操作"]

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
            username = event.source.user_id
            mydata = db.get().val()
            # print(mydata)
            key = username

            if key not in mydata:
                #print(f"The key '{key}' exists in the data.")
                # db.child(username).update({"state":"Z"})
                
            # else:
            #     #print(f"The key '{key}' does not exist in the data.")
                user={username: {"state":"A","111111":{"money":"none"}}}
                db.update(user)
            if isinstance(event, MessageEvent) and event.message.text not in mylist:  # 如果有訊息事件
                # print("11111",event.message.text,db.child(username).child("state").get().val())
                reply_arr=[]
                if event.message.text == "reset()":
                    db.child(username).update({"state":"S"})
                    reply_arr.append(
                        TextSendMessage(
                            text="OK我們又重新開始了唷,請點下面的開始,阿如果linebot怪怪的麻煩輸入「reset()」,然後多給它一點耐心,不然它會一直壞掉!!!",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(
                                        action=PostbackAction(
                                            label="開始",
                                            text='開始',
                                            data="S"
                                        )
                                    )
                                ]
                            )
                        )
                    )
                    line_bot_api.reply_message(
                        event.reply_token,
                        reply_arr
                    )
                elif db.child(username).child("state").get().val() == "Z":
                    reply_arr.append(
                        TextSendMessage(
                            text="泥好,請點下面的開始,阿如果linebot怪怪的麻煩輸入「reset()」,然後多給它一點耐心,不然它會一直壞掉!!!",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(
                                        action=PostbackAction(
                                            label="開始",
                                            text='開始',
                                            data="S"
                                        )
                                    )
                                ]
                            )
                        )
                    )
                    line_bot_api.reply_message(
                        event.reply_token,
                        reply_arr
                    )
                    db.child(username).update({"state":"S"})                
                elif db.child(username).child("state").get().val() == "A" and event.message.text != "查看":
                    content = ""
                    if event.message.text == "全部":
                        for user_key, user_value in mydata.items():
                            if user_key == username:
                                for people_key, money_value in user_value.items():
                                    if 'money' in money_value:
                                        try:
                                            money = int(money_value['money'])
                                        except:
                                            continue
                                        money = int(money_value['money'])
                                        if money > 0:
                                            content += "目前你欠 " + people_key + " " + str(money) + "元"
                                        elif money < 0:
                                            content += "目前 " + people_key + " 欠你" + str(-1*money) + "元"
                                        else:
                                            content += "你跟 " + people_key + " 扯平ㄌ!"
                                        content += "\n"
                                if content=="":
                                    content += "目前還沒有東東喔"
                    else:
                        for item_key, item_value in mydata.items():
                            if item_key == username and event.message.text in item_value:
                                # print(item_value[event.message.text]["money"])
                                money = int(item_value[event.message.text]["money"])
                                if money > 0:
                                    content += "目前你欠 " + event.message.text + " " + str(money) + "元"
                                elif money < 0:
                                    content += "目前 " + event.message.text + " 欠你" + str(-1*money) + "元"
                                else:
                                    content += "你跟 " + event.message.text + " 扯平ㄌ!"
                                break
                        if content=="":
                            content += "查無此筆資料"                         
                    reply_arr.append(
                        TextSendMessage(text=content.strip())
                    )
                    reply_arr.append(
                        TextSendMessage(
                            text="你可以繼續輸入,或點選下方的結束操作",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(
                                        action=PostbackAction(
                                            label="結束操作",
                                            text="結束操作",
                                            data="N"
                                        )
                                    )
                                ]
                            )
                        )
                    )
                    line_bot_api.reply_message(
                        event.reply_token,
                        reply_arr
                    )
                elif db.child(username).child("state").get().val() == "B"and event.message.text != "記帳":
                    content = ""
                    try:
                        temp_list = event.message.text.split(' ')
                        people_key = temp_list[0]
                        money = "0.5"
                        for item_key, item_value in mydata.items():
                            if item_key == username and people_key in item_value:
                                money = int(item_value[people_key]["money"])+int(temp_list[1])
                                break
                        if money == "0.5":
                            money = int(temp_list[1])
                        if money > 0:
                            content += "目前你欠 " + people_key + " " + str(money) + "元"
                        elif money < 0:
                            content += "目前 " + people_key + " 欠你 " + str(-1*money) + "元"
                        else:
                            content += "你跟 " + people_key + " 扯平ㄌ!"
                        db.child(username).child(people_key).update({"money":str(money)})
                    except:
                        content = "輸入格式錯誤"
                    reply_arr.append(  # 回覆傳入的訊息文字
                        TextSendMessage(text=content)
                    )
                    reply_arr.append(
                        TextSendMessage(
                            text="你可以繼續輸入,或點選下方的結束操作",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(
                                        action=PostbackAction(
                                            label="結束操作",
                                            text="結束操作",
                                            data="N"
                                        )
                                    )
                                ]
                            )
                        )
                    )
                    line_bot_api.reply_message(
                        event.reply_token,
                        reply_arr
                    )
                elif db.child(username).child("state").get().val() == "C"and event.message.text != "刪除":
                    content = ""
                    for item_key, item_value in mydata.items():
                        if item_key == username and event.message.text in item_value:
                            db.child(username).child(event.message.text).remove()
                            content += "刪除成功!"
                            break
                    if content=="":
                        content += "查無此筆資料"
                    reply_arr.append(
                        TextSendMessage(text=content),
                    )
                    reply_arr.append(
                        TextSendMessage(
                            text="你可以繼續輸入,或點選下方的結束操作",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(
                                        action=PostbackAction(
                                            label="結束操作",
                                            text="結束操作",
                                            data="N"
                                        )
                                    )
                                ]
                            )
                        )
                    )
                    line_bot_api.reply_message(
                        event.reply_token,
                        reply_arr
                    )
                else:
                    db.child(username).update({"state":"S"})
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="阿好像怪怪的捏,不然我們重來怎麼樣...\n請點下面的開始,阿如果linebot怪怪的麻煩輸入「reset()」,然後多給它一點耐心,不然它會一直壞掉!!!",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(
                                        action=PostbackAction(
                                            label="開始",
                                            text='開始',
                                            data="S"
                                        )
                                    )
                                ]
                            )
                        )
                    )
            elif isinstance(event, PostbackEvent):
                # print("222222")
                if event.postback.data == "N":
                    db.child(username).update({"state":"S"})
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="窩們下次再見!!\n要繼續操作請點下面的開始,阿如果linebot怪怪的麻煩輸入「reset()」,然後多給它一點耐心,不然它會一直壞掉!!!",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(
                                        action=PostbackAction(
                                            label="開始",
                                            text="開始",
                                            data="S"
                                        )
                                    )
                                ]
                            )
                        )
                    )
                elif event.postback.data == "S":
                    db.child(username).update({"state":"F"})
                    line_bot_api.reply_message(
                        event.reply_token,
                        TemplateSendMessage(
                            alt_text="Buttons template",
                            template=ButtonsTemplate(
                                title="選單",
                                text="請選擇你想執行的動作",
                                actions=[
                                    PostbackTemplateAction(
                                        label="查看",
                                        text="查看",
                                        data="A"
                                    ),
                                    PostbackTemplateAction(
                                        label="記帳",
                                        text="記帳",
                                        data="B"
                                    ),
                                    PostbackTemplateAction(
                                        label="刪除",
                                        text="刪除",
                                        data="C"
                                    )
                                ]
                            )
                        )
                    )
                elif event.postback.data == "A":
                    db.child(username).update({"state":"A"})
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請輸入「全部」或你想查詢的名字"),
                    )
                elif event.postback.data == "B":
                    db.child(username).update({"state":"B"})
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="請輸入「名字 記帳的金額」,例如:「龍貓鼠 1224」,若是你欠對方請輸入正值,若是對方欠你請輸入負值"),
                    )
                elif event.postback.data == "C":
                    content="請輸入你想刪除的名字:\n"
                    for item_key, item_value in mydata.items():
                        if item_key == username:
                            for people_key, money_value in item_value.items():
                                if 'money' in money_value:
                                    print(money_value)
                                    try:
                                        money = int(money_value['money'])
                                        content += people_key + "\n"
                                    except:
                                        continue
                    if content == "請輸入你想刪除的名字:\n":
                        db.child(username).update({"state":"S"})
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(
                                text="阿明明就沒有名字咩\n窩們重來!!",
                                quick_reply=QuickReply(
                                    items=[
                                        QuickReplyButton(
                                            action=PostbackAction(
                                                label="開始",
                                                text="開始",
                                                data="S"
                                            )
                                        )
                                    ]
                                )
                            )
                        )
                    else:
                        db.child(username).update({"state":"C"})
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=content.strip()),
                        )
                else:
                    db.child(username).update({"state":"S"})
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="阿好像怪怪的捏,不然我們重來怎麼樣...\n請點下面的開始,阿如果linebot怪怪的麻煩輸入「reset()」,然後多給它一點耐心,不然它會一直壞掉!!!",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(
                                        action=PostbackAction(
                                            label="開始",
                                            text="開始",
                                            data="S"
                                        )
                                    )
                                ]
                            )
                        )
                    )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()
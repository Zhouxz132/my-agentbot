import os

import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json
APP_ID="cli_a8aec818a9b8d00c"
APP_SECRET = "mxCqsm5snqyxvSnwzzaDueQa6c52rIfE"
coze_api_token = 'pat_uLQDH9ygqe0NVvhV91uS7wAX6jX9xHC8nVpDMobI31pmRj9m8TDuijFWcjigpWC4'
workflow_id = '7505874284272369683'
teacher_id = "ou_c16652b107f1613894f734758f06775c"
bot_name = "小智协作"




# 注册接收消息事件，处理接收到的消息。
# Register event handler to handle received messages.
# https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/events/receive
def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    if not data.event.message.mentions:
        return None
    list_mentions = [mentioninfo.name for mentioninfo in data.event.message.mentions]
    if bot_name not in list_mentions:
        return None
    res_content = ""
    if data.event.message.message_type == "text":
        res_content = json.loads(data.event.message.content)["text"]
    else:
        res_content = "解析消息失败，请发送文本消息\nparse message failed, please send text message"

    if data.event.message.chat_type == "p2p":
        request = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(data.event.message.chat_id)
                .msg_type("text")
                .content(json.dumps({"text":"小助手当前不支持私下沟通！！！嚯嚯嚯"}))
                .build()
            )
            .build()
        )
        # 使用OpenAPI发送消息
        # Use send OpenAPI to send messages
        # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
        response = client.im.v1.chat.create(request)

        if not response.success():
            raise Exception(
                f"client.im.v1.chat.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
            )
    else:
        content = json.dumps(
            {
                "text": "收到你发送的消息："
                        + res_content
                        + "\nReceived message:"
                        + res_content
            }
        )
        import requests

        # API URL
        url = "https://api.coze.cn/v1/workflow/run"

        # Authorization Token
        token = coze_api_token

        # 请求头
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # 请求体
        data = {
            "parameters": {
                "app_id": APP_ID,
                "app_secret_key": APP_SECRET,
                "content": res_content,
                "group_id": data.event.message.chat_id,
                "reply_msg_id": data.event.message.message_id,
                "teacher_id": teacher_id,
                "user_id": data.event.sender.sender_id.open_id,
            },
            "workflow_id": workflow_id,
            "is_async": True
        }

        # 发送 POST 请求
        response = requests.post(url, headers=headers, json=data)

        # 打印响应结果
        print("content:", res_content)
        print("Status Code:", response.status_code)
        print("Response Body:", response.json())


# 注册事件回调
# Register event handler.
event_handler = (
    lark.EventDispatcherHandler.builder("", "")
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)
    .build()
)


# 创建 LarkClient 对象，用于请求OpenAPI, 并创建 LarkWSClient 对象，用于使用长连接接收事件。
# Create LarkClient object for requesting OpenAPI, and create LarkWSClient object for receiving events using long connection.
client = lark.Client.builder().app_id(APP_ID).app_secret(APP_SECRET).build()
wsClient = lark.ws.Client(
    APP_ID,
    APP_SECRET,
    event_handler=event_handler,
    log_level=lark.LogLevel.DEBUG,
)


def main():
    #  启动长连接，并注册事件处理器。
    #  Start long connection and register event handler.
    wsClient.start()


if __name__ == "__main__":
    main()

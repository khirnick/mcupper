import json

from channels import Channel, Group

from cupper.room import GameMain


def ws_connect(message):
    message.reply_channel.send({'accept': True})
    Group('cupper').add(message.reply_channel)


def ws_receive(message):
    a = json.loads(message['text'])
    Group('cupper').send({'text': json.dumps({'user_id': a['user_id']})})
    payload = a
    payload['reply_channel'] = message.content['reply_channel']
    Channel("cupper.receive").send(payload)


def ws_disconnect(message):
    pass


def room_join(message):
    print(message['room'], " ", message.content)
    message.reply_channel.send({'text': json.dumps({'user_id': message.content['user_id']})})
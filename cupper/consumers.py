import json

from channels import Channel, Group

from cupper.room import GameMain


def ws_connect(message):
    message.reply_channel.send({'accept': True})
    Group('cupper').add(message.reply_channel)


def ws_receive(message):
    a = json.loads(message['text'])
    payload = a
    payload['reply_channel'] = message.content['reply_channel']
    Channel("cupper.receive").send(payload)


def ws_disconnect(message):
    pass


def room_join(message):
    user_id = message.content['user_id']
    room_id = int(message.content['room'])
    room = GameMain.get_room_by_id(room_id)

    print(room.user_channels)

    user_channel = room.user_channels.get(user_id)
    if user_channel is None:
        room.user_channels[user_id] = message.reply_channel

        all_users = ''
        for u in room.user_channels:
            all_users += ("{0}\n".format(u))

        print(all_users)

        for u in room.user_channels:
            room.user_channels[u].send({'text': json.dumps({'user_id': all_users})})
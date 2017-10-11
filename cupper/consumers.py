import json

from channels import Channel, Group

from cupper.room import GameMain


def ws_connect(message):
    message.reply_channel.send({'accept': True})


def ws_receive(message):
    a = json.loads(message['text'])
    payload = a
    payload['reply_channel'] = message.content['reply_channel']
    Channel("cupper.receive").send(payload)


def ws_disconnect(message):
    print('qweqwe')
    for room in GameMain.rooms:
        for u in room.user_channels:
            if room.user_channels[u] == message.reply_channel:
                del room.user_channels[u]
                print()

    all_users = ''
    for room in GameMain.rooms:
        for u in room.user_channels:
            all_users += ("{0}\n".format(u))
            room.user_channels[u].send({'text': json.dumps({'user_id': all_users})})
            all_users = ''


def room_join(message):
    user_id = message.content['user_id']
    room_id = int(message.content['room'])
    room = GameMain.get_room_by_id(room_id)

    user_channel = room.add_user_channel(user_id, message.reply_channel)
    if user_channel:

        all_users = ''
        for u in room.user_channels:
            all_users += ("{0}\n".format(u))

        for u in room.user_channels:
            room.user_channels[u].send({'text': json.dumps({'user_id': all_users})})


def room_leave(message):
    user_id = message.content['user_id']
    room_id = int(message.content['room'])
    room = GameMain.get_room_by_id(room_id)

    ch = room.user_channels[int(user_id)]

    ch.send({'text': json.dumps({'user_leave': True})})

    del room.user_channels[int(user_id)]

    all_users = ''
    for u in room.user_channels:
        if room.user_channels[u] is not None:
            all_users += ("{0}\n".format(u))

    for u in room.user_channels:
        if room.user_channels[u] is not None:
            room.user_channels[u].send({'text': json.dumps({'user_id': all_users})})



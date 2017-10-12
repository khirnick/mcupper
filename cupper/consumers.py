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
    print(message.reply_channel)

    key_to_delete = []

    for room in GameMain.rooms:
        for u in room.user_channels:
            print(room.user_channels[u])
            if str(message.reply_channel) == str(room.user_channels[u]):
                key_to_delete = u
                break
        room.user_channels.pop(key_to_delete, None)

    for room in GameMain.rooms:
        for u in room.user_channels:
            print(u)

    all_users = ''
    for room in GameMain.rooms:
        for u in room.user_channels:
            all_users += ("{0}\n".format(u))
        for u in room.user_channels:
            room.user_channels[u].send({'text': json.dumps({'user_id': all_users})})
        all_users = ''


def room_join(message):
    user_id = message.content['user_id']
    room_id = int(message.content['room'])
    room = GameMain.get_room_by_id(room_id)

    if len(room.user_channels) == room.max_channels:
        return

    user_channel = room.add_user_channel(user_id, message.reply_channel)
    if user_channel:

        all_users = ''
        for u in room.user_channels:
            all_users += ("{0}\n".format(u))

        for u in room.user_channels:
            room.user_channels[u].send({'text': json.dumps({'user_id': all_users})})

    if not room.game_is_online:
        if len(room.user_channels) == room.max_channels:
            room.game_online = True
            task = room.make_current_task()
            room.task_no += 1
            for u in room.user_channels:
                room.user_score[u] = 0
            for u in room.user_channels:
                room.user_channels[u].send({'text': json.dumps({'game_start': True, 'image': str(task.image)})})


def room_leave(message):
    user_id = message.content['user_id']
    room_id = int(message.content['room'])
    room = GameMain.get_room_by_id(room_id)

    if room.user_channels.get(int(user_id)) is not None:
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


def result(message):
    answer = message.content['answer']
    room_id = int(message.content['room'])
    room = GameMain.get_room_by_id(room_id)
    user_id = int(message.content['user_id'])

    if answer == room.current_task.correct_answer:
        room.user_score[user_id] += 1
    else:
        room.user_score[user_id] += 1

    room.current_task_no += 1

    if room.task_no == room.task_limit:
        max_score = max(room.user_score, key=room.user_score.get)
        room.user_channels[max_score].send({'text': json.dumps({'ifwinner': True})})

        for u in room.user_channels:
            if u != max_score:
                room.user_channels[u].send({'text':json.dumps({'ifwinner': False})})

        room.current_task_no = 0
        room.game_is_online = False
    else:
        task = room.make_current_task()
        for u in room.user_channels:
            room.user_channels[u].send({'text': json.dumps({'game_start': True, 'image': str(task.image)})})



import json

from channels import Channel, Group

from cupper.room import GameMain


def ws_connect(message):
    message.reply_channel.send({'accept': True})


def ws_receive(message):
    message_text = json.loads(message['text'])
    message_to_another_channel = message_text
    message_to_another_channel['reply_channel'] = message.content['reply_channel']

    Channel("cupper.receive").send(message_to_another_channel)


def ws_disconnect(message):
    GameMain.try_to_delete_user_from_rooms(message.reply_channel)
    GameMain.update_user_group()


def room_join(message):
    user_id = message.content['user_id']
    room_id = int(message.content['room'])
    room = GameMain.get_room_by_id(room_id)

    if room.add_user_channel(user_id, message.reply_channel):
        room.update_user_group()

    if not room.game_is_online:
        if room.is_busy:
            room.start_game()
            room.continue_game_with_next_question()


def room_leave(message):
    user_id = message.content['user_id']
    room_id = int(message.content['room'])
    room = GameMain.get_room_by_id(room_id)

    if room.user_channels.get(int(user_id)) is not None:
        ch = room.user_channels[int(user_id)]
        ch.send({'text': json.dumps({'user_leave': True})})
        del room.user_channels[int(user_id)]

    room.update_user_group()


def result(message):
    answer = message.content['answer']
    room_id = int(message.content['room'])
    room = GameMain.get_room_by_id(room_id)
    user_id = int(message.content['user_id'])

    room.check_answer(user_id, answer)
    room.continue_game_with_next_question()

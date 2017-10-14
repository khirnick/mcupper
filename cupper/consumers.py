import json

from channels import Channel, Group

from cupper.game import GameManager, Room


def ws_connect(message):
    message.reply_channel.send({'accept': True})


def ws_receive(message):
    message_text = json.loads(message['text'])
    message_to_another_channel = message_text
    message_to_another_channel['reply_channel'] = message.content['reply_channel']

    Channel("cupper.receive").send(message_to_another_channel)


def ws_disconnect(message):
    #FinalGameMain.delete_disconnected_user_from_rooms(message.reply_channel)
    #FinalGameMain.update_user_group()
    #GameMain.delete_disconnected_user_from_rooms(message.reply_channel)
    #GameMain.update_user_group()
    pass


def room_join(message):
    user_id = int(message.content['user_id'])
    room_id = int(message.content['room'])

    room = None

    if message.content['room_type'] == Room.FINAL_NAME:
        room = GameManager.get_final_game().get_room_by_id(room_id)
    else:
        room = GameManager.get_qualifying_game().get_room_by_id(room_id)

    if room.add_user_channel(user_id, message.reply_channel):
        room.update_user_group()

    if not room.game_is_online:
        if room.is_busy:
            room.start_game()


def room_leave(message):
    user_id = int(message.content['user_id'])
    room_id = int(message.content['room'])

    room = None

    if message.content['room_type'] == Room.FINAL_NAME:
        room = GameManager.get_final_game().get_room_by_id(room_id)
    else:
        room = GameManager.get_qualifying_game().get_room_by_id(room_id)

    room.delete_left_user_by_user_id(user_id)
    room.update_user_group()


def room_answer(message):
    answer = message.content['answer']
    room_id = int(message.content['room'])
    user_id = int(message.content['user_id'])

    room = None

    print(message.content['room_type'])

    if message.content['room_type'] == Room.FINAL_NAME:
        room = GameManager.get_final_game().get_room_by_id(room_id)
    else:
        room = GameManager.get_qualifying_game().get_room_by_id(room_id)

    room.check_answer(user_id, answer)
    room.continue_game_with_next_question()

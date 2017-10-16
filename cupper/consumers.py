import json

from channels import Channel

from game.game_manager import GameManager


def ws_connect(message):
    message.reply_channel.send({'accept': True})


def ws_receive(message):
    message_text = json.loads(message['text'])
    message_to_another_channel = message_text
    message_to_another_channel['reply_channel'] = message.content['reply_channel']

    Channel("cupper.receive").send(message_to_another_channel)


def ws_disconnect(message):
    GameManager.delete_disconnected_users_from_all_rooms_in_all_games(message.reply_channel)


def room_join(message):
    user_id = int(message.content['user_id'])
    room_id = int(message.content['room_id'])
    room_type = message.content['room_type']

    room = GameManager.get_room_based_on_type_and_id(room_type, room_id)

    if room.add_user_channel(user_id, message.reply_channel):
        room.update_user_group()

    if not room.game_is_online:
        if room.is_busy:
            room.start_game()


def room_leave(message):
    user_id = int(message.content['user_id'])
    room_id = int(message.content['room_id'])
    room_type = message.content['room_type']

    room = GameManager.get_room_based_on_type_and_id(room_type, room_id)

    room.delete_left_user_by_user_id(user_id)
    room.update_user_group()


def room_answer(message):
    answer = message.content['answer']
    room_id = int(message.content['room_id'])
    user_id = int(message.content['user_id'])
    room_type = message.content['room_type']

    room = GameManager.get_room_based_on_type_and_id(room_type, room_id)

    room.check_answer(user_id, answer)
    room.continue_game_with_next_question()

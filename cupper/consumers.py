"""
Модуль для обработки websocket запросов
Используется фреймворк django-channels
"""

import json

from channels import Channel
from channels.auth import channel_session_user_from_http, channel_session_user

from game.game_manager import GameManager


@channel_session_user_from_http
def ws_connect(message):
    """
    Подтверждение на установку соединения пользователя
    :param message: полное сообщение со всей информацией
    """

    message.reply_channel.send({'accept': True})


@channel_session_user
def ws_receive(message):
    """
    Реакция на отправку сообщения пользователем
    Распарсивание сообщение в формате JSON

    Происходит перенаправление на другой канал - на кастомный, который со стороны клиента
    указан в 'command'
    :param message: полное сообщение со всей информацией
    """

    message_text = json.loads(message['text'])

    message_to_another_channel = message_text
    message_to_another_channel['reply_channel'] = message.content['reply_channel']

    Channel("cupper.receive").send(message_to_another_channel)


@channel_session_user
def ws_disconnect(message):
    """
    Реакция при отсоединении пользователя

    Происходит отсоединение от всех комнат в каждой игре
    :param message: полное сообщение со всей информацией
    """

    GameManager.delete_disconnected_users_from_all_rooms_in_all_games(message.reply_channel)


@channel_session_user
def room_join(message):
    """
    Реакция при присоединении игрока к комнате

    Происходит обновление списка пользователей, который отсылается всем пользователям
    в комнате
    Когда комната заполнена, начинается игра
    :param message: полное сообщение со всей информацией
    """

    user_id = int(message.content['user_id'])
    room_id = int(message.content['room_id'])
    room_type = message.content['room_type']

    room = GameManager.get_room_based_on_type_and_id(room_type, room_id)

    if room.add_user_channel(user_id, message.reply_channel):
        room.update_user_group()

    if not room.game_is_online:
        if room.is_busy:
            room.start_game()


@channel_session_user
def room_leave(message):
    """
    Реакция при отсоединении от комнаты

    Пользователь удаляется из комнаты
    Всем остальным отсылается новый список пользователей в комнате
    :param message: полное сообщение со всей информацией
    """

    user_id = int(message.content['user_id'])
    room_id = int(message.content['room_id'])
    room_type = message.content['room_type']

    room = GameManager.get_room_based_on_type_and_id(room_type, room_id)

    room.delete_left_user_by_user_id(user_id)
    room.update_user_group()


@channel_session_user
def room_answer(message):
    """
    Реакция на пришедший ответ от пользователя

    Проверка на корректность
    Продолжение игры с новым заданием
    :param message: полное сообщение со всей информацией
    """

    answer = message.content['answer']
    room_id = int(message.content['room_id'])
    user_id = int(message.content['user_id'])
    room_type = message.content['room_type']

    room = GameManager.get_room_based_on_type_and_id(room_type, room_id)

    room.check_answer(user_id, answer)
    room.continue_game_with_next_question()

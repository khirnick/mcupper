import json

from django.contrib.auth.models import User

from game.models import Task
from mcupper import settings


class Room:
    """
    Класс комнаты
    Основная логика игры выполняется здесь
    """

    FINAL_NAME = 'final'
    DEFAULT_NAME = 'default'
    DEFAULT_TASK_LIMIT = 20
    DEFAULT_MAX_CHANNELS = 2

    def __init__(self, id_room, type_room, game_manager_ref,
                 task_limit=DEFAULT_TASK_LIMIT,
                 max_channels=DEFAULT_MAX_CHANNELS):
        """
        Инициализация объекта комнаты
        :param id_room: номер комнаты
        :param type_room: тип комнаты
        :param game_manager_ref: ссылка на менеджер игры
        :param task_limit: количество заданий в игре
        :param max_channels: максимальное количество игроков в комнате
        """

        self.__game_manager_ref = game_manager_ref
        self.__user_channels = {}
        self.__user_scores = {}
        self.current_task_no = 0
        self.task_limit = task_limit
        self.game_is_online = False
        self.max_channels = max_channels
        self.id = id_room
        self.current_task = None
        self.type = type_room
        self.private_room = False

        self.make_room_private() if self.type == Room.FINAL_NAME else self.make_room_public()

    def make_room_private(self):
        """
        Сделать комнату приватной
        Для финального раунда
        """

        self.private_room = True

    def make_room_public(self):
        """
        Сделать комнату публичной
        """

        self.private_room = False

    def update_current_task(self):
        """
        Обновить текущее задание в комнате
        """

        self.current_task = Task.get_random_task()

        return self.current_task

    @property
    def is_busy(self):
        """
        Проверка на загруженность комнаты
        :return: является ли комната загруженной - True/False
        """

        if len(self.__user_channels) == self.max_channels:
            return True

    def add_user_channel(self, user_id, user_channel):
        """
        Добавить пользователя в комнату, основываясь на его номере и канале
        :param user_id: номер пользователя
        :param user_channel: канал (websocket)
        :return: добавлен ли пользователь - True/False
        """

        if self.is_busy:
            return False

        if self.private_room:
            if user_id not in self.__game_manager_ref.allowed_users_id_for_final[self.id]:
                return False

        user = self.__user_channels.get(user_id)

        if user is None:
            self.__user_channels[user_id] = user_channel

        return True

    @property
    def is_empty(self):
        return len(self.__user_channels) == 0

    def send_to_all_users_over_websocket(self, data):
        """
        Отправить сообщение всем пользователем по websocket-у
        Отправлять данные обязательно в виде json

        Формат отправки: {'text': json_data}
        :param data: данные
        """

        for user_id, user_channel in self.__user_channels.items():
            user_channel.send({'text': json.dumps(data)})

    def send_to_user_over_websocket_by_id(self, user_id, data):
        """
        Отправить данные единичному пользователю по websocket-у
        Отправлять данные обязательно в виде json

        Формат отправки: {'text': json_data}
        :param user_id: номер пользователя
        :param data: данные
        """

        user_channel = self.__user_channels.get(user_id)

        if user_channel is not None:
            user_channel.send({'text': json.dumps(data)})

    def get_user_id_of_winner(self):
        """
        Получить номер победителя
        """

        return max(self.__user_scores, key=self.__user_scores.get)

    def check_answer(self, user_id_answered, answer):
        """
        Проверить ответ на корректность
        Если пользователь ответил правильно, то внутрикомнатный счет увеличивается на 1
        Иначе - уменьшается на 1
        :param user_id_answered: номер отвечающего пользователя
        :param answer: ответ, который ввел пользователь
        """

        if answer == self.current_task.correct_answer:
            self.__user_scores[user_id_answered] += 1
        else:
            self.__user_scores[user_id_answered] -= 1

    def reset_room(self):
        """
        Очистить комнату после игры
        """

        self.game_is_online = False
        self.__user_channels.clear()
        self.__user_scores.clear()
        self.current_task_no = 0

    def delete_left_user_by_user_id(self, user_id):
        """
        Удалить пользователя из комнаты, который покинул ее - комнату
        :param user_id: номер пользователя
        """

        self.send_to_user_over_websocket_by_id(user_id, {'user_leave': True})
        self.__user_channels.pop(user_id, None)

    def delete_disconnected_user_from_room(self, channel):
        """
        Удалить отключившегося пользователя из комнаты
        :param channel: канал (websocket)
        """

        for user_id, user_channel in self.__user_channels.items():
            if str(channel) == str(user_channel):
                self.__user_channels.pop(user_id, None)
                break

    def update_user_group(self):
        """
        Обновить списко пользователей в комнате
        """

        user_group = ''
        for user_id, channel in self.__user_channels.items():
            username = User.objects.get(id=user_id).username
            user_group += "{0}, ".format(username)

        self.send_to_all_users_over_websocket({'users_group': user_group.rstrip(', ')})

    def create_user_scores_dict(self):
        """
        Создать словарь с очками

        Вид: {'user_id': score}
        """

        for user_id, channel in self.__user_channels.items():
            self.__user_scores[int(user_id)] = 0

    def start_game(self):
        """
        Начать игру при заполнении комнаты
        """

        if not self.game_is_online and self.is_busy:
            self.create_user_scores_dict()
            self.game_is_online = True

            self.continue_game_with_next_question()

    def continue_game_with_next_question(self):
        """
        Продолжить игру

        При окончании игры - превышении кол-во допустимых заданий в комнате - игра заканчивается
        и отсылается заключительная информация
        """

        if not self.game_is_online:
            return

        if self.current_task_no == self.task_limit:
            self.send_complete_info_about_game()
            self.reset_room()
        else:
            task = self.update_current_task()
            self.send_to_all_users_over_websocket({'game_start': True, 'image': settings.MEDIA_URL + str(task.image)})
            self.current_task_no += 1

    def send_complete_info_about_game(self):
        """
        Отправить заключительную информацию после окончания игры

        Победитель добавляется в список игроков, допущенных до финала
        Также высылается ссылка на финальную комнату

        Проигравшим отправляется сообщение, что он ипроиграли
        """

        user_id_winner = self.get_user_id_of_winner()

        if self.type == Room.DEFAULT_NAME:
            final_room = self.__game_manager_ref.get_final_game().is_free_rooms()

            self.__game_manager_ref.add_user_id_to_final_room(self.id, user_id_winner)

            final_room_id = final_room.id

            url_to_final_room = settings.ROOM_URLS['final_room'] + str(final_room_id)
            self.send_to_user_over_websocket_by_id(user_id_winner, {'user_is_winner': True,
                                                                    'link_to_final_room': url_to_final_room})

        else:
            user_winner = User.objects.get(pk=user_id_winner)
            user_winner.profile.score += 1
            user_winner.save()

            self.__game_manager_ref.allowed_users_id_for_final.clear()

            self.send_to_user_over_websocket_by_id(user_id_winner, {'user_is_winner': True})

        for user_id, channel in self.__user_channels.items():
            if user_id != user_id_winner:
                self.send_to_user_over_websocket_by_id(user_id, {'user_is_loser': True})

import json

from django.contrib.auth.models import User

from game.models import Task
from mcupper import settings


class Room:
    FINAL_NAME = 'final'
    DEFAULT_NAME = 'default'
    DEFAULT_TASK_LIMIT = 20
    DEFAULT_MAX_CHANNELS = 2

    def __init__(self, id_room, type_room, game_manager_ref,
                 task_limit=DEFAULT_TASK_LIMIT,
                 max_channels=DEFAULT_MAX_CHANNELS):
        self.game_manager_ref = game_manager_ref
        self.current_task_no = 0
        self.task_limit = task_limit
        self.game_is_online = False
        self.max_channels = max_channels
        self.user_channels = {}
        self.user_scores = {}
        self.id = id_room
        self.current_task = None
        self.type = type_room
        self.private_room = False

        self.make_room_private() if self.type == Room.FINAL_NAME else self.make_room_public()

    def make_room_private(self):
        self.private_room = True

    def make_room_public(self):
        self.private_room = False

    def update_current_task(self):
        self.current_task = Task.get_random_task()
        return self.current_task

    @property
    def is_busy(self):
        if len(self.user_channels) == self.max_channels:
            return True

    def add_user_id_to_potential_member(self, user_id):
        self.user_channels[user_id] = None

    def add_user_channel(self, user_id, user_channel):
        if self.is_busy:
            return False

        if self.private_room:
            if user_id not in self.game_manager_ref.allowed_users_id_for_final[self.id]:
                return False

        user = self.user_channels.get(user_id)

        if user is None:
            self.user_channels[user_id] = user_channel

        return True

    def send_to_all_users_over_websocket(self, data):
        for user_id, user_channel in self.user_channels.items():
            user_channel.send({'text': json.dumps(data)})

    def send_to_user_over_websocket_by_id(self, user_id, data):
        user_channel = self.user_channels.get(user_id)

        if user_channel is not None:
            user_channel.send({'text': json.dumps(data)})

    def get_user_id_of_winner(self):
        return max(self.user_scores, key=self.user_scores.get)

    def check_answer(self, user_id_answered, answer):
        if answer == self.current_task.correct_answer:
            self.user_scores[user_id_answered] += 1
        else:
            self.user_scores[user_id_answered] += 1

    def reset_room(self):
        self.game_is_online = False
        self.user_channels.clear()
        self.user_scores.clear()
        self.current_task_no = 0

    def delete_left_user_by_user_id(self, user_id):
        self.send_to_user_over_websocket_by_id(user_id, {'user_leave': True})
        self.user_channels.pop(user_id, None)

    def delete_disconnected_user_from_room(self, channel):
        for user_id, user_channel in self.user_channels.items():
            if str(channel) == str(user_channel):
                self.user_channels.pop(user_id, None)
                break

    def update_user_group(self):
        user_group = ''
        for user_id, channel in self.user_channels.items():
            username = User.objects.get(id=user_id).username
            user_group += "{0}, ".format(username)

        self.send_to_all_users_over_websocket({'user_id': user_group.rstrip(', ')})

    def create_user_scores_dict(self):
        for user_id, channel in self.user_channels.items():
            self.user_scores[int(user_id)] = 0

    def start_game(self):
        if not self.game_is_online and self.is_busy:
            self.create_user_scores_dict()
            self.game_is_online = True

            self.continue_game_with_next_question()

    def continue_game_with_next_question(self):
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
        user_id_winner = self.get_user_id_of_winner()

        if self.type == Room.DEFAULT_NAME:
            final_room = self.game_manager_ref.get_final_game().is_free_rooms()

            self.game_manager_ref.add_user_id_to_final_room(self.id, user_id_winner)

            final_room_id = final_room.id

            url_to_final_room = settings.ROOM_URLS['final_room'] + str(final_room_id)
            self.send_to_user_over_websocket_by_id(user_id_winner, {'ifwinner': True,
                                                                    'link_to_final_room': url_to_final_room})
        else:
            user_winner = User.objects.get(pk=user_id_winner)
            user_winner.profile.score += 1
            user_winner.save()

            self.game_manager_ref.allowed_users_id_for_final.clear()

            self.send_to_user_over_websocket_by_id(user_id_winner, {'ifwinner': True})

        for user_id, channel in self.user_channels.items():
            if user_id != user_id_winner:
                self.send_to_user_over_websocket_by_id(user_id, {'ifloser': True})

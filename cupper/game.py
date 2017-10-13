import json

from cupper.models import Task


class Game:
    def __init__(self):
        self.rooms = []

    def add_room(self, type='default'):
        new_room = self.rooms.append(Room(len(self.rooms), type))
        return new_room

    def is_free_rooms(self):
        for room in self.rooms:
            if not room.is_busy:
                return room

    def get_room_by_id(self, id):
        return self.rooms[id]

    def delete_disconnected_user_from_rooms(self, channel):
        for room in self.rooms:
            room.delete_disconnected_user_from_room(channel)

    def update_user_group(self):
        for room in self.rooms:
            room.update_user_group()


class Room:
    def __init__(self, id, type):
        self.current_task_no = 0
        self.task_limit = 5
        self.game_is_online = False
        self.max_channels = 2
        self.user_channels = {}
        self.user_scores = {}
        self.id = id
        self.current_task = None
        if type == "final":
            self.private_room = True
        else:
            self.private_room = False
        self.type = type

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
            if user_id not in self.user_channels:
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
            print(self.user_scores)
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
            user_group += "{0}\n".format(user_id)

        self.send_to_all_users_over_websocket({'user_id': user_group})

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
            self.send_to_all_users_over_websocket({'game_start': True, 'image': str(task.image)})
            self.current_task_no += 1

    def send_complete_info_about_game(self):
        user_id_winner = self.get_user_id_of_winner()

        if self.type == 'default':
            print(self.type)
            final_room = FinalGameMain.is_free_rooms()
            final_room.add_user_id_to_potential_member(user_id_winner)
            final_room_id = final_room.id

            url_to_final_room = "/final_room/" + str(final_room_id)
            self.send_to_user_over_websocket_by_id(user_id_winner, {'ifwinner': True,
                                                                    'link_to_final_room': url_to_final_room})
        else:
            self.send_to_user_over_websocket_by_id(user_id_winner, {'ifwinner': True})

        for user_id, channel in self.user_channels.items():
            if user_id != user_id_winner:
                self.send_to_user_over_websocket_by_id(user_id, {'ifloser': True})


GameMain = Game()
GameMain.add_room()
GameMain.add_room()

FinalGameMain = Game()
r1 = FinalGameMain.add_room('final')
r2 = FinalGameMain.add_room('final')

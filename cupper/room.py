import json

from cupper.models import Task


class Game:
    def __init__(self):
        self.rooms = []

    def add_room(self):
        new_room = self.rooms.append(Room(len(self.rooms)))
        return new_room

    def is_free_rooms(self):
        for room in self.rooms:
            if not room.is_busy:
                return room

    def get_room_by_id(self, id):
        return self.rooms[id]


class Room:
    def __init__(self, id):
        self.current_task_no = 0
        self.task_limit = 5
        self.game_is_online = False
        self.max_channels = 2
        self.user_channels = {}
        self.user_scores = {}
        self.id = id
        self.current_task = None

    def update_current_task(self):
        self.current_task = Task.get_random_task()
        return self.current_task

    @property
    def is_busy(self):
        if len(self.user_channels) == self.max_channels:
            return False

    def add_user_channel(self, user_id, user_channel):
        if len(self.user_channels) >= self.max_channels:
            return False

        user = self.user_channels.get(user_id)

        if user is None:
            self.user_channels[int(user_id)] = user_channel

        return True

    def send_to_all_users_over_websocket(self, data):
        for user_id, user_channel in self.user_channels.items():
            user_channel.send({'text': json.dumps(data)})

    def send_to_user_over_websocket_by_id(self, user_id, data):
        user_channel = self.user_channels.get(user_id)

        if user_channel is not None:
            user_channel.send({'text': json.dumps(data)})

    def get_max_score(self):
        return max(self.user_scores, key=self.user_scores.get)

    def check_answer(self, user_id_answered, answer):
        if answer == self.current_task.correct_answer:
            self.user_scores[user_id_answered] += 1
        else:
            self.user_scores[user_id_answered] += 1

        self.current_task_no += 1

    def reset_room(self):
        self.game_is_online = False
        self.user_channels.clear()
        self.user_scores.clear()
        self.current_task_no = 0



GameMain = Game()
GameMain.add_room()
GameMain.add_room()
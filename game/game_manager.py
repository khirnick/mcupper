from game.game import Game
from game.room import Room


class GameManager:
    def __init__(self):
        self.allowed_users_id_for_final = {}

        self.qualifying_game = Game(Room.DEFAULT_NAME)
        self.final_game = Game(Room.FINAL_NAME)

        self.qualifying_game.add_room(self)
        self.qualifying_game.add_room(self)

        self.final_game.add_room(self)
        self.final_game.add_room(self)

    def get_qualifying_game(self):
        return self.qualifying_game

    def get_final_game(self):
        return self.final_game

    def add_user_id_to_final_room(self, room_id, user_id):
        if user_id in self.allowed_users_id_for_final:
            self.allowed_users_id_for_final[room_id].append(user_id)
        else:
            self.allowed_users_id_for_final[room_id] = [user_id]


GameManager = GameManager()

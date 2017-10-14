from game.room import Room


class Game:
    def __init__(self, rooms_type):
        self.rooms = []
        self.rooms_type = rooms_type

    def add_room(self, game_manager_ref):
        new_room = self.rooms.append(Room(id_room=len(self.rooms), type_room=self.rooms_type,
                                          game_manager_ref=game_manager_ref))
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
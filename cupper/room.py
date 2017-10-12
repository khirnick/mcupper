from cupper.models import Task


class Game:
    def __init__(self):
        self.rooms = []

    def add_room(self):
        new_room = self.rooms.append(Room(len(self.rooms)))
        return new_room

    def is_free_rooms(self):
        for room in self.rooms:
            if not room.is_busy():
                return room

    def get_room_by_id(self, id):
        return self.rooms[id]


class Room:
    def __init__(self, id):
        self.max_channels = 2
        self.user_channels = {}
        self.id = id
        self.current_task = None

    def make_current_task(self):
        task = Task.objects.get(pk=4)
        self.current_task = task
        print(self.current_task.image)
        return self.current_task

    def is_busy(self):
        if len(self.user_channels) == 5:
            return False

    def add_user_channel(self, user_id, user_channel):
        if len(self.user_channels) >= 5:
            return False

        user = self.user_channels.get(user_id)

        if user is None:
            self.user_channels[int(user_id)] = user_channel

        return True


GameMain = Game()
GameMain.add_room()
GameMain.add_room()
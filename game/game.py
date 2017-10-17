from game.room import Room


class Game:
    """
    Класс игры - финальной или отборочной, содержащий список комнат
    """

    def __init__(self, rooms_type, game_manager_ref):
        """
        Инициализация объекта игры
        :param rooms_type: тип комнат - финальные, отборочные
        """

        self.rooms = []
        self.rooms_type = rooms_type
        self.game_manager_ref = game_manager_ref

    def add_room(self):
        """
        Добавить комнату в игру
        :param game_manager_ref: ссылка на менеджер игр
        :return: объект комнаты
        """

        self.rooms.append(Room(id_room=len(self.rooms), type_room=self.rooms_type,
                               game_manager_ref=self.game_manager_ref))

        added_room = self.rooms[-1]

        return added_room

    def is_free_rooms(self):
        """
        Поиск первой доступной комнаты

        Если все комнаты заняты, то создается новая
        :return: свободная комната
        """

        for room in self.rooms:
            if not room.is_busy:
                return room

        new_room = self.add_room()

        return new_room

    def get_room_by_id(self, id):
        """
        Получить комнату по номеру
        :param id: номер комнаты
        :return: объект комнаты
        """

        return self.rooms[id]

    def delete_disconnected_user_from_rooms(self, channel):
        """
        Удалить отключенного пользователя из комнат
        :param channel: канал (websocket)
        """

        for room in self.rooms:
            room.delete_disconnected_user_from_room(channel)

    def update_user_group(self):
        """
        Обновить список пользователей в комнате
        """

        for room in self.rooms:
            room.update_user_group()
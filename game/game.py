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

        new_room_id = self.find_first_not_busy_id_for_room()

        if new_room_id is None:
            return None

        self.rooms.append(Room(id_room=new_room_id, type_room=self.rooms_type,
                               game_manager_ref=self.game_manager_ref))

        added_room = self.rooms[-1]

        return added_room

    def find_first_not_busy_id_for_room(self):
        for potential_id in range(Room.MAX_ROOMS_IN_GAME):
            room = self.get_room_by_id(potential_id)

            if room is None:
                return potential_id

        return None

    def is_free_rooms(self):
        """
        Поиск первой доступной комнаты

        Если все комнаты заняты, то создается новая
        :return: свободная комната
        """

        self.clean_rooms()

        for room in self.rooms:
            if not room.is_busy and not room.game_is_online:
                print('room id: ', room.id, '; busy: ', room.is_busy, ' ; is online: ', room.game_is_online)
                return room

        new_room = self.add_room()

        if new_room is None:
            return None

        return new_room

    def clean_rooms(self):
        for room in self.rooms:
            if room.is_empty:
                self.rooms.remove(room)

    def get_room_by_id(self, id):
        """
        Получить комнату по номеру
        :param id: номер комнаты
        :return: объект комнаты. Если не найдена, то None
        """

        for room in self.rooms:
            if id == room.id:
                return room

        return None

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
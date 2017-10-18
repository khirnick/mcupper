from django.shortcuts import render

from game.game_manager import GameManager


def game(request):
    """
    Рендеринг первоначальной страницы с комнатами отборочного этапа
    :param request: запрос
    :return: рендер страницы
    """

    first_free_qualifying_room = GameManager.get_qualifying_game().is_free_rooms()

    if first_free_qualifying_room is None:
        return render(request, 'game/game.html', {'rooms_exhausted': True})

    return render(request, 'game/game.html', {'room': first_free_qualifying_room})


def room(request, room_id):
    """
    Рендеринг комнаты отборочного этапа
    :param request: запрос
    :param room_id: номер конаты
    """

    qualifying_room = GameManager.get_qualifying_game().get_room_by_id(int(room_id))
    return render(request, 'game/room.html', {'room': qualifying_room})


def final_room(request, room_id):
    """
    Рендеринг комнаты финального этапа
    :param request: запрос
    :param room_id: номер конаты
    """

    final_room = GameManager.get_final_game().get_room_by_id(int(room_id))
    return render(request, 'game/room.html', {'room': final_room})
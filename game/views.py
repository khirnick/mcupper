from django.shortcuts import render

from game.game_manager import GameManager


def game(request):
    room = GameManager.get_qualifying_game().is_free_rooms()
    return render(request, 'game/game.html', {'room': room})


def room(request, room_id):
    room = GameManager.get_qualifying_game().get_room_by_id(int(room_id))
    return render(request, 'game/room.html', {'room': room})


def final_room(request, room_id):
    room = GameManager.get_final_game().get_room_by_id(int(room_id))
    return render(request, 'game/room.html', {'room': room})
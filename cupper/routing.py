from channels import route

from .consumers import ws_connect, ws_receive, ws_disconnect, room_join, room_leave

websocket_routing = [
    route('websocket.connect', ws_connect),
    route('websocket.receive', ws_receive),
    route('websocket.disconnect', ws_disconnect),
]

custom_routing = [
    route("cupper.receive", room_join, command="^join$"),
    route("cupper.receive", room_leave, command="^leave$"),
]

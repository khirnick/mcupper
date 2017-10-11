from channels.routing import route, include

channel_routing = [
    include("cupper.routing.websocket_routing", path=r"^/cupper/stream"),
    include("cupper.routing.custom_routing"),
]
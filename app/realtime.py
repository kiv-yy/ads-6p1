from collections import defaultdict

from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, claim_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[claim_id].append(websocket)

    def disconnect(self, claim_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(claim_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and claim_id in self.active_connections:
            del self.active_connections[claim_id]

    async def broadcast_to_claim(self, claim_id: int, payload: dict) -> None:
        for connection in list(self.active_connections.get(claim_id, [])):
            await connection.send_json(payload)


chat_manager = ChatConnectionManager()

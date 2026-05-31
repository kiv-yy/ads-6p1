from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import get_dev_current_user
from app.models import ChatMessage, User
from app.services.auth import AuthFlowService
from app.services.chat import ChatService, chat_manager


router = APIRouter(tags=["Chat"])


@router.get("/claims/{claim_id}/chat", response_model=list[schemas.ChatMessageRead])
def list_chat_messages(
    claim_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> list[ChatMessage]:
    return ChatService(db).list_messages(claim_id, current_user, skip=skip, limit=limit)


@router.get("/claims/{claim_id}/chat/info", response_model=schemas.ChatRoomInfo)
def read_chat_room_info(
    claim_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> schemas.ChatRoomInfo:
    return ChatService(db).get_room_info(claim_id, current_user)


@router.post("/claims/{claim_id}/chat", response_model=schemas.ChatMessageRead, status_code=status.HTTP_201_CREATED)
def send_chat_message(
    claim_id: UUID,
    message_in: schemas.ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> ChatMessage:
    return ChatService(db).send_message_by_claim_id(claim_id, current_user, message_in)


@router.post("/claims/{claim_id}/chat/upload", response_model=schemas.PostImageCreate)
async def upload_chat_attachment(
    claim_id: UUID,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> schemas.PostImageCreate:
    return await ChatService(db).upload_attachment(claim_id, current_user, request, file)


@router.websocket("/ws/claims/{claim_id}/chat")
async def realtime_chat(
    websocket: WebSocket,
    claim_id: UUID,
    token: str | None = Query(default=None),
    current_user_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> None:
    user = AuthFlowService(db).resolve_websocket_user(token, current_user_id)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    service = ChatService(db)
    try:
        claim, chat = service.get_realtime_session(claim_id, user)
    except Exception:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await chat_manager.connect(chat.id, websocket)
    try:
        await websocket.send_json(
            {
                "type": "connected",
                "claim_id": str(claim_id),
                "chat_id": str(chat.id),
                "user_id": str(user.id),
                "encryption": "client-side end-to-end; server stores ciphertext only",
            }
        )
        while True:
            payload = await websocket.receive()
            if "text" in payload and isinstance(payload["text"], str):
                try:
                    message_in = schemas.ChatMessageCreate.model_validate_json(payload["text"])
                except ValueError:
                    message_in = schemas.ChatMessageCreate(content=payload["text"])
            else:
                message_in = schemas.ChatMessageCreate(content="")
            message = service.send_message(claim, sender_id=user.id, message_in=message_in)
            event = {"type": "message", "message": schemas.ChatMessageRead.model_validate(message).model_dump(mode="json")}
            await chat_manager.broadcast_to_chat(chat.id, event)
    except WebSocketDisconnect:
        chat_manager.disconnect(chat.id, websocket)
    except ValueError:
        await websocket.send_json({"type": "error", "detail": "Invalid encrypted message payload"})
        chat_manager.disconnect(chat.id, websocket)
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)

from pathlib import Path
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app import schemas
from app.core.security import AuthService
from app.db.database import get_db
from app.dependencies import ApiError, get_dev_current_user
from app.models import ChatMessage, User
from app.services.authorization import AuthorizationPolicy
from app.services.chat import ChatRepository, chat_manager
from app.services.claims import ClaimRepository


router = APIRouter(tags=["Chat"])
UPLOAD_DIR = Path("app/static/uploads")
ALLOWED_CHAT_FILE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "application/pdf": ".pdf",
}
MAX_CHAT_FILE_SIZE = 8 * 1024 * 1024


@router.get("/claims/{claim_id}/chat", response_model=list[schemas.ChatMessageRead])
def list_chat_messages(
    claim_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> list[ChatMessage]:
    claim = ClaimRepository(db).get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_chat(claim, current_user):
        raise ApiError.forbidden("Chat is available only for accepted claims")
    return ChatRepository(db).list_messages(claim=claim, skip=skip, limit=limit)


@router.get("/claims/{claim_id}/chat/info", response_model=schemas.ChatRoomInfo)
def read_chat_room_info(
    claim_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> schemas.ChatRoomInfo:
    claim = ClaimRepository(db).get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_chat(claim, current_user):
        raise ApiError.forbidden("Chat is available only for accepted claims")
    chat = ChatRepository(db).get_or_create_for_claim(claim)
    return schemas.ChatRoomInfo(
        claim_id=claim.id,
        item_id=claim.item_id,
        chat_id=chat.id,
        participants=[claim.item.owner_id, claim.claimant_id],
        is_realtime_enabled=True,
        encryption="client-side end-to-end; server stores ciphertext in chat_messages.isi_pesan",
        active_connections=chat_manager.count_for_chat(chat.id),
        status=claim.status,
        item=claim.item,
        claim_user=claim.claimant,
        item_user_id=claim.item.owner_id,
    )


@router.post("/claims/{claim_id}/chat", response_model=schemas.ChatMessageRead, status_code=status.HTTP_201_CREATED)
def send_chat_message(
    claim_id: UUID,
    message_in: schemas.ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> ChatMessage:
    claim = ClaimRepository(db).get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_chat(claim, current_user):
        raise ApiError.forbidden("Chat is available only for accepted claims")
    return ChatRepository(db).create_message(claim, sender_id=current_user.id, message_in=message_in)


@router.post("/claims/{claim_id}/chat/upload", response_model=schemas.PostImageCreate)
async def upload_chat_attachment(
    claim_id: UUID,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> schemas.PostImageCreate:
    claim = ClaimRepository(db).get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_chat(claim, current_user):
        raise ApiError.forbidden("Chat is available only for accepted claims")

    extension = ALLOWED_CHAT_FILE_TYPES.get(file.content_type or "")
    if extension is None:
        raise ApiError.bad_request("File chat harus berupa gambar JPG, PNG, WEBP, GIF, atau PDF")

    content = await file.read()
    if len(content) > MAX_CHAT_FILE_SIZE:
        raise ApiError.bad_request("Ukuran file chat maksimal 8 MB")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"chat-{uuid4()}{extension}"
    target = UPLOAD_DIR / filename
    target.write_bytes(content)

    file_url = str(request.base_url).rstrip("/") + f"/static/uploads/{filename}"
    return schemas.PostImageCreate(image_url=file_url)


@router.websocket("/ws/claims/{claim_id}/chat")
async def realtime_chat(
    websocket: WebSocket,
    claim_id: UUID,
    token: str | None = Query(default=None),
    current_user_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
) -> None:
    try:
        user = AuthService(db).get_current_user(token) if token else None
    except Exception:
        user = None
    if user is None and current_user_id is not None:
        user = db.get(User, current_user_id)
    claim = ClaimRepository(db).get(claim_id)
    if not user or not claim or not AuthorizationPolicy.can_chat(claim, user):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    chat = ChatRepository(db).get_or_create_for_claim(claim)
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
            message = ChatRepository(db).create_message(claim, sender_id=user.id, message_in=message_in)
            event = {"type": "message", "message": schemas.ChatMessageRead.model_validate(message).model_dump(mode="json")}
            await chat_manager.broadcast_to_chat(chat.id, event)
    except WebSocketDisconnect:
        chat_manager.disconnect(chat.id, websocket)
    except ValueError:
        await websocket.send_json({"type": "error", "detail": "Invalid encrypted message payload"})
        chat_manager.disconnect(chat.id, websocket)
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)

from fastapi import APIRouter, Depends, Query, Response, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session

from app import schemas
from app.db.database import get_db
from app.dependencies import ApiError, get_dev_current_user
from app.models import ChatMessage, Claim, Item, ItemStatus, ItemType, User, UserRole
from app.services.item_service import AuthorizationPolicy, ChatRepository, ClaimRepository, ItemRepository, chat_manager
from app.services.user_service import UserRepository


router = APIRouter(tags=["Items"])


@router.post("/items", response_model=schemas.ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    item_in: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Item:
    return ItemRepository(db).create(item_in, owner_id=current_user.id)


@router.get("/items", response_model=list[schemas.ItemRead])
def list_items(
    category: str | None = None,
    item_type: ItemType | None = Query(default=None, alias="type"),
    item_status: ItemStatus | None = Query(default=None, alias="status"),
    location: str | None = None,
    keyword: str | None = None,
    q: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[Item]:
    return ItemRepository(db).list(
        category=category,
        item_type=item_type,
        status=item_status,
        location=location,
        keyword=keyword or q,
        skip=skip,
        limit=limit,
    )


@router.get("/items/{item_id}", response_model=schemas.ItemRead)
def read_item(item_id: int, db: Session = Depends(get_db)) -> Item:
    item = ItemRepository(db).get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    return item


@router.patch("/items/{item_id}", response_model=schemas.ItemRead)
def update_item(
    item_id: int,
    item_in: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Item:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Not enough permissions")
    return items.update(item, item_in)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_own_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Response:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Not enough permissions")
    items.delete(item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/items/{item_id}/resolve", response_model=schemas.ItemRead)
def resolve_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Item:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Only item owner can resolve this item")
    return items.update(item, schemas.ItemUpdate(status=ItemStatus.RESOLVED))


@router.post("/claims", response_model=schemas.ClaimRead, status_code=status.HTTP_201_CREATED, tags=["Claims"])
def create_claim(
    claim_in: schemas.ClaimCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Claim:
    item = ItemRepository(db).get(claim_in.item_id)
    if not item:
        raise ApiError.not_found("Item")
    if item.owner_id == current_user.id:
        raise ApiError.bad_request("You cannot claim your own item")
    if item.type != ItemType.FOUND.value:
        raise ApiError.bad_request("Only found items can be claimed")
    claims = ClaimRepository(db)
    if claims.get_active_for_item_and_claimant(item.id, current_user.id):
        raise ApiError.bad_request("You already have an active claim for this item")
    return claims.create(claim_in, claimant_id=current_user.id)


@router.get("/items/{item_id}/claims", response_model=list[schemas.ClaimRead], tags=["Claims"])
def list_item_claims(
    item_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> list[Claim]:
    item = ItemRepository(db).get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Only item owner can view item claims")
    return ClaimRepository(db).list_for_item(item_id=item.id, skip=skip, limit=limit)


@router.get("/claims", response_model=list[schemas.ClaimRead], tags=["Claims"])
def list_my_claims(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> list[Claim]:
    if current_user.role == UserRole.ADMIN.value:
        return ClaimRepository(db).list_all(skip=skip, limit=limit)
    return ClaimRepository(db).list_for_user(current_user.id)


@router.patch("/claims/{claim_id}", response_model=schemas.ClaimRead, tags=["Claims"])
def update_claim_status(
    claim_id: int,
    claim_in: schemas.ClaimUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> Claim:
    claims = ClaimRepository(db)
    claim = claims.get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_moderate_claim(claim, current_user):
        raise ApiError.forbidden("Only item owner can moderate claims")
    return claims.update_status(claim, claim_in.status)


@router.get("/claims/{claim_id}/chat", response_model=list[schemas.ChatMessageRead], tags=["Chat"])
def list_chat_messages(
    claim_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> list[ChatMessage]:
    claim = ClaimRepository(db).get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_access_claim(claim, current_user):
        raise ApiError.forbidden("Only claim participants can access this resource")
    if not AuthorizationPolicy.can_chat(claim, current_user):
        raise ApiError.forbidden("Chat is available only for accepted claims")
    return ChatRepository(db).list_messages(claim_id=claim.id, skip=skip, limit=limit)


@router.get("/claims/{claim_id}/chat/info", response_model=schemas.ChatRoomInfo, tags=["Chat"])
def read_chat_room_info(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> schemas.ChatRoomInfo:
    claim = ClaimRepository(db).get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_access_claim(claim, current_user):
        raise ApiError.forbidden("Only claim participants can access this resource")
    if not AuthorizationPolicy.can_chat(claim, current_user):
        raise ApiError.forbidden("Chat is available only for accepted claims")
    return schemas.ChatRoomInfo(
        claim_id=claim.id,
        item_id=claim.item_id,
        participants=[claim.item.owner_id, claim.claimant_id],
        is_realtime_enabled=True,
        encryption="client-side end-to-end; server stores ciphertext only",
        active_connections=chat_manager.count_for_claim(claim.id),
        status=claim.status,
        item=claim.item,
        claim_user=claim.claimant,
        item_user_id=claim.item.owner_id,
    )


@router.post("/claims/{claim_id}/chat", response_model=schemas.ChatMessageRead, status_code=status.HTTP_201_CREATED, tags=["Chat"])
def send_chat_message(
    claim_id: int,
    message_in: schemas.ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_dev_current_user),
) -> ChatMessage:
    claim = ClaimRepository(db).get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_access_claim(claim, current_user):
        raise ApiError.forbidden("Only claim participants can access this resource")
    if not AuthorizationPolicy.can_chat(claim, current_user):
        raise ApiError.forbidden("Chat is available only for accepted claims")
    return ChatRepository(db).create_message(claim, sender_id=current_user.id, message_in=message_in)


@router.websocket("/ws/claims/{claim_id}/chat")
async def realtime_chat(
    websocket: WebSocket,
    claim_id: int,
    current_user_id: int,
    db: Session = Depends(get_db),
) -> None:
    user = UserRepository(db).get(current_user_id)
    claim = ClaimRepository(db).get(claim_id)
    if not user or not claim or not AuthorizationPolicy.can_chat(claim, user):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await chat_manager.connect(claim_id, websocket)
    try:
        await websocket.send_json(
            {
                "type": "connected",
                "claim_id": claim_id,
                "user_id": current_user_id,
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
            event = schemas.ChatMessageRead.model_validate(message).model_dump(mode="json")
            await chat_manager.broadcast_to_claim(claim_id, event)
    except WebSocketDisconnect:
        chat_manager.disconnect(claim_id, websocket)
    except ValueError:
        await websocket.send_json({"type": "error", "detail": "Invalid encrypted message payload"})
        chat_manager.disconnect(claim_id, websocket)
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)

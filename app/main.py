from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, Query, Response, WebSocket, WebSocketDisconnect, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas
from app.auth import AuthService, create_access_token
from app.config import get_settings
from app.crud import AuthorizationPolicy, ChatRepository, ClaimRepository, ItemRepository, UserRepository
from app.database import Base, engine, get_db
from app.realtime import chat_manager


Base.metadata.create_all(bind=engine)

settings = get_settings()
app = FastAPI(
    title="IPB Lost & Found System",
    description="API boilerplate untuk mahasiswa IPB mencari barang hilang dan barang ditemukan di kampus.",
    version="0.1.0",
)


class ApiError:
    @staticmethod
    def not_found(resource: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")

    @staticmethod
    def forbidden(detail: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

    @staticmethod
    def bad_request(detail: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def get_dev_current_user(current_user_id: int = Query(...), db: Session = Depends(get_db)) -> models.User:
    user = UserRepository(db).get(current_user_id)
    if not user:
        raise ApiError.not_found("User")
    if not user.is_active or user.is_blocked:
        raise ApiError.forbidden("User inactive or blocked")
    return user


def get_dev_admin_user(current_user: models.User = Depends(get_dev_current_user)) -> models.User:
    if current_user.role != models.UserRole.ADMIN.value:
        raise ApiError.forbidden("Admin access required")
    return current_user


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/auth/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED, tags=["Auth"])
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)) -> models.User:
    users = UserRepository(db)
    if users.get_by_email(user_in.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    return users.create(user_in)


@app.post("/auth/login", response_model=schemas.Token, tags=["Auth"])
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> schemas.Token:
    user = AuthService(db).authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_blocked:
        raise ApiError.forbidden("User is blocked")

    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(subject=str(user.id), expires_delta=expires_delta)
    return schemas.Token(access_token=access_token)


@app.get("/users/me", response_model=schemas.UserRead, tags=["Users"])
def read_me(current_user: models.User = Depends(get_dev_current_user)) -> models.User:
    return current_user


@app.post("/items", response_model=schemas.ItemRead, status_code=status.HTTP_201_CREATED, tags=["Items"])
def create_item(
    item_in: schemas.ItemCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_dev_current_user),
) -> models.Item:
    return ItemRepository(db).create(item_in, owner_id=current_user.id)


@app.get("/items", response_model=list[schemas.ItemRead], tags=["Items"])
def list_items(
    category: models.ItemCategory | None = None,
    location: str | None = None,
    keyword: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[models.Item]:
    return ItemRepository(db).list(category=category, location=location, keyword=keyword, skip=skip, limit=limit)


@app.get("/items/{item_id}", response_model=schemas.ItemRead, tags=["Items"])
def read_item(item_id: int, db: Session = Depends(get_db)) -> models.Item:
    item = ItemRepository(db).get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    return item


@app.patch("/items/{item_id}", response_model=schemas.ItemRead, tags=["Items"])
def update_item(
    item_id: int,
    item_in: schemas.ItemUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_dev_current_user),
) -> models.Item:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Not enough permissions")
    return items.update(item, item_in)


@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Items"])
def delete_own_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_dev_current_user),
) -> Response:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    if not AuthorizationPolicy.can_manage_item(item, current_user):
        raise ApiError.forbidden("Not enough permissions")
    items.delete(item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/claims", response_model=schemas.ClaimRead, status_code=status.HTTP_201_CREATED, tags=["Claims"])
def create_claim(
    claim_in: schemas.ClaimCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_dev_current_user),
) -> models.Claim:
    item = ItemRepository(db).get(claim_in.item_id)
    if not item:
        raise ApiError.not_found("Item")
    if item.owner_id == current_user.id:
        raise ApiError.bad_request("You cannot claim your own item")
    if item.category != models.ItemCategory.FOUND.value:
        raise ApiError.bad_request("Only found items can be claimed")
    return ClaimRepository(db).create(claim_in, claimant_id=current_user.id)


@app.get("/claims", response_model=list[schemas.ClaimRead], tags=["Claims"])
def list_my_claims(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_dev_current_user),
) -> list[models.Claim]:
    return ClaimRepository(db).list_for_user(current_user.id)


@app.patch("/claims/{claim_id}", response_model=schemas.ClaimRead, tags=["Claims"])
def update_claim_status(
    claim_id: int,
    claim_in: schemas.ClaimUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_dev_current_user),
) -> models.Claim:
    claims = ClaimRepository(db)
    claim = claims.get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_moderate_claim(claim, current_user):
        raise ApiError.forbidden("Only item owner can moderate claims")
    return claims.update_status(claim, claim_in.status)


@app.get("/claims/{claim_id}/chat", response_model=list[schemas.ChatMessageRead], tags=["Chat"])
def list_chat_messages(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_dev_current_user),
) -> list[models.ChatMessage]:
    claim = ClaimRepository(db).get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_access_claim(claim, current_user):
        raise ApiError.forbidden("Only claim participants can access this resource")
    if not AuthorizationPolicy.can_chat(claim, current_user):
        raise ApiError.forbidden("Chat is available only for accepted claims")
    return claim.messages


@app.post("/claims/{claim_id}/chat", response_model=schemas.ChatMessageRead, status_code=status.HTTP_201_CREATED, tags=["Chat"])
def send_chat_message(
    claim_id: int,
    message_in: schemas.ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_dev_current_user),
) -> models.ChatMessage:
    claim = ClaimRepository(db).get(claim_id)
    if not claim:
        raise ApiError.not_found("Claim")
    if not AuthorizationPolicy.can_access_claim(claim, current_user):
        raise ApiError.forbidden("Only claim participants can access this resource")
    if not AuthorizationPolicy.can_chat(claim, current_user):
        raise ApiError.forbidden("Chat is available only for accepted claims")
    return ChatRepository(db).create_message(claim, sender_id=current_user.id, message_in=message_in)


@app.websocket("/ws/claims/{claim_id}/chat")
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
            payload = await websocket.receive_json()
            message_in = schemas.ChatMessageCreate.model_validate(payload)
            message = ChatRepository(db).create_message(claim, sender_id=user.id, message_in=message_in)
            event = schemas.ChatWebSocketEvent(
                message=schemas.ChatMessageRead.model_validate(message),
            ).model_dump(mode="json")
            await chat_manager.broadcast_to_claim(claim_id, event)
    except WebSocketDisconnect:
        chat_manager.disconnect(claim_id, websocket)
    except ValueError:
        await websocket.send_json({"type": "error", "detail": "Invalid encrypted message payload"})
        chat_manager.disconnect(claim_id, websocket)
        await websocket.close(code=status.WS_1003_UNSUPPORTED_DATA)


@app.delete("/admin/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Admin"])
def admin_delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_dev_admin_user),
) -> Response:
    items = ItemRepository(db)
    item = items.get(item_id)
    if not item:
        raise ApiError.not_found("Item")
    items.delete(item)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.patch("/admin/users/{user_id}/block", response_model=schemas.UserRead, tags=["Admin"])
def admin_block_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_dev_admin_user),
) -> models.User:
    users = UserRepository(db)
    user = users.get(user_id)
    if not user:
        raise ApiError.not_found("User")
    return users.block(user)

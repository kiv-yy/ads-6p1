from app.schemas import UserCreate


def test_user_create_schema_accepts_ipb_email() -> None:
    user = UserCreate(email="student@apps.ipb.ac.id", full_name="IPB Student", password="password123")
    assert user.email == "student@apps.ipb.ac.id"

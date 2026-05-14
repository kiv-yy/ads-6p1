from app.models import ItemCategory
from app.schemas import ItemCreate


def test_item_create_schema() -> None:
    item = ItemCreate(
        title="Payung Hitam",
        description="Payung hitam tertinggal di sekitar perpustakaan.",
        category=ItemCategory.FOUND,
        location="Perpustakaan IPB",
    )
    assert item.category == ItemCategory.FOUND

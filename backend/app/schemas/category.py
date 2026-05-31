from uuid import UUID

from pydantic import BaseModel, ConfigDict, computed_field


class CategoryRead(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def category_id(self) -> UUID:
        return self.id

    @computed_field
    @property
    def nama_kategori(self) -> str:
        return self.name

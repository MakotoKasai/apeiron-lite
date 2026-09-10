# タグ：入力検証とレスポンスの構造を定義するPydanticモデル。

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class TagCreate(BaseModel):
    name: str = Field(min_length=1)
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        # 空白だけの入力を拒否する。受理した値の前後の空白はそのまま保持する。
        if not value.strip():
            raise ValueError("name must not be blank")
        return value
class TagUpdate(BaseModel):
    name: str = Field(min_length=1)
    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        # 空白だけの入力を拒否する。受理した値の前後の空白はそのまま保持する。
        if not value.strip():
            raise ValueError("name must not be blank")
        return value
class Tag(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime
class TagWithOrder(BaseModel):
    tag: Tag
    sort_order: int
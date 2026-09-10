# 写真：入力検証とレスポンスの構造を定義するPydanticモデル。

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class PhotoCreate(BaseModel):
    file_path: str = Field(min_length=1)
    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, value: str) -> str:
        # 空白だけの入力を拒否する。受理した値の前後の空白はそのまま保持する。
        if not value.strip():
            raise ValueError("file_path must not be blank")
        return value

class PhotoUpdate(BaseModel):
    file_path: str = Field(min_length=1)
    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, value: str) -> str:
        # 空白だけの入力を拒否する。受理した値の前後の空白はそのまま保持する。
        if not value.strip():
            raise ValueError("file_path must not be blank")
        return value

class Photo(BaseModel):
    id: int
    file_path: str
    created_at: datetime
    updated_at: datetime

class PhotoWithOrder(BaseModel):
    photo: Photo
    sort_order: int

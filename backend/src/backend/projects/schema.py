# プロジェクト：入力検証とレスポンスの構造を定義するPydanticモデル。

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ProjectCreate(BaseModel):
    title: str  = Field(min_length=1)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        # 空白だけの入力を拒否する。受理した値の前後の空白はそのまま保持する。
        if not value.strip():
            raise ValueError("title must not be blank")
        return value

    description: str

class ProjectUpdate(BaseModel):
    title: str= Field(min_length=1)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        # 空白だけの入力を拒否する。受理した値の前後の空白はそのまま保持する。
        if not value.strip():
            raise ValueError("title must not be blank")
        return value

    description: str

class Project(BaseModel):
    id: int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime


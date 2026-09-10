# 関連付けの並び替えAPIで共有するリクエストモデル。範囲判定はサービス側で行う。

from pydantic import BaseModel

class OrderUpdate(BaseModel):
    new_order: int
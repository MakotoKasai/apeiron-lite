# タグ：HTTPリクエストを受け、サービスの結果や例外をAPI応答に変換する。

from fastapi import APIRouter, HTTPException

from .exceptions import TagAlreadyExistsError
from .schema import Tag, TagCreate, TagUpdate
from .service import create_tag, get_tag_by_id, get_tag_by_name, update_tag, delete_tag

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("", status_code=201)
def create_tag_endpoint(tag_create: TagCreate):
    try:
        return create_tag(tag_create)
    except TagAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Tag already exists"
        )

@router.get("/{tag_id}", response_model=Tag)
def get_tag_by_id_endpoint(tag_id: int):
    tag = get_tag_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )
    return tag

@router.get("/by_name/{tag_name}", response_model=Tag)
def get_tag_by_name_endpoint(tag_name: str | None = None):
    tag =  get_tag_by_name(tag_name)
    if not tag:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )
    return tag

@router.put("/{tag_id}", response_model=Tag)
def update_tag_endpoint(tag_id: int, tag_update: TagUpdate):
    try:
        updated = update_tag(tag_id, tag_update)
    except TagAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Tag already exists"
        )
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )
    return updated

@router.delete("/{tag_id}", status_code=204)
def delete_tag_endpoint(tag_id: int):
    deleted = delete_tag(tag_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )
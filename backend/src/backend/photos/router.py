# 写真：HTTPリクエストを受け、サービスの結果や例外をAPI応答に変換する。

from fastapi import APIRouter, HTTPException

from .exceptions import PhotoAlreadyExistsError, InvalidPhotoInputError
from .schema import Photo, PhotoCreate, PhotoUpdate
from .service import create_photo, get_all_photos, get_photo_by_id, update_photo, delete_photo, add_tag_to_photo, \
    get_tags_by_photo_id, remove_tag_from_photo, update_tag_order_within_photo, get_tag_with_order_by_id
from ..exceptions import SortOrderIsOutOfRangeError
from ..schema import OrderUpdate
from ..tags.exceptions import PhotoTagAlreadyExistsError, TagDoesNotExistsError
from ..tags.schema import TagWithOrder
from ..tags.service import get_tag_by_id

router = APIRouter(prefix="/photos", tags=["photos"])

@router.post("", status_code=201)
def create_photo_endpoint(photo_create: PhotoCreate):
    try:
        photo = create_photo(photo_create)
    except PhotoAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Photo already exists"
        )
    except InvalidPhotoInputError:
        raise HTTPException(
            status_code=422,
            detail="Input value is invalid"
        )
    if photo is None:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )

@router.get("", response_model=list[Photo])
def get_all_photos_endpoint():
    return get_all_photos()

@router.get("/{photo_id}", response_model=Photo)
def get_photo_by_id_endpoint(photo_id: int):
    photo = get_photo_by_id(photo_id)
    if not photo:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )
    return photo

@router.put("/{photo_id}", response_model=Photo)
def update_photo_endpoint(photo_id: int, photo_update: PhotoUpdate):
    try:
        updated = update_photo(photo_id, photo_update)
    except PhotoAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Photo already exists"
        )
    except InvalidPhotoInputError:
        raise HTTPException(
            status_code=422,
            detail="Input value is invalid"
        )
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )
    return updated

@router.delete("/{photo_id}", status_code=204)
def delete_photo_endpoint(photo_id: int):
    deleted = delete_photo(photo_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )

@router.post("/{photo_id}/tags/{tag_id}", status_code=201)
def add_tag_to_photo_endpoint(photo_id: int, tag_id: str):
    print(tag_id)
    try:
        added = add_tag_to_photo(photo_id, tag_id)
    except PhotoTagAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Tag already exists"
        )
    if not added:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )
    return added

@router.get("/{photo_id}/tags/{tag_id}", response_model=TagWithOrder)
def get_tag_order_within_photo_endpoint(photo_id: int, tag_id: int):
    try:
        tag_with_order = get_tag_with_order_by_id(photo_id, tag_id)
    except TagDoesNotExistsError:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )
    return tag_with_order

@router.get("/{photo_id}/tags", response_model=list[TagWithOrder])
def get_all_photo_tags_endpoint(photo_id: int):
    photo = get_photo_by_id(photo_id)
    if not photo:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )
    return get_tags_by_photo_id(photo_id)

@router.put("/{photo_id}/tags/{tag_id}", status_code=201)
def update_tag_order_within_photo_endpoint(photo_id: int, tag_id: int, update_order: OrderUpdate):
    if get_photo_by_id(photo_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )
    if get_tag_by_id(tag_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )
    try:
        update_tag_order_within_photo(photo_id, tag_id, update_order.new_order)
    except TagDoesNotExistsError:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )
    except SortOrderIsOutOfRangeError:
        raise HTTPException(
            status_code=400,
            detail="Sort order out of range"
        )

@router.delete("/{photo_id}/tags/{tag_id}", status_code=204)
def remove_tag_from_photo_endpoint(photo_id: int, tag_id: str):
    deleted = remove_tag_from_photo(photo_id, tag_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )

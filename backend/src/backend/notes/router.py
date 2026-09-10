# ノート：HTTPリクエストを受け、サービスの結果や例外をAPI応答に変換する。

from fastapi import APIRouter, HTTPException

from .exceptions import NoteAlreadyExistsError, InvalidNoteInputError
from .service import get_all_notes, create_note, get_note_by_id, update_note, delete_note, add_photo_to_note, \
    add_tag_to_note, get_photos_by_note_id, get_tags_by_note_id, remove_tag_from_note, remove_photo_from_note, \
    update_photo_order_within_note, update_tag_order_within_note
from .schema import Note, NoteCreate, NoteUpdate
from ..exceptions import SortOrderIsOutOfRangeError
from ..photos.exceptions import NotePhotoAlreadyExistsError, PhotoDoesNotExistsError, NotePhotoDoesNotExistsError
from ..photos.schema import PhotoWithOrder
from ..schema import OrderUpdate
from ..tags.exceptions import NoteTagAlreadyExistsError, TagDoesNotExistsError
from ..tags.schema import TagWithOrder

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("", response_model=list[Note])
def get_notes_endpoint():
    return get_all_notes()

@router.get("/{note_id}", response_model=Note)
def get_note_endpoint(note_id):
    note = get_note_by_id(note_id)
    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )
    return note

@router.post("", status_code=201)
def create_note_endpoint(note_create: NoteCreate):
    try:
        note= create_note(note_create)
    except NoteAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Note already exists"
        )
    except InvalidNoteInputError:
        raise HTTPException(
            status_code=422,
            detail="Bad note input"
        )
    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

@router.put("/{note_id}", response_model=Note)
def update_note_endpoint(note_id: int, note_update: NoteUpdate):
    try:
        updated = update_note(note_id, note_update)
    except NoteAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Note already exists"
        )
    except InvalidNoteInputError:
        raise HTTPException(
            status_code=422,
            detail="Bad note input"
        )
    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )
    return updated

@router.delete("/{note_id}", status_code=204)
def delete_note_endpoint(note_id: int):
    deleted = delete_note(note_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

@router.post("/{note_id}/photos/{photo_id}", status_code=204)
def add_note_photo_endpoint(note_id: int, photo_id: int):
    try:
        success = add_photo_to_note(note_id, photo_id)
    except NotePhotoAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Photo already exists"
        )
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Note-Photo relation is not found"
        )

@router.get("/{note_id}/photos", response_model=list[PhotoWithOrder])
def get_photos_by_note_endpoint(note_id: int):
    note = get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )
    return get_photos_by_note_id(note_id)

@router.put("/{note_id}/photos/{photo_id}", status_code=204)
def update_photo_order_within_note_endpoint(note_id: int, photo_id: int, order_update: OrderUpdate):
    try:
        update_photo_order_within_note(note_id, photo_id, order_update.new_order)
    except PhotoDoesNotExistsError:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )
    except SortOrderIsOutOfRangeError:
        raise HTTPException(
            status_code=400,
            detail="Sort order out of range"
        )

@router.delete("/{note_id}/photos/{photo_id}", status_code=204)
def remove_photo_from_note_endpoint(note_id: int, photo_id: int):
    try:
        remove_photo_from_note(note_id, photo_id)
    except NotePhotoDoesNotExistsError:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )

@router.post("/{note_id}/tags/{tag_id}", status_code=204)
def add_note_tags_endpoint(note_id: int, tag_id: int):
    try:
        add_tag_to_note(note_id, tag_id)
    except NoteTagAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Tag already exists"
        )

@router.get("/{note_id}/tags", response_model=list[TagWithOrder])
def get_tags_by_note_endpoint(note_id: int):
    note = get_note_by_id(note_id)
    if not note:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )
    return get_tags_by_note_id(note_id)

@router.put("/{note_id}/tags/{tag_id}", status_code=204)
def update_tag_order_within_note_endpoint(note_id: int, tag_id: int, order_update: OrderUpdate):
    try:
        update_tag_order_within_note(note_id, tag_id, order_update.new_order)
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

@router.delete("/{note_id}/tags/{tag_id}", status_code=204)
def remove_tag_from_note_endpoint(note_id: int, tag_id: int):
    success = remove_tag_from_note(note_id, tag_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )
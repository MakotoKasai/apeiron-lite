# プロジェクト：HTTPリクエストを受け、サービスの結果や例外をAPI応答に変換する。

from fastapi import APIRouter, HTTPException

from .exceptions import ProjectAlreadyExistsError, InvalidProjectInputError
from .schema import Project, ProjectCreate, ProjectUpdate
from .service import get_all_projects, create_project, get_project_by_id, update_project, delete_project, \
    get_photos_by_project_id, get_tags_by_project_id, add_note_to_project, add_tag_to_project, add_photo_to_project, \
    get_note_with_order_within_project, update_note_order_within_project, remove_note_from_project, \
    remove_photo_from_project, remove_tag_from_project, get_notes_by_project_id, update_tag_order_within_project, \
    update_photo_order_within_project
from ..exceptions import SortOrderIsOutOfRangeError
from ..notes.exceptions import ProjectNoteAlreadyExistsError, NoteNotFoundError
from ..notes.schema import NoteWithOrder
from ..notes.service import get_note_by_id
from ..photos.exceptions import ProjectPhotoAlreadyExistsError, PhotoDoesNotExistsError
from ..photos.schema import PhotoWithOrder
from ..photos.service import get_photo_by_id
from ..schema import OrderUpdate
from ..tags.exceptions import ProjectTagAlreadyExistsError, TagDoesNotExistsError
from ..tags.schema import TagWithOrder
from ..tags.service import get_tag_by_id

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model = list[Project])
def get_projects_endpoint():
    return get_all_projects()

@router.post("", status_code=201)
def create_project_endpoint(project_create: ProjectCreate):
    try:
        project = create_project(project_create)
    except ProjectAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Project already exists"
        )
    except InvalidProjectInputError:
        raise HTTPException(
            status_code=422,
            detail="Project input is invalid"
        )
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

@router.get("/{project_id}", response_model=Project)
def get_project_endpoint(project_id: int):
    project = get_project_by_id(project_id)
    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    else:
        return project

@router.put("/{project_id}", response_model=Project)
def update_project_endpoint(project_id: int, project_update: ProjectUpdate):
    try:
        updated = update_project(project_id, project_update)
    except ProjectAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Project already exists"
        )
    except InvalidProjectInputError:
        raise HTTPException(
            status_code=422,
            detail="Project input is invalid"
        )
    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    else :
        return updated

@router.delete("/{project_id}", status_code=204)
def delete_project_endpoint(project_id: int):
    deleted = delete_project(project_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )

@router.post("/{project_id}/notes/{note_id}", status_code=201)
def add_note_to_project_endpoint(project_id: int, note_id: int):
    if get_project_by_id(project_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    if get_note_by_id(note_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )
    try:
        add_note_to_project(project_id, note_id)
    except ProjectNoteAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Project_Note already exists"
        )

@router.get("/{project_id}/notes/{note_id}", response_model=NoteWithOrder|None)
def get_note_with_order_within_project_endpoint(project_id: int, note_id: int):
    note = get_note_with_order_within_project(project_id, note_id)
    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Project_Note not found"
        )
    return note

@router.put("/{project_id}/notes/{note_id}", status_code=204)
def update_note_order_within_project_endpoint(project_id: int, note_id: int, note_order_update: OrderUpdate):
    try:
        update_note_order_within_project(project_id, note_id, note_order_update.new_order)
    except NoteNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )
    except SortOrderIsOutOfRangeError:
        raise HTTPException(
            status_code=400,
            detail="Sort order out of range"
        )

@router.get("/{project_id}/notes", response_model=list[NoteWithOrder])
def get_notes_by_project_endpoint(project_id: int):
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    return get_notes_by_project_id(project_id)

@router.delete("/{project_id}/notes/{note_id}", status_code=204)
def remove_note_from_project_endpoint(project_id: int, note_id: int):
    success = remove_note_from_project(project_id, note_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Project_Note not found"
        )

@router.post("/{project_id}/photos/{photo_id}", status_code=201)
def add_photo_to_project_endpoint(project_id: int, photo_id: int):
    if get_project_by_id(project_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    if get_photo_by_id(photo_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Photo not found"
        )
    try:
        add_photo_to_project(project_id, photo_id)
    except ProjectPhotoAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Project_Photo already exists"
        )

@router.get("/{project_id}/photos", response_model=list[PhotoWithOrder])
def get_photos_by_project_endpoint(project_id: int):
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project_Photo not found"
        )
    return get_photos_by_project_id(project_id)

@router.put("/{project_id}/photos/{photo_id}", status_code=204)
def update_photo_order_within_project_endpoint(project_id: int, photo_id: int, order_update: OrderUpdate):
    try:
        update_photo_order_within_project(project_id, photo_id, order_update.new_order)
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

@router.delete("/{project_id}/photos/{photo_id}", status_code=204)
def remove_photo_from_project_endpoint(project_id: int, photo_id: int):
    success = remove_photo_from_project(project_id, photo_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Project_Photo not found"
        )

@router.post("/{project_id}/tags/{tag_id}", status_code=201)
def add_tag_to_project_endpoint(project_id: int, tag_id: int):
    if get_project_by_id(project_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found"
        )
    if get_tag_by_id(tag_id) is None:
        raise HTTPException(
            status_code=404,
            detail="Tag not found"
        )
    try:
        add_tag_to_project(project_id, tag_id)
    except ProjectTagAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Project_Tag already exists"
        )

@router.get("/{project_id}/tags", response_model=list[TagWithOrder])
def get_tags_by_project_endpoint(project_id: int):
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project_Tag not found"
        )
    return get_tags_by_project_id(project_id)

@router.put("/{project_id}/tags/{tag_id}", status_code=204)
def update_tag_order_within_project_endpoint(project_id: int, tag_id: int, order_update: OrderUpdate):
    try:
        update_tag_order_within_project(project_id, tag_id, order_update.new_order)
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


@router.delete("/{project_id}/tags/{tag_id}", status_code=204)
def remove_tag_from_project_endpoint(project_id: int, tag_id: int):
    success = remove_tag_from_project(project_id, tag_id)
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Project_Tag not found"
        )
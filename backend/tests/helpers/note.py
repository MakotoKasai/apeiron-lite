# APIを経由せずSQLでテストの前提データを作成する。APIの動作検証は各テストで行う。

import psycopg

from backend.db import get_connection
from backend.photos.exceptions import NotePhotoAlreadyExistsError
from backend.tags.exceptions import NoteTagAlreadyExistsError


def create_test_note(title: str, body: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO notes (title, body)
                    VALUES (%s, %s)
                    RETURNING id;
                """, (title, body)
            )
            row = cursor.fetchone()
    return row[0]

def add_photo_to_test_note(note_id: int, photo_id: int):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO note_photos_relation (note_id, photo_id, sort_order)
                    SELECT %s, %s, COALESCE(MAX(sort_order), 0) + 1
                    FROM note_photos_relation
                    WHERE note_id = %s
                    """, (note_id, photo_id, note_id)
                )
                rowcount = cursor.rowcount
    except psycopg.errors.UniqueViolation as err:
        raise NotePhotoAlreadyExistsError() from err
    if rowcount == 1:
        return True
    else:
        return False

def add_tag_to_test_note(note_id: int, tag_id: int):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO note_tags_relation (note_id, tag_id, sort_order)
                    SELECT %s, %s, COALESCE(MAX(sort_order), 0) + 1
                    FROM note_tags_relation
                    WHERE note_id = %s
                    """, (note_id, tag_id, note_id)
                )
                rowcount = cursor.rowcount
    except psycopg.errors.UniqueViolation as err:
        raise NoteTagAlreadyExistsError() from err
    if rowcount == 1:
        return True
    else:
        return False

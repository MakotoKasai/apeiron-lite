# ノート：SQLによる永続化と取得を担う。DBの制約違反は必要に応じて業務例外へ変換する。

import psycopg

from .exceptions import NoteAlreadyExistsError, InvalidNoteInputError
from .schema import NoteCreate, Note, NoteUpdate
from ..db import get_connection
from ..exceptions import SortOrderIsOutOfRangeError
from ..photos.exceptions import NotePhotoAlreadyExistsError, PhotoDoesNotExistsError, NotePhotoDoesNotExistsError
from ..photos.schema import PhotoWithOrder, Photo
from ..tags.exceptions import NoteTagAlreadyExistsError, TagDoesNotExistsError
from ..tags.schema import TagWithOrder, Tag


def create_note(note_create: NoteCreate) -> Note | None:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO notes (title, body)
                       VALUES (%s, %s)
                       RETURNING id, title, body, created_at, updated_at
                    """,
                    (note_create.title, note_create.body)
                )
                row = cursor.fetchone()
    except psycopg.errors.UniqueViolation as err:
        raise NoteAlreadyExistsError() from err
    except psycopg.errors.CheckViolation as err:
        raise InvalidNoteInputError() from err
    except psycopg.errors.StringDataRightTruncation as err:
        raise InvalidNoteInputError() from err
    if row is None:
        return None
    return Note(
        id=row[0],
        title=row[1],
        body=row[2],
        created_at=row[3],
        updated_at=row[4],
    )

def get_note_by_id(note_id: int) -> Note | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id, title, body, created_at, updated_at
                    FROM notes
                    WHERE id = %s
                """,(note_id, )
            )
            row = cursor.fetchone()
    if row is None:
        return None
    return Note(
        id=row[0],
        title=row[1],
        body=row[2],
        created_at=row[3],
        updated_at=row[4],
    )

def get_all_notes() -> list[Note]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id, title, body, created_at, updated_at
                    FROM notes
                    ORDER BY updated_at DESC
                """
            )
            rows = cursor.fetchall()
    return [
        Note(
            id=row[0],
            title=row[1],
            body=row[2],
            created_at=row[3],
            updated_at=row[4],
        ) for row in rows
    ]

def update_note(note_id: int, update: NoteUpdate) -> Note | None:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        UPDATE notes
                        SET title = %s, body = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING id, title, body, created_at, updated_at
                    """, (update.title, update.body, note_id)
                )
                row = cursor.fetchone()
    except psycopg.errors.UniqueViolation as err:
        raise NoteAlreadyExistsError() from err
    except psycopg.errors.CheckViolation as err:
        raise InvalidNoteInputError() from err
    if row is None:
        return None
    return Note(
        id=row[0],
        title=row[1],
        body=row[2],
        created_at=row[3],
        updated_at=row[4],
    )

def delete_note(note_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    DELETE FROM notes
                    WHERE id = %s
                """, (note_id, )
            )
            if cursor.rowcount == 1:
                return True
    return False


# 親ごとの最大順序 + 1 に追加する。関連がない場合は COALESCE により1から始まる。
def add_photo_to_note(note_id: int, photo_id: int) -> bool:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO note_photos_relation (note_id, photo_id, sort_order)
                        SELECT %s, %s, COALESCE(MAX(sort_order),0)+1
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

# 親ごとの最大順序 + 1 に追加する。関連がない場合は COALESCE により1から始まる。
def add_tag_to_note(note_id: int, tag_id: int) -> bool:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO note_tags_relation (note_id, tag_id,sort_order)
                        SELECT %s, %s, COALESCE(MAX(sort_order),0)+1
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

def get_photos_by_note_id(note_id: int) -> list[PhotoWithOrder]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT pt.id, pt.file_path, pt.created_at, pt.updated_at, np.sort_order
                    FROM photos as pt
                    INNER JOIN note_photos_relation as np
                    ON pt.id = np.photo_id
                    WHERE np.note_id = %s
                    ORDER BY np.sort_order
                """, (note_id, )
            )
            rows = cursor.fetchall()
    return [
        PhotoWithOrder(
            photo = Photo(
                id = row[0],
                file_path = row[1],
                created_at = row[2],
                updated_at = row[3],
            ),
            sort_order = row[4],
        )
        for row in rows
    ]

def update_photo_order_within_note(note_id: int, photo_id: int, new_order: int) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            current_order = get_current_order_of_photo_within_note(cursor, note_id, photo_id)
            if current_order == new_order :
                return
            max_order = get_max_order_of_photos_within_note(note_id)
            if (0 >= new_order) | (new_order > max_order):
                raise SortOrderIsOutOfRangeError
            # 移動対象を一時的に -1 へ退避し、空いた順序へ他の要素を移す。
            set_order_of_photo_within_note(cursor, note_id, photo_id, -1)
            if new_order > current_order:
                shift_order_of_photos_down_within_note(cursor, note_id, new_order, current_order)
            elif current_order > new_order:
                shift_order_of_photos_up_within_note(cursor, note_id, new_order, current_order)
            set_order_of_photo_within_note(cursor, note_id, photo_id, new_order)

def get_max_order_of_photos_within_note(note_id: int) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT COALESCE(MAX(sort_order),0)
                    FROM note_photos_relation
                    WHERE note_id = %s
                """, (note_id, )
            )
            row = cursor.fetchone()
    if row is None:
        return 0
    return row[0]

def get_current_order_of_photo_within_note(cursor, note_id: int, photo_id: int) -> int:
    cursor.execute(
        """
            Select sort_order
            FROM note_photos_relation
            WHERE note_id = %s
            AND photo_id = %s
        """,
        (note_id, photo_id,)
    )
    row = cursor.fetchone()
    if row is None:
        raise PhotoDoesNotExistsError
    return row[0]

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_photos_up_within_note(cursor, note_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT photo_id, sort_order
            FROM note_photos_relation
            WHERE note_id = %s
            AND sort_order >= %s
            AND sort_order < %s
            ORDER BY sort_order DESC
        """,
        (note_id, new_order, old_order,)
    )
    rows = cursor.fetchall()
    for photo_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE note_photos_relation
                SET sort_order = %s
                WHERE note_id = %s
                AND photo_id = %s
            """,
            (sort_order + 1, note_id, photo_id,)
        )

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_photos_down_within_note(cursor, note_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT photo_id, sort_order
            FROM note_photos_relation
            WHERE note_id = %s
                AND sort_order > %s
                AND sort_order <= %s
            ORDER BY sort_order ASC
        """,
        (note_id, old_order, new_order,)
    )
    rows = cursor.fetchall()
    for photo_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE note_photos_relation
                SET sort_order = %s
                WHERE note_id = %s
                AND photo_id = %s
            """,
            (sort_order -1 , note_id, photo_id,)
        )

def set_order_of_photo_within_note(cursor, note_id: int, photo_id: int, new_order: int) -> None:
    cursor.execute(
        """
            UPDATE note_photos_relation
            SET sort_order = %s
            WHERE note_id = %s
            AND photo_id = %s
        """,
        (new_order, note_id, photo_id,)
    )
    rowcount = cursor.rowcount
    if rowcount == 0:
        raise PhotoDoesNotExistsError

# 関連行のみを削除する。本体データと残りの sort_order は変更しない。
def remove_photo_from_note(note_id: int, photo_id: int) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    DELETE FROM note_photos_relation
                    WHERE note_id = %s
                    AND photo_id = %s
                """, (note_id, photo_id, )
            )
            if cursor.rowcount == 0:
                raise NotePhotoDoesNotExistsError

def get_tags_by_note_id(note_id: int) -> list[TagWithOrder]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SElECT t.id, t.name, t.created_at, t.updated_at, nt.sort_order
                    FROM tags as t 
                    INNER JOIN note_tags_relation as nt
                    ON t.id = nt.tag_id
                    WHERE nt.note_id = %s
                    ORDER BY nt.sort_order
                """, (note_id,)
            )
            rows = cursor.fetchall()
    return [
        TagWithOrder(
            tag = Tag(
                id = row[0],
                name = row[1],
                created_at = row[2],
                updated_at = row[3],
            ),
            sort_order = row[4],
        )
        for row in rows
    ]

def update_tag_order_within_note(note_id: int, tag_id: int, new_order: int) -> None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            current_order = get_current_order_of_tag_within_note(cursor, note_id, tag_id)
            if current_order == new_order:
                return
            max_order = get_max_order_of_tags_within_note(note_id)
            if (0 >= new_order) | (new_order > max_order):
                raise SortOrderIsOutOfRangeError
            # 移動対象を一時的に -1 へ退避し、空いた順序へ他の要素を移す。
            set_order_of_tag_within_note(cursor, note_id, tag_id, -1)
            if new_order > current_order:
                shift_order_of_tags_down_within_note(cursor, note_id, new_order, current_order)
            elif current_order > new_order:
                shift_order_of_tags_up_within_note(cursor, note_id, new_order, current_order)
            set_order_of_tag_within_note(cursor, note_id, tag_id, new_order)

def get_max_order_of_tags_within_note(note_id: int) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT COALESCE(MAX(sort_order),0)
                    FROM note_tags_relation
                    WHERE note_id = %s
                """, (note_id, )
            )
            row = cursor.fetchone()
    if row is None:
        return 0
    return row[0]

def get_current_order_of_tag_within_note(cursor, note_id: int, tag_id: int) -> int:
    cursor.execute(
        """
            Select sort_order
            FROM note_tags_relation
            WHERE note_id = %s
            AND tag_id = %s
        """,
        (note_id, tag_id,)
    )
    row = cursor.fetchone()
    if row is None:
        raise TagDoesNotExistsError
    return row[0]

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_tags_up_within_note(cursor, note_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT tag_id, sort_order
            FROM note_tags_relation
            WHERE note_id = %s
            AND sort_order >= %s
            AND sort_order < %s
            ORDER BY sort_order DESC
        """,
        (note_id, new_order, old_order,)
    )
    rows = cursor.fetchall()
    for tag_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE note_tags_relation
                SET sort_order = %s
                WHERE note_id = %s
                AND tag_id = %s
            """,
            (sort_order + 1, note_id, tag_id,)
        )

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_tags_down_within_note(cursor, note_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT tag_id, sort_order
            FROM note_tags_relation
            WHERE note_id = %s
                AND sort_order > %s
                AND sort_order <= %s
            ORDER BY sort_order ASC
        """,
        (note_id, old_order, new_order,)
    )
    rows = cursor.fetchall()
    for tag_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE note_tags_relation
                SET sort_order = %s
                WHERE note_id = %s
                AND tag_id = %s
            """,
            (sort_order -1 , note_id, tag_id,)
        )

def set_order_of_tag_within_note(cursor, note_id: int, tag_id: int, new_order: int) -> bool:
    cursor.execute(
        """
            UPDATE note_tags_relation
            SET sort_order = %s
            WHERE note_id = %s
            AND tag_id = %s
        """,
        (new_order, note_id, tag_id,)
    )
    rowcount = cursor.rowcount
    if rowcount == 0:
        return False
    else:
        return True


# 関連行のみを削除する。本体データと残りの sort_order は変更しない。
def remove_tag_from_note(note_id: int, tag_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    DELETE FROM note_tags_relation
                    WHERE note_id = %s
                    AND tag_id = %s
                """, (note_id, tag_id, )
            )
            if cursor.rowcount == 1:
                return True
            else:
                return False
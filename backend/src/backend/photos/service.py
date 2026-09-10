# 写真：SQLによる永続化と取得を担う。DBの制約違反は必要に応じて業務例外へ変換する。

import psycopg

from .exceptions import PhotoAlreadyExistsError, InvalidPhotoInputError
from ..db import get_connection
from .schema import PhotoCreate, Photo, PhotoUpdate
from ..exceptions import SortOrderIsOutOfRangeError
from ..tags.exceptions import PhotoTagAlreadyExistsError, TagDoesNotExistsError
from ..tags.schema import TagWithOrder, Tag


def create_photo(photo_create: PhotoCreate) -> Photo | None:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO photos (file_path)
                        VALUES (%s)
                        RETURNING id, file_path, created_at, updated_at
                    """, (photo_create.file_path, )
                )
                row = cursor.fetchone()
    except psycopg.errors.UniqueViolation as err:
        raise PhotoAlreadyExistsError() from err
    except psycopg.errors.CheckViolation as err:
        raise InvalidPhotoInputError() from err
    if row is None:
        return None
    return Photo(
        id=row[0],
        file_path=row[1],
        created_at=row[2],
        updated_at=row[3],
    )

def get_all_photos() -> list[Photo]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id, file_path, created_at, updated_at
                    FROM photos
                    ORDER BY updated_at DESC
                """
            )
            rows = cursor.fetchall()
    return [
        Photo(
            id=row[0],
            file_path=row[1],
            created_at=row[2],
            updated_at=row[3],
        )
        for row in rows
    ]

def get_photo_by_id(photo_id: int) -> Photo | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id, file_path, created_at, updated_at
                    FROM photos
                    WHERE id = %s
                """, (photo_id, )
            )
            row = cursor.fetchone()
    if row is None:
        return None
    return Photo(
        id=row[0],
        file_path=row[1],
        created_at=row[2],
        updated_at=row[3],
    )

def update_photo(photo_id: int, photo_update: PhotoUpdate) -> Photo | None:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        UPDATE photos
                        SET file_path = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING id, file_path, created_at, updated_at
                    """, (photo_update.file_path, photo_id)
                )
                row = cursor.fetchone()
    except psycopg.errors.UniqueViolation as err:
        raise PhotoAlreadyExistsError() from err
    except psycopg.errors.CheckViolation as err:
        raise InvalidPhotoInputError() from err
    if row is None:
        return None
    return Photo(
        id=row[0],
        file_path=row[1],
        created_at=row[2],
        updated_at=row[3],
    )

def delete_photo(photo_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    DELETE FROM photos
                    WHERE id = %s
                """, (photo_id, )
            )
            if cursor.rowcount == 1:
                return True
            else:
                return False

# 親ごとの最大順序 + 1 に追加する。関連がない場合は COALESCE により1から始まる。
def add_tag_to_photo(photo_id: int, tag_id: str) -> bool:
    print("add_tag_to_photo")
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO photo_tags_relation  (photo_id, tag_id, sort_order)
                        SELECT %s, %s, COALESCE(MAX(sort_order),0)+1
                        FROM photo_tags_relation
                        WHERE photo_id = %s
                    """, (photo_id, tag_id, photo_id)
                )
                rowcount = cursor.rowcount
    except psycopg.errors.UniqueViolation as err:
        raise PhotoTagAlreadyExistsError from err
    if rowcount == 1:
        return True
    else:
        return False

def get_tag_with_order_by_id(photo_id:int, tag_id: int) -> TagWithOrder | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT tg.id, tg.name, tg.created_at, tg.updated_at, pt.sort_order
                    FROM tags as tg 
                    INNER JOIN photo_tags_relation as pt
                    ON tg.id = pt.tag_id 
                    WHERE pt.photo_id = %s
                    AND pt.tag_id = %s
                """,
                (photo_id, tag_id,)
            )
            row = cursor.fetchone()
    if row is None:
        raise TagDoesNotExistsError
    return TagWithOrder(
        tag = Tag(
            id = row[0],
            name = row[1],
            created_at=row[2],
            updated_at=row[3],
        ),
        sort_order = row[4],
    )

def get_tags_by_photo_id(photo_id: int) -> list[TagWithOrder]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT tg.id, tg.name, tg.created_at, tg.updated_at, pt.sort_order
                    FROM tags as tg 
                    INNER JOIN photo_tags_relation as pt
                    ON tg.id = pt.tag_id 
                    WHERE pt.photo_id = %s
                    ORDER BY pt.sort_order
                """, (photo_id, )
            )
            rows = cursor.fetchall()
    return [
        TagWithOrder(
            tag = Tag(
                id=row[0],
                name = row[1],
                created_at=row[2],
                updated_at=row[3],
            ),
            sort_order = row[4],
        )
        for row in rows
    ]

def update_tag_order_within_photo(photo_id: int, tag_id: int, new_order: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            max_order = get_max_order_of_tags_within_photo(photo_id)
            if(0 >= new_order) | (new_order > max_order):
                raise SortOrderIsOutOfRangeError
            current_order = get_current_order_of_tag_within_photo(cursor, photo_id, tag_id)
            if current_order == new_order:
                return True
            # 移動対象を一時的に -1 へ退避し、空いた順序へ他の要素を移す。
            set_order_of_tag_within_photo(cursor, photo_id, tag_id, -1)
            if new_order > current_order:
                shift_order_of_tags_down_within_photo(cursor, photo_id, new_order, current_order)
            elif current_order > new_order:
                shift_order_of_tags_up_within_photo(cursor, photo_id, new_order, current_order)
            return set_order_of_tag_within_photo(cursor, photo_id, tag_id, new_order)

def get_max_order_of_tags_within_photo(photo_id: int) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT COALESCE(MAX(sort_order),0)
                    FROM photo_tags_relation
                    WHERE photo_id = %s
                """, (photo_id, )
            )
            row = cursor.fetchone()
    if row is None:
        return 0
    return row[0]

def get_current_order_of_tag_within_photo(cursor, photo_id: int, tag_id: int) -> int:
    cursor.execute(
        """
            Select sort_order
            FROM photo_tags_relation
            WHERE photo_id = %s
            AND tag_id = %s
        """,
        (photo_id, tag_id,)
    )
    row = cursor.fetchone()
    if row is None:
        raise TagDoesNotExistsError
    return row[0]

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_tags_up_within_photo(cursor, photo_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT tag_id, sort_order
            FROM photo_tags_relation
            WHERE photo_id = %s
            AND sort_order >= %s
            AND sort_order < %s
            ORDER BY sort_order DESC
        """,
        (photo_id, new_order, old_order,)
    )
    rows = cursor.fetchall()
    for tag_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE photo_tags_relation
                SET sort_order = %s
                WHERE photo_id = %s
                AND tag_id = %s
            """,
            (sort_order + 1, photo_id, tag_id,)
        )

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_tags_down_within_photo(cursor, photo_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT tag_id, sort_order
            FROM photo_tags_relation
            WHERE photo_id = %s
                AND sort_order > %s
                AND sort_order <= %s
            ORDER BY sort_order ASC
        """,
        (photo_id, old_order, new_order,)
    )
    rows = cursor.fetchall()
    for tag_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE photo_tags_relation
                SET sort_order = %s
                WHERE photo_id = %s
                AND tag_id = %s
            """,
            (sort_order -1 , photo_id, tag_id,)
        )

def set_order_of_tag_within_photo(cursor, photo_id: int, tag_id: int, new_order: int) -> bool:
    cursor.execute(
        """
            UPDATE photo_tags_relation
            SET sort_order = %s
            WHERE photo_id = %s
            AND tag_id = %s
        """,
        (new_order, photo_id, tag_id,)
    )
    rowcount = cursor.rowcount
    if rowcount == 0:
        return False
    else:
        return True

# 関連行のみを削除する。本体データと残りの sort_order は変更しない。
def remove_tag_from_photo(photo_id: int, tag_id: str) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    DELETE FROM photo_tags_relation 
                    WHERE photo_id = %s
                    AND tag_id = %s
                """, (photo_id, tag_id,)
            )
            rowcount = cursor.rowcount
    if rowcount == 0:
        return True
    else:
        return False
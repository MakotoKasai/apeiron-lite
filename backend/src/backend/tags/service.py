# タグ：SQLによる永続化と取得を担う。DBの制約違反は必要に応じて業務例外へ変換する。

import psycopg

from .exceptions import TagAlreadyExistsError, InvalidTagInputError
from .schema import Tag, TagCreate, TagUpdate
from ..db import get_connection

def create_tag(tag_create: TagCreate) -> Tag | None:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO tags (name)
                        VALUES (%s)
                        RETURNING id, name, created_at, updated_at;
                    """, (tag_create.name,)
                )
                row=cursor.fetchone()
    except psycopg.errors.UniqueViolation as err:
        raise TagAlreadyExistsError() from err
    except psycopg.errors.CheckViolation as err:
        raise InvalidTagInputError() from err
    if row is None:
        return None
    return Tag(
        id=row[0],
        name=row[1],
        created_at=row[2],
        updated_at=row[3],
    )

def get_tag_by_id(tag_id: int) -> Tag | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id, name, created_at, updated_at
                    FROM tags
                    WHERE id = %s
                """, (tag_id, )
            )
            row = cursor.fetchone()
    if row is None:
        return None
    return Tag(
        id=row[0],
        name=row[1],
        created_at=row[2],
        updated_at=row[3],
    )

def get_tag_by_name(name: str | None) -> Tag | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT id, name, created_at, updated_at
                    FROM tags
                    WHERE name = %s
                """, (name, )
            )
            row = cursor.fetchone()
    if row is None:
        return None
    return Tag(
        id=row[0],
        name=row[1],
        created_at=row[2],
        updated_at=row[3],
    )

def update_tag(tag_id:int, tag_update: TagUpdate) -> Tag | None:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        UPDATE tags
                        SET name = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING id, name, created_at, updated_at;
                    """, (tag_update.name, tag_id)
                )
                row=cursor.fetchone()
    except psycopg.errors.UniqueViolation as err:
        raise TagAlreadyExistsError() from err
    except psycopg.errors.CheckViolation as err:
        raise InvalidTagInputError() from err
    if row is None:
        return None
    return Tag(
        id=row[0],
        name=row[1],
        created_at=row[2],
        updated_at=row[3],
    )

def delete_tag(tag_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    DELETE FROM tags
                    WHERE id = %s
                """, (tag_id, )
            )
            return cursor.rowcount == 1


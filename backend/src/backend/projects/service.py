# プロジェクト：SQLによる永続化と取得を担う。DBの制約違反は必要に応じて業務例外へ変換する。

import psycopg

from .exceptions import ProjectAlreadyExistsError, InvalidProjectInputError
from .schema import Project, ProjectCreate, ProjectUpdate
from ..db import get_connection
from ..exceptions import SortOrderIsOutOfRangeError
from ..notes.exceptions import ProjectNoteAlreadyExistsError, NoteNotFoundError
from ..notes.schema import Note, NoteWithOrder
from ..photos.exceptions import ProjectPhotoAlreadyExistsError, PhotoDoesNotExistsError
from ..photos.schema import PhotoWithOrder, Photo
from ..tags.exceptions import TagDoesNotExistsError, ProjectTagAlreadyExistsError
from ..tags.schema import TagWithOrder, Tag


def get_project_by_id(project_id: int) -> Project | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                   SELECT id, title, description, created_at, updated_at
                   FROM projects
                   WHERE id = %s
                """, (project_id, )
            )
            row = cursor.fetchone()
    if row is None:
        return None
    return Project(
        id=row[0],
        title=row[1],
        description=row[2],
        created_at=row[3],
        updated_at=row[4],
    )

def get_all_projects() -> list[Project]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT id, title, description, created_at, updated_at
                   FROM projects
                   ORDER BY updated_at DESC
                """,
            )
            rows = cursor.fetchall()
    return [
        Project(
            id=row[0],
            title=row[1],
            description=row[2],
            created_at=row[3],
            updated_at=row[4],
        )
        for row in rows
    ]

def create_project(project_create: ProjectCreate) -> Project | None:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO projects (title, description)
                        VALUES (%s, %s)
                        RETURNING id, title, description, created_at, updated_at
                    """,
                    (project_create.title, project_create.description)
                )
                row = cursor.fetchone()
    except psycopg.errors.UniqueViolation as err:
        raise ProjectAlreadyExistsError() from err
    except psycopg.errors.CheckViolation as err:
        raise InvalidProjectInputError() from err
    except psycopg.errors.StringDataRightTruncation as err:
        raise InvalidProjectInputError() from err
    if row is None:
        return None
    return Project(
        id=row[0],
        title=row[1],
        description=row[2],
        created_at=row[3],
        updated_at=row[4],
    )

def update_project(project_id: int, project_update: ProjectUpdate) -> Project | None:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        UPDATE projects
                        SET title = %s, description = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                        RETURNING id, title, description, created_at, updated_at
                    """, (project_update.title, project_update.description, project_id)
                )
                row = cursor.fetchone()
    except psycopg.errors.UniqueViolation as err:
        raise ProjectAlreadyExistsError() from err
    except psycopg.errors.CheckViolation as err:
        raise InvalidProjectInputError() from err
    if row is None:
        return None
    return Project(
        id=row[0],
        title=row[1],
        description=row[2],
        created_at=row[3],
        updated_at=row[4],
    )

def delete_project(project_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    DELETE FROM projects WHERE id = %s
                """, (project_id, )
            )
            if cursor.rowcount == 0:
                return False
            else:
                return True

# 親ごとの最大順序 + 1 に追加する。関連がない場合は COALESCE により1から始まる。
def add_note_to_project(project_id: int, note_id: int) -> bool:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO project_notes_relation (project_id, note_id, sort_order)
                        SELECT %s, %s, COALESCE(MAX(sort_order),0)+1
                        FROM project_notes_relation
                        WHERE project_id = %s
                    """, (project_id, note_id, project_id)
                )
                rowcount = cursor.rowcount
    except psycopg.errors.UniqueViolation as err:
        raise ProjectNoteAlreadyExistsError() from err
    if rowcount == 0:
        return False
    else:
        return True

def get_note_with_order_within_project(project_id: int, note_id: int) -> NoteWithOrder | None:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT nt.id, nt.title, nt.body, nt.created_at, nt.updated_at, pn.sort_order
                    FROM notes as nt
                    INNER JOIN project_notes_relation as pn
                    ON nt.id = pn.note_id
                    WHERE pn.project_id = %s
                    AND pn.note_id = %s
                """, (project_id, note_id,)
            )
            row = cursor.fetchone()
    if row is None:
        return None
    return NoteWithOrder(
        note = Note(
            id = row[0],
            title = row[1],
            body = row[2],
            created_at=row[3],
            updated_at=row[4],
        ),
        sort_order = row[5],
    )

def get_notes_by_project_id(project_id: int) -> list[NoteWithOrder]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT nt.id, nt.title, nt.body, nt.created_at, nt.updated_at, pn.sort_order
                FROM notes nt
                         INNER JOIN project_notes_relation pn
                                    ON nt.id = pn.note_id
                WHERE pn.project_id = %s
                ORDER BY pn.sort_order
                """, (project_id,)
            )
            rows = cursor.fetchall()
    return [
        NoteWithOrder(
            note = Note(
                id=row[0],
                title=row[1],
                body=row[2],
                created_at=row[3],
                updated_at=row[4],
            ),
            sort_order = row[5],
        )
        for row in rows
    ]

def update_note_order_within_project(project_id: int, note_id: int, new_order: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            current_order = get_current_order_of_note_within_project(cursor, project_id, note_id)
            if current_order == new_order:
                return True
            max_order = get_max_order_of_notes_within_project(project_id)
            if (new_order <= 0) | (new_order > max_order):
                raise SortOrderIsOutOfRangeError
            # 移動対象を一時的に -1 へ退避し、空いた順序へ他の要素を移す。
            set_order_of_note_within_project(cursor, project_id, note_id, -1)
            if new_order > current_order:
                print("shift_order_of_notes_down_within_project")
                shift_order_of_notes_down_within_project(cursor, project_id, new_order, current_order)
            elif current_order > new_order:
                print("shift_order_of_notes_up_within_project")
                shift_order_of_notes_up_within_project(cursor, project_id, new_order, current_order)
            return set_order_of_note_within_project(cursor, project_id, note_id, new_order)

def get_max_order_of_notes_within_project(project_id: int) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT COALESCE(MAX(sort_order),0)
                    FROM project_notes_relation
                    WHERE project_id = %s
                """, (project_id, )
            )
            row = cursor.fetchone()
    if row is None:
        return 0
    return row[0]

def get_current_order_of_note_within_project(cursor, project_id: int, note_id: int) -> int:
    cursor.execute(
        """
            Select sort_order
            FROM project_notes_relation
            WHERE project_id = %s
            AND note_id = %s
        """,
        (project_id, note_id,)
    )
    row = cursor.fetchone()
    if row is None:
        raise NoteNotFoundError
    return row[0]

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_notes_up_within_project(cursor, project_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT note_id, sort_order
            FROM project_notes_relation
            WHERE project_id = %s
            AND sort_order >= %s
            AND sort_order < %s
            ORDER BY sort_order DESC
        """,
        (project_id, new_order, old_order,)
    )
    rows = cursor.fetchall()
    for note_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE project_notes_relation
                SET sort_order = %s
                WHERE project_id = %s
                AND note_id = %s
            """,
            (sort_order + 1, project_id, note_id,)
        )

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_notes_down_within_project(cursor, project_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT note_id, sort_order
            FROM project_notes_relation
            WHERE project_id = %s
                AND sort_order > %s
                AND sort_order <= %s
            ORDER BY sort_order ASC
        """,
        (project_id, old_order, new_order,)
    )
    rows = cursor.fetchall()
    for note_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE project_notes_relation
                SET sort_order = %s
                WHERE project_id = %s
                AND note_id = %s
            """,
            (sort_order -1 , project_id, note_id,)
        )

def set_order_of_note_within_project(cursor, project_id: int, note_id: int, new_order: int) -> bool:
    print("set_order_of_note_within_project")
    print(new_order)
    cursor.execute(
        """
            UPDATE project_notes_relation
            SET sort_order = %s
            WHERE project_id = %s
            AND note_id = %s
        """,
        (new_order, project_id, note_id,)
    )
    rowcount = cursor.rowcount
    if rowcount == 0:
        return False
    else:
        return True

# 関連行のみを削除する。本体データと残りの sort_order は変更しない。
def remove_note_from_project(project_id: int, note_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    DELETE FROM project_notes_relation
                    WHERE project_id = %s
                    AND note_id = %s
                """,
                (project_id, note_id, )
            )
            rowcount = cursor.rowcount
    if rowcount == 0:
        return False
    else:
        return True

# 親ごとの最大順序 + 1 に追加する。関連がない場合は COALESCE により1から始まる。
def add_photo_to_project(project_id: int, photo_id: int) -> bool:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO project_photos_relation (project_id, photo_id, sort_order)
                        SELECT %s, %s, COALESCE(MAX(sort_order),0)+1
                        FROM project_photos_relation
                        WHERE project_id = %s
                    """, (project_id, photo_id, project_id)
                )
                rowcount = cursor.rowcount
    except psycopg.errors.UniqueViolation as err:
        raise ProjectPhotoAlreadyExistsError() from err
    if rowcount == 0:
        return False
    else:
        return True

def get_photos_by_project_id(project_id: int) -> list[PhotoWithOrder]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT pt.id, pt.file_path, pt.created_at, pt.updated_at, pp.sort_order
                    FROM photos as pt
                    INNER JOIN project_photos_relation as pp
                    ON pt.id = pp.photo_id
                    WHERE pp.project_id = %s
                    ORDER BY pp.sort_order
                """, (project_id,)
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

def update_photo_order_within_project(project_id: int, photo_id: int, new_order: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            current_order = get_current_order_of_photo_within_project(cursor, project_id, photo_id)
            if current_order == new_order:
                return True
            max_order = get_max_order_of_photos_within_project(project_id)
            if (new_order <= 0) | (new_order > max_order):
                raise SortOrderIsOutOfRangeError
            # 移動対象を一時的に -1 へ退避し、空いた順序へ他の要素を移す。
            set_order_of_photo_within_project(cursor, project_id, photo_id, -1)
            if new_order > current_order:
                print("shift_order_of_photos_down_within_project")
                shift_order_of_photos_down_within_project(cursor, project_id, new_order, current_order)
            elif current_order > new_order:
                print("shift_order_of_photos_up_within_project")
                shift_order_of_photos_up_within_project(cursor, project_id, new_order, current_order)
            return set_order_of_photo_within_project(cursor, project_id, photo_id, new_order)

def get_max_order_of_photos_within_project(project_id: int) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT COALESCE(MAX(sort_order),0)
                    FROM project_photos_relation
                    WHERE project_id = %s
                """, (project_id, )
            )
            row = cursor.fetchone()
    if row is None:
        return 0
    return row[0]


def get_current_order_of_photo_within_project(cursor, project_id: int, photo_id: int) -> int:
    cursor.execute(
        """
            Select sort_order
            FROM project_photos_relation
            WHERE project_id = %s
            AND photo_id = %s
        """,
        (project_id, photo_id,)
    )
    row = cursor.fetchone()
    if row is None:
        raise PhotoDoesNotExistsError
    return row[0]

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_photos_up_within_project(cursor, project_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT photo_id, sort_order
            FROM project_photos_relation
            WHERE project_id = %s
            AND sort_order >= %s
            AND sort_order < %s
            ORDER BY sort_order DESC
        """,
        (project_id, new_order, old_order,)
    )
    rows = cursor.fetchall()
    for photo_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE project_photos_relation
                SET sort_order = %s
                WHERE project_id = %s
                AND photo_id = %s
            """,
            (sort_order + 1, project_id, photo_id,)
        )

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_photos_down_within_project(cursor, project_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT photo_id, sort_order
            FROM project_photos_relation
            WHERE project_id = %s
                AND sort_order > %s
                AND sort_order <= %s
            ORDER BY sort_order ASC
        """,
        (project_id, old_order, new_order,)
    )
    rows = cursor.fetchall()
    for photo_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE project_photos_relation
                SET sort_order = %s
                WHERE project_id = %s
                AND photo_id = %s
            """,
            (sort_order -1 , project_id, photo_id,)
        )

def set_order_of_photo_within_project(cursor, project_id: int, photo_id: int, new_order: int) -> bool:
    print("set_order_of_photo_within_project")
    print(new_order)
    cursor.execute(
        """
            UPDATE project_photos_relation
            SET sort_order = %s
            WHERE project_id = %s
            AND photo_id = %s
        """,
        (new_order, project_id, photo_id,)
    )
    rowcount = cursor.rowcount
    if rowcount == 0:
        return False
    else:
        return True

# 関連行のみを削除する。本体データと残りの sort_order は変更しない。
def remove_photo_from_project(project_id: int, photo_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM project_photos_relation
                WHERE project_id = %s
                AND photo_id = %s
                """,
                (project_id, photo_id, )
            )
            rowcount = cursor.rowcount
    if rowcount == 1:
        return True
    else:
        return False

# 親ごとの最大順序 + 1 に追加する。関連がない場合は COALESCE により1から始まる。
def add_tag_to_project(project_id: int, tag_id: int) -> bool:
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                        INSERT INTO project_tags_relation (project_id, tag_id, sort_order)
                        SELECT %s, %s, COALESCE(MAX(sort_order),0)+1
                        FROM project_tags_relation
                        WHERE project_id = %s
                    """, (project_id, tag_id, project_id)
                )
                rowcount = cursor.rowcount
    except psycopg.errors.UniqueViolation as err:
        raise ProjectTagAlreadyExistsError() from err
    if rowcount == 0:
        return False
    else:
        return True

def get_tags_by_project_id(project_id: int) -> list[TagWithOrder]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT t.id, t.name, t.created_at, t.updated_at, pt.sort_order
                    FROM tags as t 
                        INNER JOIN project_tags_relation pt 
                        ON t.id = pt.tag_id
                    WHERE pt.project_id = %s
                    ORDER BY pt.sort_order
                """, (project_id, )
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

def update_tag_order_within_project(project_id: int, tag_id: int, new_order: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            current_order = get_current_order_of_tag_within_project(cursor, project_id, tag_id)
            if current_order == new_order:
                return True
            max_order = get_max_order_of_tags_within_project(project_id)
            if (new_order <= 0) | (new_order > max_order):
                raise SortOrderIsOutOfRangeError
            # 移動対象を一時的に -1 へ退避し、空いた順序へ他の要素を移す。
            set_order_of_tag_within_project(cursor, project_id, tag_id, -1)
            if new_order > current_order:
                print("shift_order_of_tags_down_within_project")
                shift_order_of_tags_down_within_project(cursor, project_id, new_order, current_order)
            elif current_order > new_order:
                print("shift_order_of_tags_up_within_project")
                shift_order_of_tags_up_within_project(cursor, project_id, new_order, current_order)
            return set_order_of_tag_within_project(cursor, project_id, tag_id, new_order)

def get_max_order_of_tags_within_project(project_id: int) -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT COALESCE(MAX(sort_order),0)
                    FROM project_tags_relation
                    WHERE project_id = %s
                """, (project_id, )
            )
            row = cursor.fetchone()
    if row is None:
        return 0
    return row[0]

def get_current_order_of_tag_within_project(cursor, project_id: int, tag_id: int) -> int:
    cursor.execute(
        """
            Select sort_order
            FROM project_tags_relation
            WHERE project_id = %s
            AND tag_id = %s
        """,
        (project_id, tag_id,)
    )
    row = cursor.fetchone()
    if row is None:
        raise TagDoesNotExistsError
    return row[0]

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_tags_up_within_project(cursor, project_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT tag_id, sort_order
            FROM project_tags_relation
            WHERE project_id = %s
            AND sort_order >= %s
            AND sort_order < %s
            ORDER BY sort_order DESC
        """,
        (project_id, new_order, old_order,)
    )
    rows = cursor.fetchall()
    for tag_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE project_tags_relation
                SET sort_order = %s
                WHERE project_id = %s
                AND tag_id = %s
            """,
            (sort_order + 1, project_id, tag_id,)
        )

# 順序を増やす場合は降順、減らす場合は昇順に更新し、途中の一意制約違反を避ける。
def shift_order_of_tags_down_within_project(cursor, project_id: int, new_order: int, old_order: int) -> None:
    cursor.execute(
        """
            SELECT tag_id, sort_order
            FROM project_tags_relation
            WHERE project_id = %s
                AND sort_order > %s
                AND sort_order <= %s
            ORDER BY sort_order ASC
        """,
        (project_id, old_order, new_order,)
    )
    rows = cursor.fetchall()
    for tag_id, sort_order in rows:
        cursor.execute(
            """
                UPDATE project_tags_relation
                SET sort_order = %s
                WHERE project_id = %s
                AND tag_id = %s
            """,
            (sort_order -1 , project_id, tag_id,)
        )

def set_order_of_tag_within_project(cursor, project_id: int, tag_id: int, new_order: int) -> bool:
    print("set_order_of_tag_within_project")
    print(new_order)
    cursor.execute(
        """
            UPDATE project_tags_relation
            SET sort_order = %s
            WHERE project_id = %s
            AND tag_id = %s
        """,
        (new_order, project_id, tag_id,)
    )
    rowcount = cursor.rowcount
    if rowcount == 0:
        return False
    else:
        return True

# 関連行のみを削除する。本体データと残りの sort_order は変更しない。
def remove_tag_from_project(project_id: int, tag_id: int) -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    DELETE FROM project_tags_relation
                    WHERE project_id = %s
                    AND tag_id = %s
                """,
                (project_id, tag_id, )
            )
            rowcount = cursor.rowcount
    if rowcount == 1:
        return True
    else:
        return False

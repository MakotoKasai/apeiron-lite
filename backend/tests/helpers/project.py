# APIを経由せずSQLでテストの前提データを作成する。APIの動作検証は各テストで行う。

from backend.db import get_connection

def create_test_project(title: str, description: str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO projects (title, description)
                        VALUES (%s, %s)
                        RETURNING id
                """, (title, description)
            )
            row = cursor.fetchone()
    return row[0]

def add_note_to_test_project(project_id: int, note_id: int):
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
            if cursor.rowcount == 1:
                return True
            else:
                return False

def add_photo_to_test_project(project_id: int, photo_id: int):
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
            if cursor.rowcount == 1:
                return True
            else:
                return False

def add_tag_to_test_project(project_id: int, tag_id: int):
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
            if cursor.rowcount == 1:
                return True
            else:
                return False
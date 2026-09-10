# APIを経由せずSQLでテストの前提データを作成する。APIの動作検証は各テストで行う。

from backend.db import get_connection

def create_test_photo(file_path : str):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO photos (file_path)
                    VALUES (%s)
                    RETURNING id;
                """, (file_path,)
            )
            row = cursor.fetchone()
    return row[0]

def add_tag_to_test_photo(photo_id: int, tag_id: str) -> bool:
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
    if rowcount == 1:
        return True
    else:
        return False
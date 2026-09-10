# APIを経由せずSQLでテストの前提データを作成する。APIの動作検証は各テストで行う。

from backend.db import get_connection

def create_tag_data(tag_name : str):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                    INSERT INTO tags (name)
                    VALUES (%s)
                    RETURNING id;
                """, (tag_name,)
            )
            row = cursor.fetchone()
    return row[0]


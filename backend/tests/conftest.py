# 実DBを使用するAPIテストの共通設定。接続先には必ずテスト専用DBを指定する。

import pytest
from fastapi.testclient import TestClient
from backend.db import get_connection
from backend.main import app

# 各テストの実行前に全データを削除し、採番も初期化してテスト間の依存をなくす。
@pytest.fixture(autouse=True)
def setup():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                    TRUNCATE TABLE
                        project_tags_relation,
                        note_tags_relation,
                        photo_tags_relation,
                        project_photos_relation,
                        note_photos_relation,
                        project_notes_relation,
                        notes,
                        photos,
                        tags,
                        projects
                    RESTART IDENTITY CASCADE;
                """
            )

@pytest.fixture
def client():
    return TestClient(app)

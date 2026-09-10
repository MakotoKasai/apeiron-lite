# apeiron-lite Backend

プロジェクト・ノート・写真のファイルパス・タグを管理するFastAPI製のAPIです。PostgreSQLにデータと関連付けを保存し、親ごとの表示順序を管理します。写真のアップロードや画像ファイルの配信は実装していません。

## 構成

```text
backend/
├── src/backend/
│   ├── main.py          # FastAPIアプリとルーターの登録
│   ├── db.py            # 環境設定とPostgreSQL接続
│   ├── schema.py        # 共通の並び替えリクエスト
│   ├── exceptions.py    # 共通例外
│   └── projects/・notes/・photos/・tags/
│       ├── router.py    # HTTP入出力とエラー応答
│       ├── schema.py    # Pydanticによる入力検証・応答モデル
│       ├── service.py   # SQLと業務処理
│       └── exceptions.py
├── db/docker/compose.yml
├── db/migrations/      # 001～010のテーブル作成SQL
└── tests/              # 実DBを使うAPIテストとデータ準備用helpers
```

## 開発環境の準備

Python 3.13以上、uv、Docker Composeを利用します。以下はPowerShellの例です。リポジトリのルートから移動し、以降は `backend` ディレクトリで実行します。

```powershell
cd backend
uv sync
```

### 環境変数

`backend/db/docker/.env` にPostgreSQLコンテナの初期設定を用意します。既存ファイルがある場合は値を確認して利用してください。以下の認証情報はローカル開発用の例です。

```dotenv
POSTGRES_DB=apeiron
POSTGRES_USER=apeiron
POSTGRES_PASSWORD=local_dev_password
```

`backend/.env` にAPIの接続先を設定します。ユーザー名・パスワードは上の設定に合わせます。

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=apeiron
DB_USER=apeiron
DB_PASSWORD=local_dev_password
```

設定はアプリのimport時に読み込まれます。環境変数は `.env` より優先され、`.env` の探索先は作業ディレクトリです。設定を変更した場合はアプリを再起動してください。認証情報を含む `.env` は共有・コミットしないでください。

### DBの起動とテーブル作成

```powershell
docker compose --env-file db/docker/.env -f db/docker/compose.yml up -d
docker compose --env-file db/docker/.env -f db/docker/compose.yml exec db pg_isready -U apeiron -d apeiron
```

接続受付を確認してから、空の開発DBへSQLを番号順に適用します。ユーザー名やDB名を変更した場合はコマンドも合わせてください。

```powershell
Get-ChildItem db/migrations/*.sql | Sort-Object Name | ForEach-Object {
    Get-Content -Raw -Encoding UTF8 $_.FullName |
        docker compose --env-file db/docker/.env -f db/docker/compose.yml exec -T db psql -U apeiron -d apeiron -v ON_ERROR_STOP=1
    if ($LASTEXITCODE -ne 0) { throw "SQLの適用に失敗しました: $($_.Name)" }
}
```

SQLは初回作成用で、適用履歴の管理や自動実行はありません。既存テーブルへの再実行は失敗します。Composeの名前付きボリュームにDBが保存されるため、通常の停止・再起動でデータは保持されます。既存ボリュームに対して `POSTGRES_*` を変更しても、作成済みユーザーやDBの設定は変更されません。

## APIの起動

```powershell
uv run fastapi dev src/backend/main.py
```

- API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- OpenAPI定義: <http://127.0.0.1:8000/openapi.json>

`uv run backend` は現在メッセージを表示するだけのコマンドで、APIサーバーを起動しません。

## APIの概要

| リソース | 操作 |
| --- | --- |
| `/projects` | GETで一覧、POSTで作成 |
| `/notes` | GETで一覧、POSTで作成 |
| `/photos` | GETで一覧、POSTで作成 |
| `/tags` | POSTで作成 |
| 上記の `/{id}` | GETで取得、PUTで更新、DELETEで削除 |
| `/tags/by_name/{tag_name}` | GETでタグ名の完全一致検索 |

作成・更新のJSONは、プロジェクトが `title` と `description`、ノートが `title` と `body`、写真が `file_path`、タグが `name` です。PUTでも各入力フィールドが必要です。タイトル・パス・タグ名は空文字や空白だけの値を拒否します。プロジェクトとノートのタイトルはDB側で255文字以内に制限されています。

関連付けは次のパスで操作します。

| パス | 対応メソッド |
| --- | --- |
| `/projects/{project_id}/notes`・`photos`・`tags` | GETで関連一覧 |
| `/projects/{project_id}/notes/{note_id}` | GET・POST・PUT・DELETE |
| `/projects/{project_id}/photos/{photo_id}` | POST・PUT・DELETE |
| `/projects/{project_id}/tags/{tag_id}` | POST・PUT・DELETE |
| `/notes/{note_id}/photos`・`tags` | GETで関連一覧 |
| `/notes/{note_id}/photos/{photo_id}` | POST・PUT・DELETE |
| `/notes/{note_id}/tags/{tag_id}` | POST・PUT・DELETE |
| `/photos/{photo_id}/tags` | GETで関連一覧 |
| `/photos/{photo_id}/tags/{tag_id}` | GET・POST・PUT・DELETE |

関連パスのPOSTは既存データの関連付け、DELETEは関連解除、PUTは `{"new_order": 2}` のようなJSONによる並び替えです。関連一覧は本体データと `sort_order` を返します。

成功時のステータスは操作によって201または204となるため、詳細はSwagger UIで確認してください。現在、プロジェクト・ノート・写真の作成APIは201を返しますが、作成したオブジェクトをレスポンスに返していません。必要に応じて一覧APIで確認してください。

## データと並び順

- タイトル（プロジェクト・ノート）、写真のパス、タグ名にはそれぞれ一意制約があります。
- 関連テーブルは親と子の組み合わせ、および親と `sort_order` の組み合わせを一意にします。
- 関連追加時は親ごとの最大順序に1を加えます。最初の要素は1です。
- 並び替えでは対象を一時的に `-1` へ退避し、移動区間の要素を順番に更新してから対象の順序を確定します。更新処理は同じ接続のトランザクション内で行います。
- 関連解除後に残りの順序を連番へ詰める処理はありません。並び替えの上限判定には件数ではなく最大順序を使っています。
- 現在のSQLには関連テーブルの外部キーやカスケード削除の定義がありません。本体削除時の関連行の自動削除は保証されません。

## テスト

**各テストの前に、接続先DBの全10テーブルをTRUNCATEし、IDの採番も初期化します。必ずテスト専用DBを使用してください。** APIを別途起動する必要はありません。TestClientがアプリを直接呼び出しますが、PostgreSQLは必要です。

初回のみ専用DBを作成してSQLを適用します。

```powershell
docker compose --env-file db/docker/.env -f db/docker/compose.yml exec db createdb -U apeiron apeiron_test
Get-ChildItem db/migrations/*.sql | Sort-Object Name | ForEach-Object {
    Get-Content -Raw -Encoding UTF8 $_.FullName |
        docker compose --env-file db/docker/.env -f db/docker/compose.yml exec -T db psql -U apeiron -d apeiron_test -v ON_ERROR_STOP=1
    if ($LASTEXITCODE -ne 0) { throw "SQLの適用に失敗しました: $($_.Name)" }
}
```

接続先をテスト実行中だけ切り替えます。他の接続設定は `backend/.env` を利用します。

```powershell
$previousDbName = $env:DB_NAME
try {
    $env:DB_NAME = "apeiron_test"
    uv run pytest tests -q
} finally {
    $env:DB_NAME = $previousDbName
}
```

特定のテストだけを実行する場合は、同じ接続先設定で `uv run pytest tests/test_project.py -q` のように指定します。テストがDB全体を初期化するため、同じDBを使うテストの並列実行は避けてください。

## トラブルシューティング

- 設定読み込みエラー：作業ディレクトリが `backend` であることと、5つの `DB_*` 設定を確認します。
- DB接続エラー：コンテナの起動状態、5432ポート、ユーザー名・パスワード・DB名を確認します。
- テーブルが見つからない：実際の接続先DBに `db/migrations` のSQLが適用されているか確認します。
- `uv` が見つからない：uvをインストールし、PATHが反映されたターミナルで実行します。

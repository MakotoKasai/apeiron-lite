# DB接続設定を環境変数・作業ディレクトリの .env から読み込む。

import psycopg
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: str

    model_config=SettingsConfigDict(env_file=".env")

# import時に設定を確定するため、環境変数は起動前に指定する。
settings = Settings()

# 呼び出し側の with で正常終了時はコミット、例外時はロールバックし、接続を閉じる。
def get_connection():
    return psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )
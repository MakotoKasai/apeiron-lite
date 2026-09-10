# 機能ごとのルーターを登録するFastAPIアプリケーションの入口。

from fastapi import FastAPI

from .projects.router import router as projects_router
from .notes.router import router as notes_router
from .photos.router import router as photos_router
from .tags.router import router as tags_router

app = FastAPI()
app.include_router(projects_router)
app.include_router(notes_router)
app.include_router(photos_router)
app.include_router(tags_router)

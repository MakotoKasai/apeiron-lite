CREATE TABLE photos (
    id BIGSERIAL PRIMARY KEY ,
    file_path TEXT NOT NULL UNIQUE
                      CONSTRAINT chk_project_title_not_blank
                      CHECK (btrim(file_path) <> ''),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
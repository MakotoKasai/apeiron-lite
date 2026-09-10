CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
                      CONSTRAINT chk_project_title_not_blank
                      CHECK (btrim(name) <> ''),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
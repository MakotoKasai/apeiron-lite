CREATE TABLE notes (
    id BIGSERIAL PRIMARY KEY ,
    title VARCHAR(255) NOT NULL UNIQUE
                      CONSTRAINT chk_note_title_not_blank
                      CHECK (btrim(title) <> ''),
    body TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
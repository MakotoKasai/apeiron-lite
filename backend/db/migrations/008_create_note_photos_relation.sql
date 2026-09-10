CREATE TABLE note_photos_relation (
    note_id BIGINT NOT NULL,
    photo_id BIGINT NOT NULL,
    sort_order INTEGER NOT NULL,

    PRIMARY KEY (note_id, photo_id),
    UNIQUE(note_id, sort_order)
);
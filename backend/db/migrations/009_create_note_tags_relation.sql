CREATE TABLE note_tags_relation (
    note_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    sort_order INTEGER NOT NULL,

    PRIMARY KEY (note_id, tag_id),
    UNIQUE(note_id, sort_order)
);
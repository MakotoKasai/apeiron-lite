CREATE TABLE photo_tags_relation (
    photo_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    sort_order INTEGER NOT NULL,

    PRIMARY KEY (photo_id, tag_id),
    UNIQUE(photo_id, sort_order)
);
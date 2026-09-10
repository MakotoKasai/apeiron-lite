CREATE TABLE project_photos_relation (
    project_id BIGINT NOT NULL,
    photo_id BIGINT NOT NULL,
    sort_order INTEGER NOT NULL,

    PRIMARY KEY (project_id, photo_id),
    UNIQUE(project_id, sort_order)
);
CREATE TABLE project_tags_relation (
    project_id BIGINT NOT NULL,
    tag_id BIGINT NOT NULL,
    sort_order INTEGER NOT NULL,

    PRIMARY KEY (project_id, tag_id),
    UNIQUE(project_id, sort_order)
);
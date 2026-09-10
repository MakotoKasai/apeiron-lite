CREATE TABLE project_notes_relation (
    project_id BIGINT NOT NULL,
    note_id BIGINT NOT NULL,
    sort_order INTEGER NOT NULL,

    PRIMARY KEY (project_id, note_id),
    UNIQUE(project_id, sort_order)
);
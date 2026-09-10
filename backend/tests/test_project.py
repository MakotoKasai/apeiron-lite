from backend.projects.service import add_tag_to_project, add_photo_to_project
from .helpers.note import create_test_note
from .helpers.photo import create_test_photo
from .helpers.project import create_test_project, add_note_to_test_project
from .helpers.tag import create_tag_data


def test_get_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    response = client.get(
        "/projects/{}".format(project_id)
    )
    assert response.status_code == 200
    assert response.json()["id"] == project_id
    assert response.json()["title"] == "test-project"
    assert response.json()["description"] == "This is a test project"

def test_get_project_with_unknown_id(client):
    response = client.get(
        "/projects/999999"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_create_project(client):
    response = client.post(
        "/projects",
        json={
            "title": "",
            "description": "This is a test project",
        }
    )
    assert response.status_code == 422

    response = client.post(
        "/projects",
        json={
                "title": "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345",
            "description": "This is a test project",
        }
    )
    assert response.status_code == 422

    response = client.post(
        "/projects",
        json={
            "title": "012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234",
            "description": "This is a test project",
        }
    )
    assert response.status_code == 201

    response = client.post(
        "/projects",
        json={
            "title": "test-project",
            "description": "This is a test project",
        }
    )
    assert response.status_code == 201

def test_create_project_with_duplicate_title(client):
    project_id = create_test_project("test-project", "This is a test project")
    response = client.post(
        "/projects",
        json={
            "title": "test-project",
            "description": "This is a test project",
        }
    )
    assert response.status_code == 409

def test_update_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    response = client.put(
        "/projects/{}".format(project_id),
        json={
            "title": "update-project",
            "description": "This is update test project",
        }
    )
    assert response.status_code == 200
    assert response.json()["title"] == "update-project"
    assert response.json()["description"] == "This is update test project"

def test_update_project_with_duplicate_title(client):
    project_id = create_test_project("test-project", "This is a test project")
    create_test_project("update-project", "This is a test project")
    response = client.put(
        "/projects/{}".format(project_id),
        json={
            "title": "update-project",
            "description": "This is update test project",
        }
    )

    assert response.status_code == 409

def test_update_project_with_unknown_id(client):
    project_id = create_test_project("test-project", "This is a test project")
    response = client.put(
        "/projects/999999",
        json={
            "title": "update-project",
            "description": "This is update test project",
        }
    )
    assert response.status_code == 404

def test_delete_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    response = client.delete(
        "/projects/{}".format(project_id)
    )
    assert response.status_code == 204

    response2 = client.get(
        "/projects/{}".format(project_id)
    )
    assert response2.status_code == 404

def test_delete_project_with_unknown_id(client):
    project_id = create_test_project("test-project", "This is a test project")
    response = client.delete(
        "/projects/999999"
    )
    assert response.status_code == 404

def test_create_project_with_blank_title(client):
    response = client.post(
        "/projects",
        json={
            "title": "",
            "description": "This is a test project",
        }
    )
    assert response.status_code == 422

def test_add_note_to_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    note_id = create_test_note("test-note","This is a test note")
    response = client.post(f"/projects/{project_id}/notes/{note_id}")
    assert response.status_code == 201

    response2 = client.post(f"/projects/{project_id}/notes/{note_id}")
    assert response2.status_code == 409

def test_get_note_from_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    note_id = create_test_note("test-note", "This is a test note")

    response3 = client.get(f"/projects/{project_id}/notes")
    assert response3.status_code == 200
    assert len(response3.json()) == 0

    add_note_to_test_project(project_id, note_id)

    response3 = client.get(f"/projects/{project_id}/notes")
    assert response3.status_code == 200
    assert len(response3.json()) == 1

    response3 = client.get(f"/projects/{project_id}/notes/{note_id}")
    assert response3.status_code == 200
    assert response3.json()["note"]["id"] == note_id
    assert response3.json()["sort_order"] == 1

def test_remove_note_from_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    note_id = create_test_note("test-note","This is a test note")
    add_note_to_test_project(project_id, note_id)
    response = client.delete(f"/projects/{project_id}/notes/{note_id}")
    assert response.status_code == 204
    response2 = client.get(f"/projects/{project_id}/notes/{note_id}")
    assert response2.status_code == 404

def test_reorder_note_within_project_shift_up(client):
    project_id = create_test_project("test-project", "This is a test project")
    note_id1 = create_test_note("test-note1","This is a test note1")
    note_id2 = create_test_note("test-note2", "This is a test note2")
    note_id3 = create_test_note("test-note3", "This is a test note3")
    note_id4 = create_test_note("test-note4", "This is a test note4")
    add_note_to_test_project(project_id, note_id1)
    add_note_to_test_project(project_id, note_id2)
    add_note_to_test_project(project_id, note_id3)
    add_note_to_test_project(project_id, note_id4)

    response = client.get(f"/projects/{project_id}/notes/{note_id1}")
    print(response.json())
    assert response.status_code == 200
    assert response.json()["note"]["id"] == note_id1
    assert response.json()["sort_order"] == 1

    response2 = client.get(f"/projects/{project_id}/notes/{note_id2}")
    print(response2.json())
    assert response2.status_code == 200
    assert response2.json()["note"]["id"] == note_id2
    assert response2.json()["sort_order"] == 2

    response3 = client.get(f"/projects/{project_id}/notes/{note_id3}")
    print(response3.json())
    assert response3.status_code == 200
    assert response3.json()["note"]["id"] == note_id3
    assert response3.json()["sort_order"] == 3

    response4 = client.get(f"/projects/{project_id}/notes/{note_id4}")
    print(response4.json())
    assert response4.status_code == 200
    assert response4.json()["note"]["id"] == note_id4
    assert response4.json()["sort_order"] == 4

    response5 = client.put(f"/projects/{project_id}/notes/{note_id4}",
                           json={
                               "new_order": 1
                           })
    assert response5.status_code == 204

    response6 = client.get(f"/projects/{project_id}/notes/{note_id1}")
    print(response6.json())
    assert response6.status_code == 200
    assert response6.json()["note"]["id"] == note_id1
    assert response6.json()["sort_order"] == 2


    response7 = client.get(f"/projects/{project_id}/notes/{note_id2}")
    print(response7.json())
    assert response7.status_code == 200
    assert response7.json()["note"]["id"] == note_id2
    assert response7.json()["sort_order"] == 3


    response8 = client.get(f"/projects/{project_id}/notes/{note_id3}")
    print(response8.json())
    assert response8.status_code == 200
    assert response8.json()["note"]["id"] == note_id3
    assert response8.json()["sort_order"] == 4


    response9 = client.get(f"/projects/{project_id}/notes/{note_id4}")
    print(response9.json())
    assert response9.status_code == 200
    assert response9.json()["note"]["id"] == note_id4
    assert response9.json()["sort_order"] == 1


def test_reorder_note_within_project_shift_down(client):
    project_id = create_test_project("test-project", "This is a test project")
    note_id1 = create_test_note("test-note1","This is a test note1")
    note_id2 = create_test_note("test-note2", "This is a test note2")
    note_id3 = create_test_note("test-note3", "This is a test note3")
    note_id4 = create_test_note("test-note4", "This is a test note4")
    add_note_to_test_project(project_id, note_id1)
    add_note_to_test_project(project_id, note_id2)
    add_note_to_test_project(project_id, note_id3)
    add_note_to_test_project(project_id, note_id4)

    response = client.get(f"/projects/{project_id}/notes/{note_id1}")
    print(response.json())
    assert response.status_code == 200
    assert response.json()["note"]["id"] == note_id1
    assert response.json()["sort_order"] == 1

    response2 = client.get(f"/projects/{project_id}/notes/{note_id2}")
    print(response2.json())
    assert response2.status_code == 200
    assert response2.json()["note"]["id"] == note_id2
    assert response2.json()["sort_order"] == 2

    response3 = client.get(f"/projects/{project_id}/notes/{note_id3}")
    print(response3.json())
    assert response3.status_code == 200
    assert response3.json()["note"]["id"] == note_id3
    assert response3.json()["sort_order"] == 3

    response4 = client.get(f"/projects/{project_id}/notes/{note_id4}")
    print(response4.json())
    assert response4.status_code == 200
    assert response4.json()["note"]["id"] == note_id4
    assert response4.json()["sort_order"] == 4

    response5 = client.put(f"/projects/{project_id}/notes/{note_id1}",
                           json={
                               "new_order": 3
                           })
    assert response5.status_code == 204

    response6 = client.get(f"/projects/{project_id}/notes/{note_id1}")
    print(response6.json())
    assert response6.status_code == 200
    assert response6.json()["note"]["id"] == note_id1
    assert response6.json()["sort_order"] == 3

    response7 = client.get(f"/projects/{project_id}/notes/{note_id2}")
    print(response7.json())
    assert response7.status_code == 200
    assert response7.json()["note"]["id"] == note_id2
    assert response7.json()["sort_order"] == 1

    response8 = client.get(f"/projects/{project_id}/notes/{note_id3}")
    print(response8.json())
    assert response8.status_code == 200
    assert response8.json()["note"]["id"] == note_id3
    assert response8.json()["sort_order"] == 2

    response9 = client.get(f"/projects/{project_id}/notes/{note_id4}")
    print(response9.json())
    assert response9.status_code == 200
    assert response9.json()["note"]["id"] == note_id4
    assert response9.json()["sort_order"] == 4

def test_add_photo_to_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    photo_id = create_test_photo("PathA")
    photo_id2 = create_test_photo("PathB")

    response = client.post(f"/projects/{project_id}/photos/{photo_id}")
    assert response.status_code == 201

    response = client.post(f"/projects/{project_id}/photos/{photo_id}")
    assert response.status_code == 409

    response = client.post(f"/projects/{project_id}/photos/{photo_id2}")
    assert response.status_code == 201

def test_get_photo_from_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    photo_id = create_test_photo("PathA")
    photo_id2 = create_test_photo("PathB")

    response = client.get(f"/projects/{project_id}/photos")
    assert response.status_code == 200
    assert len(response.json()) == 0

    add_photo_to_project(project_id, photo_id)

    response = client.get(f"/projects/{project_id}/photos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["photo"]["id"] == photo_id

    add_photo_to_project(project_id, photo_id2)

    response = client.get(f"/projects/{project_id}/photos")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_reorder_photos_in_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    photo_id = create_test_photo("Path")
    photo_id1 = create_test_photo("PathA")
    photo_id2 = create_test_photo("PathB")
    photo_id3 = create_test_photo("PathC")
    photo_id4 = create_test_photo("PathD")

    add_photo_to_project(project_id, photo_id1)
    add_photo_to_project(project_id, photo_id2)
    add_photo_to_project(project_id, photo_id3)
    add_photo_to_project(project_id, photo_id4)

    response = client.put(f"/projects/{project_id}/photos/{photo_id}",
                          json={
                              "new_order": 3
                          })
    assert response.status_code == 404

    response = client.put(f"/projects/{project_id}/photos/{photo_id1}",
                          json={
                              "new_order": 3
                          })
    assert response.status_code == 204

    response = client.get(f"/projects/{project_id}/photos/")
    assert response.status_code == 200
    assert response.json()[0]["photo"]["id"] == photo_id2
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["photo"]["id"] == photo_id3
    assert response.json()[1]["sort_order"] == 2
    assert response.json()[2]["photo"]["id"] == photo_id1
    assert response.json()[2]["sort_order"] == 3
    assert response.json()[3]["photo"]["id"] == photo_id4
    assert response.json()[3]["sort_order"] == 4


def test_remove_photo_from_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    photo_id = create_test_photo("PathA")
    photo_id2 = create_test_photo("PathB")

    add_photo_to_project(project_id, photo_id)

    response = client.delete(f"/projects/{project_id}/photos/{photo_id}")
    assert response.status_code == 204

    response = client.delete(f"/projects/{project_id}/photos/{photo_id2}")
    assert response.status_code == 404

def test_add_tag_to_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    tag_id1 = create_tag_data("tag1")
    tag_id2 = create_tag_data("tag2")

    response = client.post(f"/projects/{project_id}/tags/{tag_id1}")
    assert response.status_code == 201

    response = client.post(f"/projects/{project_id}/tags/{tag_id1}")
    assert response.status_code == 409

    response = client.post(f"/projects/{project_id}/tags/{tag_id2}")
    assert response.status_code == 201

def test_get_tag_from_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    tag_id1 = create_tag_data("tag1")
    tag_id2 = create_tag_data("tag2")

    response = client.get(f"/projects/{project_id}/tags")
    assert response.status_code == 200
    assert len(response.json()) == 0

    add_tag_to_project(project_id, tag_id1)

    response = client.get(f"/projects/{project_id}/tags")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["tag"]["id"] == tag_id1

    add_tag_to_project(project_id, tag_id2)
    response = client.get(f"/projects/{project_id}/tags")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_reorder_tags_in_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    tag_id1 = create_tag_data("tag1")
    tag_id2 = create_tag_data("tag2")
    tag_id3 = create_tag_data("tag3")
    tag_id4 = create_tag_data("tag4")
    tag_id5 = create_tag_data("tag5")

    add_tag_to_project(project_id, tag_id1)
    add_tag_to_project(project_id, tag_id2)
    add_tag_to_project(project_id, tag_id3)
    add_tag_to_project(project_id, tag_id4)

    response = client.put(f"/projects/{project_id}/tags/{tag_id5}",
                          json={"new_order": 1})
    assert response.status_code == 404

    response = client.put(f"/projects/{project_id}/tags/{tag_id4}",
                          json={"new_order": 1})
    assert response.status_code == 204

    response = client.get(f"/projects/{project_id}/tags")
    assert response.status_code == 200
    assert response.json()[0]["tag"]["id"] == tag_id4
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["tag"]["id"] == tag_id1
    assert response.json()[1]["sort_order"] == 2
    assert response.json()[2]["tag"]["id"] == tag_id2
    assert response.json()[2]["sort_order"] == 3
    assert response.json()[3]["tag"]["id"] == tag_id3
    assert response.json()[3]["sort_order"] == 4

def test_remove_tag_from_project(client):
    project_id = create_test_project("test-project", "This is a test project")
    tag_id1 = create_tag_data("tag1")
    tag_id2 = create_tag_data("tag2")

    add_tag_to_project(project_id, tag_id1)

    response = client.delete(f"/projects/{project_id}/tags/{tag_id1}")
    assert response.status_code == 204

    response = client.delete(f"/projects/{project_id}/tags/{tag_id2}")
    assert response.status_code == 404

def test_note_through_operation(client):
    project_id = create_test_project("test-project", "This is a test project")
    note_id1 = create_test_note("note1", "note-body")

    response = client.get(f"/projects/{project_id}/notes")
    assert response.status_code == 200
    assert len(response.json()) == 0

    response = client.post(f"/projects/999999/notes/888888")
    assert response.status_code == 404
    response = client.post(f"/projects/{project_id}/notes/999999")
    assert response.status_code == 404
    response = client.post(f"/projects/999999/notes/{note_id1}")
    assert response.status_code == 404
    response = client.post(f"/projects/{project_id}/notes/{note_id1}")
    assert response.status_code == 201
    response = client.post(f"/projects/{project_id}/notes/{note_id1}")
    assert response.status_code == 409

    response = client.get(f"/projects/{project_id}/notes/{note_id1}")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()["note"]["id"] == note_id1
    assert response.json()["note"]["title"] == "note1"
    assert response.json()["note"]["body"] == "note-body"
    response = client.get(f"/projects/{project_id}/notes/888888")
    assert response.status_code == 404
    response = client.get(f"/projects/999999/notes/{note_id1}")
    assert response.status_code == 404


    note_id2= create_test_note("note2", "note-body")
    response = client.post(f"/projects/{project_id}/notes/{note_id2}")
    assert response.status_code == 201

    response = client.put(f"/projects/{project_id}/notes/{note_id1}",
                          json={"new_order": 0})
    assert response.status_code == 400
    response = client.put(f"/projects/{project_id}/notes/{note_id1}",
                          json={"new_order":1})
    assert response.status_code == 204
    response = client.put(f"/projects/{project_id}/notes/{note_id1}",
                          json={"new_order": 2})
    assert response.status_code == 204
    response = client.put(f"/projects/{project_id}/notes/{note_id1}",
                          json={"new_order": 3})
    assert response.status_code == 400

    response = client.delete(f"/projects/{project_id}/notes/{note_id1}")
    assert response.status_code == 204

    response = client.get(f"/projects/{project_id}/notes/{note_id1}")
    assert response.status_code == 404

def test_photo_through_operation(client):
    project_id = create_test_project("test-project", "This is a test project")
    photo_id1 = create_test_photo("Photo")

    response = client.get(f"/projects/{project_id}/photos")
    assert response.status_code == 200
    assert len(response.json()) == 0

    response = client.post(f"/projects/999999/photos/888888")
    assert response.status_code == 404
    response = client.post(f"/projects/{project_id}/photos/999999")
    assert response.status_code == 404
    response = client.post(f"/projects/999999/photos/{photo_id1}")
    assert response.status_code == 404
    response = client.post(f"/projects/{project_id}/photos/{photo_id1}")
    assert response.status_code == 201
    response = client.post(f"/projects/{project_id}/photos/{photo_id1}")
    assert response.status_code == 409

    response = client.get(f"/projects/{project_id}/photos")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["photo"]["id"] == photo_id1
    assert response.json()[0]["photo"]["file_path"] == "Photo"
    response = client.get(f"/projects/999999/photos")
    assert response.status_code == 404

    photo_id2= create_test_photo("Photo2")
    response = client.post(f"/projects/{project_id}/photos/{photo_id2}")
    assert response.status_code == 201

    response = client.put(f"/projects/{project_id}/photos/{photo_id1}",
                          json={"new_order": 0})
    assert response.status_code == 400
    response = client.put(f"/projects/{project_id}/photos/{photo_id1}",
                          json={"new_order":1})
    assert response.status_code == 204
    response = client.put(f"/projects/{project_id}/photos/{photo_id1}",
                          json={"new_order": 2})
    assert response.status_code == 204
    response = client.put(f"/projects/{project_id}/photos/{photo_id1}",
                          json={"new_order": 3})
    assert response.status_code == 400

    response = client.delete(f"/projects/{project_id}/photos/{photo_id2}")
    assert response.status_code == 204

    response = client.get(f"/projects/{project_id}/photos")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_tag_through_operation(client):
    project_id = create_test_project("test-project", "This is a test project")
    tag_id1 = create_tag_data("Tag")

    response = client.get(f"/projects/{project_id}/tags")
    assert response.status_code == 200
    assert len(response.json()) == 0

    response = client.post(f"/projects/999999/tags/888888")
    assert response.status_code == 404
    response = client.post(f"/projects/{project_id}/tags/999999")
    assert response.status_code == 404
    response = client.post(f"/projects/999999/tags/{tag_id1}")
    assert response.status_code == 404
    response = client.post(f"/projects/{project_id}/tags/{tag_id1}")
    assert response.status_code == 201
    response = client.post(f"/projects/{project_id}/tags/{tag_id1}")
    assert response.status_code == 409

    response = client.get(f"/projects/{project_id}/tags")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["tag"]["id"] == tag_id1
    assert response.json()[0]["tag"]["name"] == "Tag"
    response = client.get(f"/projects/999999/tags")
    assert response.status_code == 404


    tag_id2= create_tag_data("Tag2")
    response = client.post(f"/projects/{project_id}/tags/{tag_id2}")
    assert response.status_code == 201

    response = client.put(f"/projects/{project_id}/tags/{tag_id1}",
                          json={"new_order": 0})
    assert response.status_code == 400
    response = client.put(f"/projects/{project_id}/tags/{tag_id1}",
                          json={"new_order":1})
    assert response.status_code == 204
    response = client.put(f"/projects/{project_id}/tags/{tag_id1}",
                          json={"new_order": 2})
    assert response.status_code == 204
    response = client.put(f"/projects/{project_id}/tags/{tag_id1}",
                          json={"new_order": 3})
    assert response.status_code == 400

    response = client.delete(f"/projects/{project_id}/tags/{tag_id2}")
    assert response.status_code == 204

    response = client.get(f"/projects/{project_id}/tags")
    assert response.status_code == 200
    assert len(response.json()) == 1



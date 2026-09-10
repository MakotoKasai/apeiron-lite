from backend.notes.service import add_photo_to_note
from .helpers.note import create_test_note, add_photo_to_test_note, add_tag_to_test_note
from .helpers.photo import create_test_photo
from .helpers.tag import create_tag_data


def test_get_note(client):
    note_id = create_test_note("test_title", "test_body")
    response = client.get(f"/notes/{note_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "test_title"
    assert response.json()["body"] == "test_body"

def test_get_note_with_invalid_note_id(client):
    note_id = create_test_note("test_title", "test_body")
    response = client.get(f"/notes/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

def test_create_note(client):
    response = client.post("/notes",
                           json={
                               "title": "test_title",
                               "body": "test_body",
                           })
    assert response.status_code == 201

    response2 = client.post("/notes",
                            json={
                                "title": "test_title",
                                "body": "test_body",
                            })
    assert response2.status_code == 409

    response = client.post(
        "/notes",
        json={
            "title": "",
            "body": "test_body",
        }
    )
    assert response.status_code == 422

    response = client.post(
        "/notes",
        json={
            "title": "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345",
            "body": "test_body",
        }
    )
    assert response.status_code == 422

    response = client.post(
        "/notes",
        json={
            "title": "012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234",
            "body": "test_body",
        }
    )
    assert response.status_code == 201

def test_create_note_with_invalid_title(client):
    response = client.post("/notes",
                           json={
                                "title": "",
                               "body": "test_body",
                           })
    assert response.status_code == 422

def test_update_note(client):
    note_id = create_test_note("test_title", "test_body")
    response = client.put(f"/notes/{note_id}",
                          json={
                              "title": "test_title2",
                              "body": "test_body2",
                          })
    assert response.status_code == 200
    assert response.json()["title"] == "test_title2"
    assert response.json()["body"] == "test_body2"

    response2 = client.put(f"/notes/{note_id}",
                           json={
                               "title": "",
                               "body": "test_body2",
                           })
    assert response2.status_code == 422

def test_delete_note(client):
    note_id = create_test_note("test_title", "test_body")
    response = client.delete(f"/notes/{note_id}")
    assert response.status_code == 204

    response2 = client.delete(f"/notes/{note_id}")
    assert response2.status_code == 404

def test_get_photo_from_note(client):
    note_id = create_test_note("test_title", "test_body")
    photo_id1 = create_test_photo("filePathA")
    photo_id2 = create_test_photo("filePathB")
    print(photo_id1)
    print(photo_id2)

    add_photo_to_test_note(note_id, photo_id1)
    add_photo_to_test_note(note_id, photo_id2)

    response = client.get(f"/notes/{note_id}/photos")
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["photo"]["file_path"] == "filePathA"
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["photo"]["file_path"] == "filePathB"
    assert response.json()[1]["sort_order"] == 2

def test_add_photo_to_note(client):
    note_id = create_test_note("test_title", "test_body")
    photo_id1 = create_test_photo("filePathA")

    response = client.post(f"/notes/{note_id}/photos/{photo_id1}",)

def test_remove_photo_from_note(client):
    note_id = create_test_note("test_title", "test_body")
    photo_id1 = create_test_photo("filePathA")

    response = client.delete(f"/notes/{note_id}/photos/{photo_id1}")
    assert response.status_code == 404

    add_photo_to_test_note(note_id, photo_id1)

    response = client.delete(f"/notes/{note_id}/photos/{photo_id1}")
    assert response.status_code == 204

    response2 = client.get(f"/notes/{note_id}/photos")
    print(response2.json())
    assert response2.status_code == 200
    assert response2.json() == []

def test_shift_down_photo_order_in_note(client):
    note_id = create_test_note("test_title", "test_body")
    photo_id1 = create_test_photo("filePathA")
    photo_id2 = create_test_photo("filePathB")
    photo_id3 = create_test_photo("filePathC")
    photo_id4 = create_test_photo("filePathD")

    response = client.put(f"/notes/{note_id}/photos/{photo_id4}",
                          json={
                              "new_order": 2
                          })
    assert response.status_code == 404

    add_photo_to_test_note(note_id, photo_id1)
    add_photo_to_test_note(note_id, photo_id2)
    add_photo_to_test_note(note_id, photo_id3)
    add_photo_to_test_note(note_id, photo_id4)

    response = client.get(f"/notes/{note_id}/photos")
    assert response.status_code == 200
    assert len(response.json()) == 4
    assert response.json()[0]["photo"]["file_path"] == "filePathA"
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["photo"]["file_path"] == "filePathB"
    assert response.json()[1]["sort_order"] == 2
    assert response.json()[2]["photo"]["file_path"] == "filePathC"
    assert response.json()[2]["sort_order"] == 3
    assert response.json()[3]["photo"]["file_path"] == "filePathD"
    assert response.json()[3]["sort_order"] == 4

    response = client.put(f"/notes/{note_id}/photos/{photo_id4}",
                          json={
                              "new_order": 2
                          })
    assert response.status_code == 204

    response2 = client.get(f"/notes/{note_id}/photos")
    print(response2.json())
    assert response2.status_code == 200
    assert len(response2.json()) == 4
    assert response2.json()[0]["photo"]["file_path"] == "filePathA"
    assert response2.json()[0]["sort_order"] == 1
    assert response2.json()[1]["photo"]["file_path"] == "filePathD"
    assert response2.json()[1]["sort_order"] == 2
    assert response2.json()[2]["photo"]["file_path"] == "filePathB"
    assert response2.json()[2]["sort_order"] == 3
    assert response2.json()[3]["photo"]["file_path"] == "filePathC"
    assert response2.json()[3]["sort_order"] == 4

def test_shift_up_photo_order_in_note(client):
    note_id = create_test_note("test_title", "test_body")
    photo_id1 = create_test_photo("filePathA")
    photo_id2 = create_test_photo("filePathB")
    photo_id3 = create_test_photo("filePathC")
    photo_id4 = create_test_photo("filePathD")

    response = client.put(f"/notes/{note_id}/photos/{photo_id1}",
                          json={
                              "new_order": 3
                          })
    assert response.status_code == 404

    add_photo_to_test_note(note_id, photo_id1)
    add_photo_to_test_note(note_id, photo_id2)
    add_photo_to_test_note(note_id, photo_id3)
    add_photo_to_test_note(note_id, photo_id4)

    response = client.get(f"/notes/{note_id}/photos")
    assert response.status_code == 200
    assert len(response.json()) == 4
    assert response.json()[0]["photo"]["file_path"] == "filePathA"
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["photo"]["file_path"] == "filePathB"
    assert response.json()[1]["sort_order"] == 2
    assert response.json()[2]["photo"]["file_path"] == "filePathC"
    assert response.json()[2]["sort_order"] == 3
    assert response.json()[3]["photo"]["file_path"] == "filePathD"
    assert response.json()[3]["sort_order"] == 4

    response = client.put(f"/notes/{note_id}/photos/{photo_id1}",
                          json={
                              "new_order": 3
                          })
    assert response.status_code == 204

    response2 = client.get(f"/notes/{note_id}/photos")
    print(response2.json())
    assert response2.status_code == 200
    assert len(response2.json()) == 4
    assert response2.json()[0]["photo"]["file_path"] == "filePathB"
    assert response2.json()[0]["sort_order"] == 1
    assert response2.json()[1]["photo"]["file_path"] == "filePathC"
    assert response2.json()[1]["sort_order"] == 2
    assert response2.json()[2]["photo"]["file_path"] == "filePathA"
    assert response2.json()[2]["sort_order"] == 3
    assert response2.json()[3]["photo"]["file_path"] == "filePathD"
    assert response2.json()[3]["sort_order"] == 4

def test_get_tag_from_note(client):
    note_id = create_test_note("test_title", "test_body")
    tag_id1 = create_tag_data("filePathA")
    tag_id2 = create_tag_data("filePathB")
    add_tag_to_test_note(note_id, tag_id1)
    add_tag_to_test_note(note_id, tag_id2)

    response = client.get(f"/notes/{note_id}/tags")
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["tag"]["name"] == "filePathA"
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["tag"]["name"] == "filePathB"
    assert response.json()[1]["sort_order"] == 2

def test_remove_tag_from_note(client):
    note_id = create_test_note("test_title", "test_body")
    tag_id1 = create_tag_data("filePathA")

    response = client.delete(f"/notes/{note_id}/tags/{tag_id1}")
    assert response.status_code == 404

    add_tag_to_test_note(note_id, tag_id1)

    response = client.delete(f"/notes/{note_id}/tags/{tag_id1}")
    assert response.status_code == 204

    response2 = client.get(f"/notes/{note_id}/tags")
    print(response2.json())
    assert response2.status_code == 200
    assert response2.json() == []

def test_shift_down_tag_order_in_note(client):
    note_id = create_test_note("test_title", "test_body")
    tag_id1 = create_tag_data("filePathA")
    tag_id2 = create_tag_data("filePathB")
    tag_id3 = create_tag_data("filePathC")
    tag_id4 = create_tag_data("filePathD")

    response = client.put(f"/notes/{note_id}/tags/{tag_id4}",
                          json={
                              "new_order": 2
                          })
    assert response.status_code == 404

    add_tag_to_test_note(note_id, tag_id1)
    add_tag_to_test_note(note_id, tag_id2)
    add_tag_to_test_note(note_id, tag_id3)
    add_tag_to_test_note(note_id, tag_id4)

    response = client.get(f"/notes/{note_id}/tags")
    assert response.status_code == 200
    assert len(response.json()) == 4
    assert response.json()[0]["tag"]["name"] == "filePathA"
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["tag"]["name"] == "filePathB"
    assert response.json()[1]["sort_order"] == 2
    assert response.json()[2]["tag"]["name"] == "filePathC"
    assert response.json()[2]["sort_order"] == 3
    assert response.json()[3]["tag"]["name"] == "filePathD"
    assert response.json()[3]["sort_order"] == 4

    response = client.put(f"/notes/{note_id}/tags/{tag_id4}",
                          json={
                              "new_order": 2
                          })
    assert response.status_code == 204

    response2 = client.get(f"/notes/{note_id}/tags")
    print(response2.json())
    assert response2.status_code == 200
    assert len(response2.json()) == 4
    assert response2.json()[0]["tag"]["name"] == "filePathA"
    assert response2.json()[0]["sort_order"] == 1
    assert response2.json()[1]["tag"]["name"] == "filePathD"
    assert response2.json()[1]["sort_order"] == 2
    assert response2.json()[2]["tag"]["name"] == "filePathB"
    assert response2.json()[2]["sort_order"] == 3
    assert response2.json()[3]["tag"]["name"] == "filePathC"
    assert response2.json()[3]["sort_order"] == 4

def test_shift_up_tag_order_in_note(client):
    note_id = create_test_note("test_title", "test_body")
    tag_id1 = create_tag_data("filePathA")
    tag_id2 = create_tag_data("filePathB")
    tag_id3 = create_tag_data("filePathC")
    tag_id4 = create_tag_data("filePathD")

    response = client.put(f"/notes/{note_id}/tags/{tag_id1}",
                          json={
                              "new_order": 3
                          })
    assert response.status_code == 404

    add_tag_to_test_note(note_id, tag_id1)
    add_tag_to_test_note(note_id, tag_id2)
    add_tag_to_test_note(note_id, tag_id3)
    add_tag_to_test_note(note_id, tag_id4)

    response = client.get(f"/notes/{note_id}/tags")
    assert response.status_code == 200
    assert len(response.json()) == 4
    assert response.json()[0]["tag"]["name"] == "filePathA"
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["tag"]["name"] == "filePathB"
    assert response.json()[1]["sort_order"] == 2
    assert response.json()[2]["tag"]["name"] == "filePathC"
    assert response.json()[2]["sort_order"] == 3
    assert response.json()[3]["tag"]["name"] == "filePathD"
    assert response.json()[3]["sort_order"] == 4

    response = client.put(f"/notes/{note_id}/tags/{tag_id1}",
                          json={
                              "new_order": 3
                          })
    assert response.status_code == 204

    response2 = client.get(f"/notes/{note_id}/tags")
    print(response2.json())
    assert response2.status_code == 200
    assert len(response2.json()) == 4
    assert response2.json()[0]["tag"]["name"] == "filePathB"
    assert response2.json()[0]["sort_order"] == 1
    assert response2.json()[1]["tag"]["name"] == "filePathC"
    assert response2.json()[1]["sort_order"] == 2
    assert response2.json()[2]["tag"]["name"] == "filePathA"
    assert response2.json()[2]["sort_order"] == 3
    assert response2.json()[3]["tag"]["name"] == "filePathD"
    assert response2.json()[3]["sort_order"] == 4

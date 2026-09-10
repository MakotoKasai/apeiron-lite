from backend.photos.service import add_tag_to_photo
from .helpers.photo import create_test_photo, add_tag_to_test_photo
from .helpers.tag import create_tag_data


def test_get_photo(client):
    photo_id = create_test_photo("pathA")
    response = client.get(f"/photos/{photo_id}")
    assert response.status_code == 200
    assert response.json()["id"] == photo_id
    assert response.json()["file_path"] == "pathA"

def test_get_photo_with_wrong_id(client):
    photo_id = create_test_photo("pathA")
    response = client.get(f"/photos/999999")
    assert response.status_code == 404

def test_create_photo(client):
    response = client.post("/photos/",
                           json={"file_path": "pathA"})
    assert response.status_code == 201

    response = client.post(
        "/photos",
        json={
            "file_path": "",
        }
    )
    assert response.status_code == 422

    response = client.post(
        "/photos",
        json={
            "file_path": "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345",
        }
    )
    assert response.status_code == 201

    response = client.post(
        "/photos",
        json={
            "file_path": "012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234",
        }
    )
    assert response.status_code == 201

def test_create_photo_with_blank_filepath(client):
    response = client.post("/photos/",
                           json={"file_path": ""})
    assert response.status_code == 422

def test_update_photo(client):
    photo_id = create_test_photo("pathA")
    response = client.put(f"/photos/{photo_id}",
                          json={"file_path": "pathB"})
    assert response.status_code == 200
    assert response.json()["file_path"] == "pathB"

def test_update_photo_with_blank_filepath(client):
    photo_id = create_test_photo("pathA")
    response = client.put(f"/photos/{photo_id}",
                          json={"file_path": ""})
    assert response.status_code == 422

def test_delete_photo(client):
    photo_id = create_test_photo("pathA")
    response = client.delete(f"/photos/{photo_id}")
    assert response.status_code == 204

def test_delete_photo_with_unknown_photo_id(client):
    photo_id = create_test_photo("pathA")
    response = client.delete(f"/photos/999999")
    assert response.status_code == 404


def test_get_tags_from_photo(client):
    photo_id = create_test_photo("pathA")
    tag_id1 = create_tag_data("tagA")
    add_tag_to_test_photo(photo_id, tag_id1)

    response = client.get(f"/photos/{photo_id}/tags")
    print(response.json())
    assert response.status_code == 200
    assert response.json()[0]["tag"]["id"] == tag_id1
    assert response.json()[0]["sort_order"] == 1

    tag_id2 = create_tag_data("tagB")
    add_tag_to_test_photo(photo_id, tag_id2)

    response = client.get(f"/photos/{photo_id}/tags")
    print(response.json())
    assert response.status_code == 200
    assert response.json()[1]["tag"]["id"] == tag_id2
    assert response.json()[1]["sort_order"] == 2

def test_create_photo_tag(client):
    photo_id = create_test_photo("pathA")
    tag_id = create_tag_data("tag_1")

    response = client.post(f"/photos/{photo_id}/tags/{tag_id}")
    print(response.json())
    assert response.status_code == 201

    response = client.get(f"/photos/{photo_id}/tags/{tag_id}" )
    print(response.json())
    assert response.status_code == 200

    response = client.post(f"/photos/{photo_id}/tags/{tag_id}")
    print(response.json())
    assert response.status_code == 409

def test_shift_down_tag_within_photo(client):
    photo_id = create_test_photo("pathA")
    tag_id1 = create_tag_data("tag_1")
    tag_id2 = create_tag_data("tag_2")
    tag_id3 = create_tag_data("tag_3")
    tag_id4 = create_tag_data("tag_4")

    add_tag_to_test_photo(photo_id, tag_id1)
    add_tag_to_test_photo(photo_id, tag_id2)
    add_tag_to_test_photo(photo_id, tag_id3)
    add_tag_to_test_photo(photo_id, tag_id4)

    response = client.get(f"/photos/{photo_id}/tags")
    print(response.json())
    assert response.status_code == 200
    assert response.json()[0]["tag"]["id"] == tag_id1
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["tag"]["id"] == tag_id2
    assert response.json()[1]["sort_order"] == 2
    assert response.json()[2]["tag"]["id"] == tag_id3
    assert response.json()[2]["sort_order"] == 3
    assert response.json()[3]["tag"]["id"] == tag_id4
    assert response.json()[3]["sort_order"] == 4

    response = client.put(f"/photos/{photo_id}/tags/{tag_id4}",
                          json={"new_order": 2}
                          )
    print(response.json())
    assert response.status_code == 201

    response = client.get(f"/photos/{photo_id}/tags")
    print(response.json())
    assert response.status_code == 200
    assert response.json()[0]["tag"]["id"] == tag_id1
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["tag"]["id"] == tag_id4
    assert response.json()[1]["sort_order"] == 2
    assert response.json()[2]["tag"]["id"] == tag_id2
    assert response.json()[2]["sort_order"] == 3
    assert response.json()[3]["tag"]["id"] == tag_id3
    assert response.json()[3]["sort_order"] == 4


def test_shift_up_tag_within_photo(client):
    photo_id = create_test_photo("pathA")
    tag_id1 = create_tag_data("tag_1")
    tag_id2 = create_tag_data("tag_2")
    tag_id3 = create_tag_data("tag_3")
    tag_id4 = create_tag_data("tag_4")

    add_tag_to_test_photo(photo_id, tag_id1)
    add_tag_to_test_photo(photo_id, tag_id2)
    add_tag_to_test_photo(photo_id, tag_id3)
    add_tag_to_test_photo(photo_id, tag_id4)

    response = client.get(f"/photos/{photo_id}/tags")
    print(response.json())
    assert response.status_code == 200
    assert response.json()[0]["tag"]["id"] == tag_id1
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["tag"]["id"] == tag_id2
    assert response.json()[1]["sort_order"] == 2
    assert response.json()[2]["tag"]["id"] == tag_id3
    assert response.json()[2]["sort_order"] == 3
    assert response.json()[3]["tag"]["id"] == tag_id4
    assert response.json()[3]["sort_order"] == 4

    response = client.put(f"/photos/{photo_id}/tags/{tag_id1}",
                          json={"new_order": 4}
                          )
    print(response.json())
    assert response.status_code == 201

    response = client.get(f"/photos/{photo_id}/tags")
    print(response.json())
    assert response.status_code == 200
    assert response.json()[0]["tag"]["id"] == tag_id2
    assert response.json()[0]["sort_order"] == 1
    assert response.json()[1]["tag"]["id"] == tag_id3
    assert response.json()[1]["sort_order"] == 2
    assert response.json()[2]["tag"]["id"] == tag_id4
    assert response.json()[2]["sort_order"] == 3
    assert response.json()[3]["tag"]["id"] == tag_id1
    assert response.json()[3]["sort_order"] == 4


def test_remove_photo_tag(client):
    photo_id = create_test_photo("pathA")
    tag_id = create_tag_data("tag_1")

    add_tag_to_test_photo(photo_id, tag_id)

    response = client.get(f"/photos/{photo_id}/tags")
    print(response.json())
    assert response.status_code == 200

    response = client.delete(f"/photos/{photo_id}/tags/{tag_id}")
    assert response.status_code == 404

    response = client.get(f"/photos/{photo_id}/tags")
    print(response.json())
    assert response.status_code == 200
    assert len(response.json()) == 0
from .helpers.tag import create_tag_data


def test_create_tag(client):
    response = client.post(
        "/tags",
        json={
            "name": "test-tag"
        }
    )
    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["name"] == "test-tag"

    response = client.post(
        "/tags",
        json={
            "name": "",
        }
    )
    assert response.status_code == 422

    response = client.post(
        "/tags",
        json={
            "name": "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345",
        }
    )
    assert response.status_code == 201

    response = client.post(
        "/tags",
        json={
            "name": "012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234",
        }
    )
    assert response.status_code == 201

def test_create_duplicate_tag(client):
    create_tag_data("test-tag")

    response = client.post(
        "/tags",
        json={
            "name": "test-tag"
        }
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Tag already exists"

def test_update_tag(client):
    tag_id = create_tag_data("test-tag")

    response = client.put(
        "/tags/{}".format(tag_id),
        json={
            "name": "test-tag2"
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == 1
    assert response.json()["name"] == "test-tag2"

    response2 = client.put(
        "/tags/999999",
        json={
            "name": "test-tag3"
        }
    )

    assert response2.status_code == 404
    assert response2.json() == {"detail": "Tag not found"}

def test_update_duplicate_tag(client):
    tag_id1 = create_tag_data("test-tag1")
    create_tag_data("test-tag2")

    response = client.put(
        "/tags/{}".format(tag_id1),
        json={
            "name": "test-tag2"
        }
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Tag already exists"

def test_get_tag(client):
    tag_id = create_tag_data("test-tag")

    response = client.get("/tags/{}".format(tag_id))
    assert response.status_code == 200
    assert response.json()["id"] == tag_id
    assert response.json()["name"] == "test-tag"

def test_get_tag_with_unknown_id(client):
    response = client.get("/tags/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Tag not found"}

def test_get_tag_by_name(client):
    tag_id = create_tag_data("test-tag")

    response = client.get("/tags/by_name/test-tag")
    assert response.status_code == 200
    assert response.json()["id"] == tag_id
    assert response.json()["name"] == "test-tag"

    response2 = client.get("/tags/by_name/test")
    assert response2.status_code == 404
    assert response2.json() == {"detail": "Tag not found"}

def test_delete_tag(client):
    tag_id = create_tag_data("test-tag")

    response = client.delete("/tags/{}".format(tag_id))
    assert response.status_code == 204

def test_delete_tag_with_unknown_id(client):
    response = client.delete("/tags/999999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Tag not found"}



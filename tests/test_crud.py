import pytest
from fastapi import status

def test_create_item(client):
    response = client.post(
        "/items/",
        json={"name": "Test Item", "description": "Test Description", "price": 10.5}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["description"] == "Test Description"
    assert data["price"] == 10.5
    assert "id" in data

def test_read_items(client):
    # Create test items
    client.post("/items/", json={"name": "Item 1", "description": "Desc 1", "price": 10.0})
    client.post("/items/", json={"name": "Item 2", "description": "Desc 2", "price": 20.0})

    response = client.get("/items/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Item 1"
    assert data[1]["name"] == "Item 2"

def test_read_item(client):
    # Create a test item
    create_response = client.post(
        "/items/",
        json={"name": "Test Item", "description": "Test Description", "price": 10.5}
    )
    item_id = create_response.json()["id"]

    # Read the item
    response = client.get(f"/items/{item_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["id"] == item_id

def test_read_non_existent_item(client):
    response = client.get("/items/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_item(client):
    # Create a test item
    create_response = client.post(
        "/items/",
        json={"name": "Original Name", "description": "Original Desc", "price": 10.0}
    )
    item_id = create_response.json()["id"]

    # Update the item
    update_response = client.put(
        f"/items/{item_id}",
        json={"name": "Updated Name", "description": "Updated Desc", "price": 20.0}
    )
    assert update_response.status_code == status.HTTP_200_OK
    data = update_response.json()
    assert data["name"] == "Updated Name"
    assert data["description"] == "Updated Desc"
    assert data["price"] == 20.0

def test_delete_item(client):
    # Create a test item
    create_response = client.post(
        "/items/",
        json={"name": "Test Item", "description": "Test Description", "price": 10.5}
    )
    item_id = create_response.json()["id"]

    # Delete the item
    delete_response = client.delete(f"/items/{item_id}")
    assert delete_response.status_code == status.HTTP_200_OK

    # Verify item is deleted
    get_response = client.get(f"/items/{item_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

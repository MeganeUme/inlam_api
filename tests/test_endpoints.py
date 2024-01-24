import sys
import os

# Assuming this script is in the tests directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import json
import pytest
from app.app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_get_books_endpoint_success(client):
    # Test the endpoint for retrieving all books
    response = client.get("/books")
    assert response.status_code == 200


def test_add_books_endpoint_no_title_success(client):
    # Test the endpoint for adding books with insuficcient parameters
    data = {
        "author": "Test Author",
        "summary": "Test Summary",
        "genre": "Test Genre"
    }
    response = client.post("/books", json=data)
    assert response.status_code == 400


def test_get_book_id_endpoint_success(client):
    # Test the endpoint for retrieving a specific book by ID
    response = client.get("/books/4")
    assert response.status_code == 200


def test_update_book_endpoint_nonexistent_id_success(client):
    # Test the endpoint for updating a specific book by ID
    data = {
        "title": "Updated Title",
        "author": "Updated Author",
        "summary": "Updated Summary",
        "genre": "Updated Genre"
    }
    response = client.put("/books/33", json=data)
    assert response.status_code == 404


def test_delete_book_endpoint_nonexistent_id_success(client):
    # Test the endpoint for deleting a specific book by ID
    response = client.delete("/books/99999")
    assert response.status_code == 500


def test_get_all_reviews_endpoint_success(client):
    # Test the endpoint for retrieving all reviews
    response = client.get("/reviews")
    assert response.status_code == 200


def test_get_book_reviews_endpoint_success(client):
    # Test the endpoint for retrieving reviews for a specific book by ID
    response = client.get("/reviews/1")
    assert response.status_code == 200


def test_get_top_reviews_endpoint_success(client):
    # Test the endpoint for retrieving the top reviews
    response = client.get("/books/top")
    assert response.status_code == 200

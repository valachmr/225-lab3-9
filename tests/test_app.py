import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    os.environ['DATABASE'] = ':memory:'
    with app.app_context():
        init_db()                    # <-- creates the table before each test
    with app.test_client() as client:
        yield client

def test_index_get(client):
    response = client.get('/')
    assert response.status_code == 200

def test_index_post_missing_fields(client):
    response = client.post('/', data={'name': ''})
    assert response.status_code in [200, 302]

def test_index_post_valid(client):
    response = client.post('/', data={'name': 'John', 'phone': '5551234567'})
    assert response.status_code in [200, 302]
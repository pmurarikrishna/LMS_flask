import pytest
from app import create_app, db
from app.models import Book

@pytest.fixture
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

@pytest.fixture
def init_database():
    db.session.add(Book(title='Test Book', author='Test Author', isbn='1234567890123', published_year=2020, category='Fiction', quantity=10))
    db.session.commit()

    yield db

    db.session.remove()
    db.drop_all()

def test_add_book(test_client):
    response = test_client.post('/api/books', json={
        'title': 'Book1',
        'author': 'Author1',
        'isbn': '1234567890124',
        'published_year': 2025,
        'category': 'Non-Fiction',
        'quantity': 5
    })
    assert response.status_code == 201
    assert response.json['message'] == 'Book added successfully!'

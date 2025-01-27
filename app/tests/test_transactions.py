import pytest
from app import create_app, db
from app.models import Book, User
from datetime import date

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def test_client(app):
    return app.test_client()

@pytest.fixture
def init_database(app):
    with app.app_context():
        # Add test data
        book = Book(
            title='Book1',
            author='Author1',
            isbn='1234567890124',
            published_year=2025,
            category='Non-Fiction',
            quantity=5
        )
        user = User(
            name='User1',
            email='user1@test.com',
            password='Qwerty@123',
            role='user'
        )
        db.session.add(book)
        db.session.add(user)
        db.session.commit()
        yield db

def test_checkout_book(test_client, init_database):
    response = test_client.post('/api/transactions/checkout', json={
        'user_id': 1,
        'book_id': 1,
        'checkout_date': date.today().isoformat(),  # Use ISO format for JSON
        'due_date': date.today().isoformat()        # Use ISO format for JSON
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Book checked out successfully!'

def test_return_book(test_client, init_database):
    # Checkout the book first
    test_client.post('/api/transactions/checkout', json={
        'user_id': 1,
        'book_id': 1,
        'checkout_date': date.today().isoformat(),
        'due_date': date.today().isoformat()
    })

    # Return the book
    response = test_client.post('/api/transactions/return', json={
        'user_id': 1,
        'book_id': 1,
        'return_date': date.today().isoformat()
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Book returned successfully!'

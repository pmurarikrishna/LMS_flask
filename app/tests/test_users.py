import pytest
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

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
    db.session.add(User(name='Admin User', email='admin@test.com', password=generate_password_hash('password'), role='admin'))
    db.session.commit()

    yield db

    db.session.remove()
    db.drop_all()

def test_create_user(test_client):
    response = test_client.post('/api/users', json={
        'name': 'User1',
        'email': 'user1@test.com',
        'password': 'Qwerty@123',
        'role': 'user'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User created successfully!'

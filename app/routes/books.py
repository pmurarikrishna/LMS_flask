from flask import Blueprint, request, jsonify
from app.models import Book
from app import db

books_bp = Blueprint('books', __name__)

@books_bp.route('/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = Book(**data)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully!'}), 201

@books_bp.route('/books', methods=['GET'])
def list_books():
    books = Book.query.all()
    return jsonify([book.as_dict() for book in books])

@books_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    data = request.json
    book = Book.query.get_or_404(book_id)
    for key, value in data.items():
        setattr(book, key, value)
    db.session.commit()
    return jsonify({'message': 'Book updated successfully!'}), 200

@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted successfully!'}), 200

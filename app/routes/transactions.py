from flask import Blueprint, request, jsonify
from app.models import Transaction, Book, User
from app import db
from datetime import date

transactions_bp = Blueprint('transactions', __name__)

@transactions_bp.route('/transactions/checkout', methods=['POST'])
def checkout_book():
    try:
        data = request.json
        required_fields = ['user_id', 'book_id', 'checkout_date', 'due_date']

        # Validate required fields
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Parse dates
        checkout_date = date.fromisoformat(data['checkout_date'])
        due_date = date.fromisoformat(data['due_date'])

        # Fetch book
        book = Book.query.get(data['book_id'])
        if not book:
            return jsonify({'error': 'Book not found!'}), 404

        if book.quantity > 0:
            # Update book quantity and create transaction
            book.quantity -= 1
            transaction = Transaction(
                user_id=data['user_id'],
                book_id=data['book_id'],
                checkout_date=checkout_date,
                due_date=due_date
            )
            db.session.add(transaction)
            db.session.commit()
            return jsonify({
                'message': 'Book checked out successfully!',
                'transaction': {
                    'user_id': transaction.user_id,
                    'book_id': transaction.book_id,
                    'checkout_date': transaction.checkout_date.isoformat(),
                    'due_date': transaction.due_date.isoformat()
                },
                'remaining_quantity': book.quantity
            }), 200

        return jsonify({'error': 'Book not available!'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

@transactions_bp.route('/transactions/return', methods=['POST'])
def return_book():
    try:
        data = request.json
        required_fields = ['user_id', 'book_id']

        # Validate required fields
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Find the active transaction
        transaction = Transaction.query.filter_by(
            user_id=data['user_id'],
            book_id=data['book_id'],
            return_date=None
        ).first()

        if transaction:
            # Update transaction and book
            transaction.return_date = date.today()
            book = Book.query.get(data['book_id'])
            if not book:
                return jsonify({'error': 'Book not found!'}), 404
            book.quantity += 1
            db.session.commit()
            return jsonify({
                'message': 'Book returned successfully!',
                'transaction': {
                    'user_id': transaction.user_id,
                    'book_id': transaction.book_id,
                    'return_date': transaction.return_date.isoformat()
                },
                'updated_quantity': book.quantity
            }), 200

        return jsonify({'error': 'No active transaction found!'}), 400
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500
    
@transactions_bp.route('/transactions', methods=['GET'])
def get_all_transactions():
    try:
        transactions = Transaction.query.all()
        transaction_list = [
            {
                'id': transaction.id,
                'user_id': transaction.user_id,
                'book_id': transaction.book_id,
                'checkout_date': transaction.checkout_date.isoformat(),
                'due_date': transaction.due_date.isoformat(),
                'return_date': transaction.return_date.isoformat() if transaction.return_date else None
            }
            for transaction in transactions
        ]
        return jsonify({'transactions': transaction_list}), 200
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

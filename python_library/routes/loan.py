import logging

from flask import Blueprint, jsonify

from .. import db
from ..models import Book, BookLoan, PhysicalBook, Client, Branch, ClientJP, ClientFP

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('loans', __name__, url_prefix='/api/loans')

@bp.route('/<int:client_id>/<int:id_physical_book>/<date:due_date>', methods=['POST'])
def create_loan(client_id, id_physical_book, due_date):
    """
    Endpoint for creating a loan
    :param client_id: <int> Client ID
    :param id_physical_book: <int> Physical Book ID
    :param due_date: <date> Due Date
    """
    try:
        new_loan = BookLoan(
            idPhysicalBook=id_physical_book,
            idClient=client_id,
            DueDate=due_date
        )
        db.session.add(new_loan)

        db.session.flush()

        physical_book = db.session.query(
            PhysicalBook
        ).filter(
            PhysicalBook.idPhysicalBook == id_physical_book
        ).first()

        physical_book.Status = 'BORROWED'

        db.session.commit()
        return jsonify({"message": "Loan created successfully."}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error in creating loan: {e}")
        return jsonify({"message": f"Error in creating loan: {e}"}), 500

@bp.route('/<int:loan_id>/return', methods=['PUT'])
def return_loan(loan_id):
    """
    Endpoint to return a loan
    :param loan_id: <int> loan id
    """
    try:
        result = get_loan_by_id(loan_id)

        if not result:
            return jsonify({'message': 'Loan not found'}), 404

        loan, physical_book = result

        loan.Status = 'RETURNED'
        physical_book.Status = 'AVAILABLE'
        db.session.commit()
        return jsonify({'message': 'Loan returned successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to return loan: {e}")
        return jsonify({"message": f"Failed to return loan: {e}"}), 500

@bp.route('/<int:loan_id>/lost', methods=['PUT'])
def lost_loan(loan_id):
    """
    Endpoint to set and unset a loan as LOST
    :param loan_id: <int> loan id
    """
    try:
        result = get_loan_by_id(loan_id)
        if not result:
            return jsonify({'message': 'Loan not found'}), 404

        loan = result[0]
        loan.Status = 'LOST'
        db.session.commit()
        return jsonify({'message': 'Loan set successfully'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to set/unset loan: {e}")
        return jsonify({'message': f"Failed to set/unset loan: {e}"}), 500

def get_loan_by_id(loan_id):
    """
    Get Loan by id
    :param loan_id: <int> loan id
    """
    return db.session.query(
        BookLoan,
        PhysicalBook,
        Book,
        Branch,
        Client,
        ClientFP,
        ClientJP
    ).join(
        PhysicalBook,
        Book,
        Branch,
        Client
    ).outerjoin(
        ClientJP,
        ClientFP
    ).filter(
        BookLoan.id == loan_id
    ).first()
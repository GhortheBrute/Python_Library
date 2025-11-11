from datetime import datetime, timedelta
import logging

from flask import Blueprint, jsonify, request

from .. import db
from ..models import Book, BookLoan, PhysicalBook, Client, Branch, ClientJP, ClientFP

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('loans', __name__, url_prefix='/api/loans')

@bp.route('/', methods=['POST'])
def create_loan():
    """
    Endpoint for creating a loan
    """
    data = request.get_json()
    if not data:
        return jsonify({'message': 'No data provided'}), 400


    id_physical_book = data.get('idPhysicalBook')
    id_client = data.get('idClient')
    days_solicited = data.get('BorrowTimeSolicited', 14) # Se não for informado, o padrão é 14

    if not id_physical_book or not id_client:
        return jsonify({"error": "idClient and idPhysicalBook are required."}), 400

    try:
        # Verifica se o livro está disponível

        physical_book = db.session.get(PhysicalBook, id_physical_book)
        if not physical_book:
            return jsonify({"error": "Book not found"}), 404
        if physical_book.Status != 'AVAILABLE':
            return jsonify({"error":"Book not available to loan."}), 409

        # Calcula data de due_date
        due_date = datetime.now().date() + timedelta(days=days_solicited)

        new_loan = BookLoan(
            idPhysicalBook=id_physical_book,
            idClient=id_client,
            DueDate=due_date,
            BorrowTimeSolicited=days_solicited
        )
        db.session.add(new_loan)

        physical_book.Status = 'BORROWED'
        db.session.add(physical_book)

        db.session.commit()
        return jsonify({"message": "Loan created successfully.", "DueDate": due_date}), 201
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
        loan.ReturnDate = db.func.now()
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

        loan, physical_book = result
        loan.Status = 'LOST'
        physical_book.Status = 'LOST'
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
        BookLoan.idBookLoan == loan_id
    ).first()
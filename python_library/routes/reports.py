import logging

from flask import Blueprint, jsonify
from datetime import date

from .. import db
from ..models import BookLoan, Client, ClientFP, ClientJP, PhysicalBook, Book

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@bp.route('/overdue', methods=['GET'])
def get_overdue_loans():
    """
    Return overdue loans due dates
    ---
    tags:
        - Reports
    responses:
        200:
            description: Report successfully retrieved
        500:
            description: Internal server error
    """
    try:
        today = date.today()

        # Consulta:
        # 1. Status deve ser 'ACTIVE'
        # 2. DueDate deve ser menor que hoje
        query = db.session.query(
            BookLoan,
            Client,
            ClientFP,
            ClientJP,
            PhysicalBook,
            Book
        ).join(
            Client, BookLoan.idClient == Client.idClient
        ).outerjoin(
            ClientFP, Client.idClient == ClientFP.idClient
        ).outerjoin(
            ClientJP, Client.idClient == ClientJP.idClient
        ).join(
            PhysicalBook, BookLoan.idPhysicalBook == PhysicalBook.idPhysicalBook
        ).join(
            Book, PhysicalBook.ISBN == Book.ISBN
        ).filter(
            BookLoan.Status == 'ACTIVE',
            BookLoan.DueDate < today
        )

        results = query.all()

        output = []
        for loan, client, client_fp, client_jp, phys_book, book in results:

            # Descobrir o nome do cliente
            client_name = "Desconhecido"
            if client.Type == 'PF' and client_fp:
                client_name = f"{client_fp.FName} {client_fp.LName}"
            elif client.Type == 'JP' and client_jp:
                client_name = client_jp.FantasyName or client_jp.Name

            # Calcular os dias de atraso
            days_overdue = (today - loan.DueDate).days

            loan_data = {
                'idBookLoan': loan.idBookLoan,
                'ClientName': client_name,
                'BookTitle': book.Title,
                'DueDate': loan.DueDate.isoformat(),
                'DaysOverdue': days_overdue
            }
            output.append(loan_data)

        return jsonify({'overdue_loans': output, 'count': len(output)}), 200
    except Exception as e:
        logging.error(f"Failed to get overdue report: {e}")
        return jsonify({'error': f"Failed to get overdue report: {e}"}), 500
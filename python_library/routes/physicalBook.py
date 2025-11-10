import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Book, Branch, PhysicalBook, Author, Publisher, Language

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('physicalBooks', __name__, url_prefix='/api/physicalBooks')

@bp.route('/', methods=('POST'))
def create_book():
    """
    Endpoint for creating a book
    """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validação Simples
    required_fields = ['ISBN', 'idBranch']

    for field in required_fields:
        if field not in data:
            return jsonify({'message': 'Missing required field'}), 400

    try:
        # Criar um livro físico
        new_physical_book = PhysicalBook(
            ISBN=data['ISBN'],
            idBranch=data['idBranch']
        )
        db.session.add(new_physical_book)

        db.session.commit()

        return jsonify({'message': 'Book successfully created'}), 201
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to create book {e}')
        return jsonify({'message': f'Failed to create book: {e}'}), 400

@bp.route('/', methods=['GET'])
def get_physical_books():
    """
    Endpoint for getting all physical books
    Accepts a 'status' query param:
    - ?status=active (default)
    - ?status=inactive
    - ?status=all
    """
    try:
        status_filter = request.args.get('status', 'active')

        query = db.session.query(
            PhysicalBook,
            Book,
            Branch,
            Author,
            Publisher,
            Language
        ).join(
            Book,
            Branch,
            Author,
            Publisher,
            Language
        )

        if status_filter == 'active':
            query = query.filter(Book.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(Book.is_active == False)
        elif status_filter == 'all':
            pass
        else:
            return jsonify({"error": "Invalid 'status' parameter. Use 'active', 'inactive', or 'all'."}), 400

        results = query.all()

        output = []
        for physical_book, book, branch, author, publisher, language in results:
            physical_book_data = {
                'idPhysicalBook': physical_book.idPhysicalBook,
                'ISBN': physical_book.ISBN,
                'Title': book.Title,
                'Author': f"{author.LName}, {author.FName} {author.MName}",
                'Publisher': publisher.Name,
                'Edition': book.Edition,
                'Language': language.Name,
                'BranchName': branch.BranchName
            }
            output.append(physical_book_data)

        return jsonify({'physical_books': output}), 200
    except Exception as e:
        logging.error(f'Failed to get physical books: {e}')
        return jsonify({'message': f'Failed to get physical books: {e}'}), 400


@bp.route('/<int:book_id>', methods=['GET'])
def get_physical_book(book_id):
    """
    Endpoint for getting a physical book by ID
    """
    try:
        result = get_physical_book_by_id(book_id)
        if not result:
            return jsonify({"error": "Physical Book not found"}), 404

        output = []
        physical_book, book, branch, author, publisher, language = result
        physical_book_data = {
            'idPhysicalBook': physical_book.idPhysicalBook,
            'ISBN': physical_book.ISBN,
            'Title': book.Title,
            'Author': f"{author.LName}, {author.FName} {author.MName}",
            'Publisher': publisher.Name,
            'Edition': book.Edition,
            'Language': language.Name,
            'BranchName': branch.BranchName
        }
        output.append(physical_book_data)

        return jsonify({'physical_book': output}), 200
    except Exception as e:
        logging.error(f'Failed to get physical book: {e}')
        return jsonify({'message': f'Failed to get physical book: {e}'}), 400


@bp.route('/<int:book_id>', methods=['PUT', 'PATCH'])
def update_physical_book(book_id):
    """
    Endpoint for updating a physical book
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = get_physical_book_by_id(book_id)

        if not result:
            return jsonify({"error": "Physical Book not found"}), 404

        physical_book = result[0]

        # Atualizar o livro
        physical_book.idBranch = data["idBranch", physical_book.idBranch]

        db.session.commit()
        return jsonify({'message': 'Physical Book branch successfully updated'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to update physical book: {e}')
        return jsonify({'message': f'Failed to update physical book: {e}'}), 400

@bp.route('/<int:book_id>', methods=['DELETE'])
def delete_physical_book(book_id):
    """
    Endpoint for deleting a physical book
    """
    try:
        result = get_physical_book_by_id(book_id)
        if not result:
            return jsonify({"error": "Physical Book not found"}), 404

        physical_book = result[0]

        physical_book.is_active = False
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to delete physical book: {e}')
        return jsonify({'message': f'Failed to delete physical book: {e}'}), 400

@bp.route('/<int:book_id>', methods=['PUT', 'PATCH'])
def set_in_repair_physical_book(book_id):
    """
    Endpoint for setting and unsetting a Lost Physical Book
    """
    try:
        result = get_physical_book_by_id(book_id)

        if not result:
            return jsonify({"error": "Physical Book not found"}), 404

        physical_book = result[0]
        if physical_book.Status != "IN REPAIR":
            physical_book.Status = "IN REPAIR"
        else:
            physical_book.Status = "AVAILABLE"

        db.session.commit()
        return jsonify({'message': 'Physical Book Status successfully updated'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f'Failed to set physical book: {e}')
        return jsonify({'message': f'Failed to set physical book: {e}'}), 400

def get_physical_book_by_id(book_id):
    return db.session.query(
        PhysicalBook,
        Book,
        Branch,
        Author,
        Publisher,
        Language
    ).join(
        Book,
        Branch,
        Author,
        Publisher,
        Language
    ).filter(
        PhysicalBook.idPhysicalBook == book_id,
        ).first()  # .first() pega apenas um
import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Book, Publisher, Author, Collection

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('books', __name__, url_prefix='/api/books')

@bp.route('/', methods=['POST'])
def create_book():
    """
    Endpoint for creating a book
    Awaits a JSON with book details and address
    """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validação simples
    required_fields = ['ISBN', 'Title', 'idAuthor', 'idPublisher', 'Language']

    # Validação de dados
    for field in required_fields:
        if field not in data:
            return jsonify({"Error": f"Required field {field} is missing"}), 400

    # Transação de Banco de Dados
    try:
        # Criar o Book pai
        new_book = Book(
            ISBN=data.get('ISBN'),
            Title=data.get('Title'),
            idAuthor=data.get('idAuthor'),
            idPublisher=data.get('idPublisher'),
            Edition=data.get('Edition'),
            Language=data.get('Language'),
            Collection=data.get('Collection'),
            AgeRange=data.get('AgeRange')
        )
        db.session.add(new_book)

        # 4. Se tudo certo, comitar a transação
        db.session.commit()

        return jsonify({'message': 'Book successfully created'}), 201

    except Exception as e:
        # 5. Se algo deu errado, reverter tudo
        db.session.rollback()
        logging.error(f"Failed to create book: {e}")
        return jsonify({"error": f"Failed to create book"}), 500

@bp.route('/', methods=['GET'])
def get_books():
    """
    endpoint for getting all books
    Accepts a 'status' query param:
    - ?status=active (default)
    - ?status=inactive
    - ?status=all
    """
    try:
        # Pegamos o parâmetro da url
        # Se nada for passado, o valor padrão é 'active'
        status_filter = request.args.get('status', 'active')

        # 1. Fazemos a consulta unindo as 4 tabelas de Clientes
        # (Client, ClientFP, ClientJP, Address)
        query = db.session.query(
            Book,
            Author,
            Publisher,
            Collection
        ).join(
            Author,
            Publisher
        ).outerjoin(
            Collection
        )

        # Adicionamos o filtro de status
        if status_filter == 'active':
            query = query.filter(Book.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(Book.is_active == False)
        elif status_filter == 'all':
            pass
        else:
            return jsonify({"error": "Invalid 'status' parameter. Use 'active', 'inactive', or 'all'."}), 400

        results = query.all()

        # 2. Formatamos os resultados para JSON
        output = []
        for book, author, publisher, collection in results:
            book_data = {
                'ISBN': book.ISBN,
                'Title': book.Title,
                'Author': f"{author.LName}, {author.FName} {author.MName}",
                'Publisher': publisher.Name,
                'Edition': book.Edition,
                'Language': book.Language,
                'Collection': collection.Name,
                'AgeRange': book.AgeRange,
                'Review': book.Review
            }
            output.append(book_data)

        return jsonify({'books': output}), 200

    except Exception as e:
        logging.error(f"Failed to get books: {e}")
        return jsonify({"error": f"Failed to get books"}), 500

@bp.route('/<string:isbn>', methods=['GET'])
def get_book(isbn):
    """
    endpoint for getting a book
    """
    try:
        # 1. Fazemos a mesma consulta, mas filtramos pelo ID
        result = get_book_by_isbn(isbn)

        # 2. Verificamos se o cliente foi encontrado
        if not result:
            return jsonify({"error": "Book not found"}), 404

        # 3. Desempacotamos os resultados
        book, author, publisher, collection  = result

        # 4. Formatamos o JSON de resposta
        book_data = {
            'ISBN': book.ISBN,
            'Title': book.Title,
            'Author': f"{author.LName}, {author.FName} {author.MName}",
            'Publisher': publisher.Name,
            'Edition': book.Edition,
            'Language': book.Language,
            'Collection': collection.Name,
            'AgeRange': book.AgeRange,
            'Review': book.Review
        }
        return jsonify(book_data), 200

    except Exception as e:
        logging.error(f"Failed to get book: {e}")
        return jsonify({"error": f"Failed to get book: {e}"}), 500

@bp.route('/<string:isbn>', methods=['PUT', 'PATCH'])
def update_book(isbn):
    """
    endpoint for updating a book
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = get_book_by_isbn(isbn)

        if not result:
            return jsonify({"error": "Book not found"}), 404

        book, author, publisher = result

        # Atualizar o livro
        book.Title = data.get('Title', book.Title)
        book.Edition = data.get('Edition', book.Edition)
        book.Language = data.get('Language', book.Language)
        book.Collection = data.get('Collection', book.Collection)
        book.AgeRange = data.get('AgeRange', book.AgeRange)
        book.idAuthor = data.get('idAuthor', book.idAuthor)
        book.idPublisher = data.get('idPublisher', book.idPublisher)

        db.session.commit()
        return jsonify({'message': 'Book successfully updated'}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to update book: {e}")
        return jsonify({"error": f"Failed to update book: {e}"}), 500

@bp.route('/<int:id>', methods=['DELETE'])
def delete_book(isbn):
    """
    endpoint for deleting a book
    """
    try:
        result = get_book_by_isbn(isbn)
        if not result:
            return jsonify({"error": "Book not found"}), 404

        book, author, publisher = result
        book.is_active = False
        db.session.commit()
        return '', 204
    except Exception as e:
        logging.error(f"Failed to delete book: {e}")
        return jsonify({"error": f"Failed to delete book: {e}"}), 500

def get_book_by_isbn(isbn):
    return db.session.query(
        Book,
        Author,
        Publisher,
        Collection
    ).join(
        Author,
        Publisher
    ).outerjoin(
        Collection
    ).filter(
        Book.ISBN == isbn,
        ).first()  # .first() pega apenas um

def get_book_by_title(title):
    pass

def get_book_by_author(author):
    pass

def get_book_by_publisher(publisher):
    pass
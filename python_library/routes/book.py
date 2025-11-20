import logging

from flask import Blueprint, request, jsonify
from sqlalchemy import or_

from .. import db
from ..models import Book, Publisher, Author, Collection, Language

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('books', __name__, url_prefix='/api/books')

@bp.route('/', methods=['POST'])
def create_book():
    """
    Endpoint for creating a book
    Awaits a JSON with book details and address
    ---
    tags:
        - Books
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            required:
                - ISBN
                - Title
                - idAuthor
                - idPublisher
                - Language
            properties:
                ISBN:
                    type: string
                    example: 9788599296578
                    description: ISBN-13 of the book. Can contain '-'
                Title:
                    type: string
                    example: "Lord of the Rings: The Fellowship of the Ring"
                    description: Book title
                idAuthor:
                    type: integer
                    example: 1
                    description: Book author ID
                idPublisher:
                    type: integer
                    example: 2
                    description: Book publisher ID
                Edition:
                    type: string
                    example: Special Edition
                    description: (Optional) Book edition
                Language:
                    type: integer
                    example: 3
                    description: Book language ID
                Collection:
                    type: integer
                    example: 4
                    description: (Optional) Book collection ID
                AgeRange:
                    type: integer
                    example: 5
                    description: (Optional) Age range of the book, for grouping and recommendation
    responses:
        201:
            description: Book successfully created
        400:
            description: Validation error (missing data or wrong)
            examples:
                No Data:
                    message: "No data provided"
                Missing Field:
                    Error: "One or more required fields are missing."
        500:
            description: Internal server error
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
    ---
    tags:
      - Books
    parameters:
      - name: status
        in: query
        type: string
        default: active
        enum: ['active', 'inactive', 'all']
        description: Filter books by is_active (active, inactive or all)

        - name: title
        in: query
        type: string
        description: Filter by title (parcial search)

      - name: author
        in: query
        type: string
        description: Filter by Author's first or last name

      - name: publisher
        in: query
        type: string
        description: Filter by publisher name
    responses:
      200:
        description: Books list recovered successfully
        schema:
          type: object
          properties:
            authors:
              type: array
              items:
                type: object
                properties:
                  ISBN:
                    type: string
                    example: 1234567890123
                  Title:
                    type: string
                    example: "Lord of the Rings: The Fellowship of the Ring"
                  Author:
                    type: string
                    example: "J.R.R. Tolkien"
                  Publisher:
                    type: string
                    example: "Publisher A"
                  Edition:
                    type: string
                    example: "Special edition"
                  Language:
                    type: integer
                    example: 1
                  Collection:
                    type: string
                    example: "The Lord of the Rings"
                  AgeRange:
                    type: integer
                    example: 14
                  Review:
                    type: decimal
                    example: 4.8
      400:
        description: Invalid 'status' parameter
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid 'status' parameter."
      500:
        description: Internal server error
    """
    try:
        # Pegamos o parâmetro da url
        # Se nada for passado, o valor padrão é 'active'
        status_filter = request.args.get('status', 'active')
        title_filter = request.args.get('title')
        author_filter = request.args.get('author')
        publisher_filter = request.args.get('publisher')

        # 1. Fazemos a consulta unindo as 4 tabelas de Clientes
        # (Client, ClientFP, ClientJP, Address)
        query = db.session.query(
            Book,
            Author,
            Publisher,
            Collection,
            Language
        ).join(
            Author, Author.idAuthor == Book.idAuthor
        ).join(
            Publisher, Publisher.idPublisher == Book.idPublisher
        ).outerjoin(
            Collection, Collection.idCollection == Book.Collection
        ).join(
            Language, Language.idLanguage == Book.Language
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

        # Filtro de Título (ILIKE = Case Insensitive, % = Contém)
        if title_filter:
            query = query.filter(Book.Title.ilike(f"%{title_filter}%"))

        # Filtro de Editora
        if publisher_filter:
            query = query.filter(Publisher.Name.ilike(f"%{publisher_filter}%"))

        # Filtro de Autor (Nome ou Sobrenome)
        if author_filter:
            term = f"%{author_filter}%"
            query = query.filter(or_(
                Author.FName.ilike(f"%{author_filter}%"),
                Author.LName.ilike(f"%{author_filter}%")
            ))

        query = query.order_by(Book.Title)

        results = query.all()

        if not results:
            return jsonify({"error": "No books found."}), 400

        # 2. Formatamos os resultados para JSON
        output = []
        for book, author, publisher, collection, language in results:
            book_data = {
                'ISBN': book.ISBN,
                'Title': book.Title,
                'Author': f"{author.LName}, {author.FName} {author.MName or ''}".strip(),
                'Publisher': publisher.Name,
                'Edition': book.Edition,
                'Language': language.Name,
                'Collection': collection.Name if collection else None,
                'AgeRange': book.AgeRange,
                'Review': float(book.Review) if book.Review else None,
            }
            output.append(book_data)

        return jsonify({'books': output}), 200

    except Exception as e:
        logging.error(f"Failed to get books: {e}")
        return jsonify({"error": f"Failed to get books"}), 500

@bp.route('/<string:isbn>', methods=['GET'])
def get_book(isbn):
    """
    Endpoint for getting a book
    ---
    tags:
        - Books
    parameters:
        - name: isbn
          in: path
          type: string
          required: true
          description: Unique Book ISBN that needs to be found
    responses:
        200:
            description: Book successfully found
        404:
            description: Book not found
        500:
            description: Internal server error
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
    Endpoint for updating a book
    ---
    tags:
        - Books
    parameters:
        - name: isbn
          in: path
          type: string
          required: true
          description: Unique Book ISBN that needs to be found

        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
                Title:
                    type: string
                    example: "Lord of the Rings: The Fellowship of the Ring"
                    description: Book title
                idAuthor:
                    type: integer
                    example: 1
                    description: Book author ID
                idPublisher:
                    type: integer
                    example: 2
                    description: Book publisher ID
                Edition:
                    type: string
                    example: Special Edition
                    description: Book edition
                Language:
                    type: integer
                    example: 3
                    description: Book language ID
                Collection:
                    type: integer
                    example: 4
                    description: Book collection ID
                AgeRange:
                    type: integer
                    example: 5
                    description: Age range of the book, for grouping and recommendation
    responses:
        200:
            description: Book successfully updated
        400:
            description: No data provided
        404:
            description: Book not found
        500:
            description: Internal server error
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

@bp.route('/<string:isbn>', methods=['DELETE'])
def delete_book(isbn):
    """
    Endpoint for deleting a book
    ---
    tags:
        - Books
    parameters:
        - name: isbn
          in: path
          type: string
          required: true
          description: Unique Book ISBN that needs to be found
    responses:
        204:
            description: Book successfully deleted
        404:
            description: Book not found
        500:
            description: Internal server error
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
import logging

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from .. import db
from ..models import BookReview, Book, Client

bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')

@bp.route('/', methods=['POST'])
def create_review():
    """
    Cria uma avaliação para um livro e atualiza a nota média do livro.
    ---
    tags:
      - Reviews
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - idClient
            - ISBN
            - Rating
          properties:
            idClient:
              type: integer
              example: 1
            ISBN:
              type: string
              example: "9781234567890"
            Rating:
              type: integer
              description: Nota de 1 a 5
              example: 5
            Comment:
              type: string
              description: Comentário opcional
              example: "Livro excelente!"
    responses:
      201:
        description: Review criada com sucesso
      400:
        description: Dados inválidos (ex: nota fora de 1-5)
      404:
        description: Livro ou Cliente não encontrado
    """
    data = request.get_json()
    if not data:
        return jsonify({"message": "No data provided"}), 400

    isbn = data.get("ISBN")
    id_client = data.get("idClient")
    rating = data.get("Rating")
    comment = data.get("Comment")

    # Validação básica
    if not isbn or not id_client or rating is None:
        return jsonify({"error": "ISBN, idClient and Rating are required"}), 400

    if not (1 <= int(rating) <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    try:
        # 1. Verificar existência
        book = db.session.get(Book, isbn)
        client = db.session.get(Client, id_client)

        if not book:
            return jsonify({"error": "Book not found"}), 404
        if not client:
            return jsonify({"error": "Client not found"}), 404

        # 2. "Arquivar" review anterior (Lógica do Soft Delete)
        # Buscamos se já existe uma review ATIVA deste cliente para este livro
        previous_review = db.session.query(BookReview).filter(
            BookReview.idClient == id_client,
            BookReview.ISBN == isbn,
            BookReview.is_active == True
        ).first()

        if previous_review:
            previous_review.is_active = False
            # Não damos commit ainda, faremos tudo numa transação só no final

        # Criar a review
        # (Opcional) Verificar se o cliente já avaliou este livro antes e bloquear
        new_review = BookReview(
            idClient=id_client,
            ISBN=isbn,
            Rating=rating,
            comment=comment
        )
        db.session.add(new_review)
        db.session.flush()

        # 3. Recalcular a média do livro (Regra de negócio)
        avg_rating = db.session.query(func.avg(BookReview.Rating)).filter(
            BookReview.ISBN == isbn
        ).scalar()

        # Atualizamos o campo 'Review' na tabela Book com a nova média
        book.Review = float(avg_rating) # O banco cuida do arredondamento decimal(2,1)

        db.session.commit()

        return jsonify({
            'message': 'Review posted successfully',
            'new_book_rating': float(avg_rating),
        }), 201
    except Exception as e:
        db.session.rollback()
        logging.exception(f"Failed to create review: {e}")
        return jsonify({"error": f"Failed to create review: {e}"}), 500

@bp.route('/book/<string:isbn>', methods=['GET'])
def get_book_reviews(isbn):
    """
    Lista todas as avaliações de um livro específico.
    ---
    tags:
      - Reviews
    parameters:
      - name: isbn
        in: path
        type: string
        required: true
    responses:
      200:
        description: Lista de reviews retornada
    """
    try:
        reviews = (db.session.query(
            BookReview,
            Client)
        .join(
            Client
        ).filter(
            BookReview.ISBN == isbn,
            BookReview.Review.is_active == True
        ).all())

        output = []
        for review, client in reviews:
            # Lógica simplificada para nome do cliente
            client_name = "Cliente Anônimo"
            if client.Type == 'PF' and client.client_fp:
                client_name = f"{client.client_fp.FName} {client.client_fp.MName} {client.client_fp.LName}".strip()
            elif client.Type == 'PJ' and client.client_jp:
                client_name = client.client_jp.FantasyName or client.client_jp.Name

            output.append({
                'Rating': review.Rating,
                'Comment': review.Comment,
                'Date': review.ReviewDate,
                'Client': client_name
            })

        return jsonify({'reviews': output}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
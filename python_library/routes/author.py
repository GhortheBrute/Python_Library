import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Author

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('authors', __name__, url_prefix='/api/authors')


@bp.route('/', methods=['POST'])
def create_author():
    """
    Endpoint for creating an author
    Awaits a JSON with author details and address
    ---
    tags:
        - Authors
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            required:
                - FName
                - LName
            properties:
                FName:
                    type: string
                    example: John
                    description: First name of the author
                MName:
                    type: string
                    example: M
                    description: (Optional) Middle name of the author
                LName:
                    type: string
                    example: Silva
                    description: Last name of the author
    responses:
        201:
            description: Author successfully created
            schema:
                type: object
                properties:
                    message:
                        type: string
                        example: "Author successfully created"
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
    required_fields = ['FName', 'LName']

    # Validação de dados Pessoa Física
    for field in required_fields:
        if field not in data:
            return jsonify({"Error": f"Required field {field} is missing"}), 400

    # Transação de Banco de Dados
    try:
        # Criar o Author
        new_author = Author(
            FName=data.get('FName'),
            MName=data.get('MName'),
            LName=data.get('LName')
        )
        db.session.add(new_author)

        # Se tudo certo, comitar a transação
        db.session.commit()

        return jsonify({'message': 'Author successfully created'}), 201

    except Exception as e:
        # Se algo deu errado, reverter tudo
        db.session.rollback()
        logging.error(f"Failed to create author: {e}")
        return jsonify({"error": f"Failed to create author: {e}"}), 500


@bp.route('/', methods=['GET'])
def get_authors():
    """
    Endpoint for getting all authors
    Accepts a 'status' query param:
    - ?status=active (default)
    - ?status=inactive
    - ?status=all
    ---
    tags:
      - Authors
    parameters:
      - name: status
        in: query
        type: string
        default: active
        enum: ['active', 'inactive', 'all']
        description: Filter authors by is_active (active, inactive or all)
    responses:
      200:
        description: Authors list recovered successfully
        schema:
          type: object
          properties:
            authors:
              type: array
              items:
                type: object
                properties:
                  idAuthor:
                    type: integer
                    example: 1
                  Name:
                    type: string
                    example: "Tolkien, J.R.R."
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

        # 1. Fazemos a consulta unindo as 4 tabelas de Clientes
        # (Client, ClientFP, ClientJP, Address)
        query = db.session.query(Author)

        # Adicionamos o filtro de status
        if status_filter == 'active':
            query = query.filter(Author.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(Author.is_active == False)
        elif status_filter == 'all':
            pass
        else:
            return jsonify({"error": "Invalid 'status' parameter. Use 'active', 'inactive', or 'all'."}), 400

        results = query.all()

        # 2. Formatamos os resultados para JSON
        output = []
        for author in results:
            author_data = {
                'idAuthor': author.idAuthor,
                'Name': f"{author.LName}, {author.FName} {author.MName or ''}".strip(),
            }
            output.append(author_data)

        return jsonify({'authors': output}), 200

    except Exception as e:
        logging.error(f"Failed to get authors: {e}")
        return jsonify({"error": f"Failed to get authors"}), 500


@bp.route('/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """
    Endpoint for getting a specific author by ID
    ---
    tags:
      - Authors
    parameters:
      - name: author_id
        in: path
        type: integer
        required: true
        description: Unique Author ID that needs search
    responses:
      200:
        description: Author successfully found
        schema:
          type: object
          properties:
            idAuthor:
              type: integer
              example: 1
            Name:
              type: string
              example: "Tolkien, J.R.R."
      404:
        description: Author not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Author not found"
      500:
        description: Erro interno do servidor
    """
    try:
        # 1. Fazemos a mesma consulta, mas filtramos pelo ID
        result = get_author_by_id(author_id)

        # 2. Verificamos se o cliente foi encontrado
        if not result:
            return jsonify({"error": "Author not found"}), 404

        # 3. Desempacotamos os resultados
        author = result

        # 4. Formatamos o JSON de resposta
        author_data = {
            'idAuthor': author.idAuthor,
            'Name': f"{author.LName}, {author.FName} {author.MName} ",
        }
        return jsonify(author_data), 200

    except Exception as e:
        logging.error(f"Failed to get author: {e}")
        return jsonify({"error": f"Failed to get author: {e}"}), 500


@bp.route('/<int:author_id>', methods=['PUT', 'PATCH'])
def update_author(author_id):
    """
    Endpoint for updating an author
    ---
    tags:
      - Authors
    parameters:
      - name: author_id
        in: path
        type: integer
        required: true
        description: Unique Author ID that needs search

      - name: body
        in: body
        required: true
        schema:
            type: object
            properties:
                FName:
                    type: string
                    example: John
                    description: First name of the author
                MName:
                    type: string
                    example: M
                    description: (Optional) Middle name of the author
                LName:
                    type: string
                    example: Silva
                    description: Last name of the author
    responses:
      200:
        description: Author successfully updated
        schema:
          type: object
          properties:
            idAuthor:
              type: integer
              example: 1
            Name:
              type: string
              example: "Tolkien, J.R.R."
      400:
        description: No data provided
      404:
        description: Author not found
      500:
        description: Server internal error
    """

    # 1. Obter os dados da requisição
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # 2. -- Reaproveitando o código ---
        result = get_author_by_id(author_id)

        if not result:
            return jsonify({"error": "Client not found"}), 404

        # 3. Desempacotando os objetos
        author = result

        # 4. Atualização
        # Atualizamos os campos principais do Cliente
        # data.get('Phone', client.Phone) significa:
        # "Pegue o 'Phone' do JSON, se não existir, use o valor original
        author.FName = data.get('FName', author.FName)
        author.MName = data.get('MName', author.MName)
        author.LName = data.get('LName', author.LName)

        # 5. Salvar as mudanças no banco
        db.session.commit()

        return jsonify({"message": "Author updated successfully"}), 200
    except Exception as e:
        logging.error(f"Failed to update author: {e}")
        return jsonify({"error": f"Failed to update author: {e}"}), 500


@bp.route('/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    """
    Endpoint for deleting an author
    Verify if the author has pendencies
    ---
    tags:
      - Authors
    parameters:
      - name: author_id
        in: path
        type: integer
        required: true
        description: Unique Author ID that needs search
    responses:
      204:
        description: Author successfully deleted
      404:
        description: Author not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Author not found"
    """
    # Soft Delete
    author = db.session.query(Author).filter_by(idAuthor=author_id).first()
    if not author:
        return jsonify({"error": "Author not found"}), 404

    # Apenas marca como inativo
    author.is_active = False
    db.session.commit()

    return '', 204

def get_author_by_id(author_id):
    return db.session.query(
        Author
    ).filter(
        Author.idAuthor == author_id,
        ).first()  # .first() pega apenas um

def get_author_by_name(author_name):
    return db.session.query(
        Author
    ).filter(
        Author.FName == author_name
    ).first()
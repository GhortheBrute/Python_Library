import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Collection

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('collections', __name__, url_prefix='/api/collections')


@bp.route('/', methods=['POST'])
def create_collection():
    """
    Endpoint for creating a collection
    Awaits a JSON with collection details and address
    ---
    tags:
        - Collections
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            required:
                - Name
            properties:
                Name:
                    type: string
                    example: The Lord of the Rings
                    description: Collection name
    responses:
        201:
            description: Collection successfully created
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
    required_fields = ['Name']

    # Validação de dados Pessoa Física
    for field in required_fields:
        if field not in data:
            return jsonify({"Error": f"Required field {field} is missing"}), 400

    # Transação de Banco de Dados
    try:
        # Criar o Collection
        new_collection = Collection(Name=data.get('Name'))
        db.session.add(new_collection)

        # Se tudo certo, comitar a transação
        db.session.commit()

        return jsonify({'message': 'Collection successfully created'}), 201

    except Exception as e:
        # Se algo deu errado, reverter tudo
        db.session.rollback()
        logging.error(f"Failed to create collection: {e}")
        return jsonify({"error": f"Failed to create collection: {e}"}), 500


@bp.route('/', methods=['GET'])
def get_collections():
    """
    Endpoint for getting all collections
    Accepts a 'status' query param:
    - ?status=active (default)
    - ?status=inactive
    - ?status=all
    ---
    tags:
      - Collections
    parameters:
      - name: status
        in: query
        type: string
        default: active
        enum: ['active', 'inactive', 'all']
        description: Filter books by is_active (active, inactive or all)
    responses:
      200:
        description: Collections list recovered successfully
      400:
        description: Invalid 'status' parameter
      500:
        description: Internal server error
    """
    try:
        # Pegamos o parâmetro da url
        # Se nada for passado, o valor padrão é 'active'
        status_filter = request.args.get('status', 'active')

        # 1. Fazemos a consulta unindo as 4 tabelas de Clientes
        # (Client, ClientFP, ClientJP, Address)
        query = db.session.query(Collection)

        # Adicionamos o filtro de status
        if status_filter == 'active':
            query = query.filter(Collection.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(Collection.is_active == False)
        elif status_filter == 'all':
            pass
        else:
            return jsonify({"error": "Invalid 'status' parameter. Use 'active', 'inactive', or 'all'."}), 400

        results = query.all()

        # 2. Formatamos os resultados para JSON
        output = []
        for collection in results:
            collection_data = {
                'idCollection': collection.idCollection,
                'Name': collection.Name
            }
            output.append(collection_data)

        return jsonify({'collections': output}), 200

    except Exception as e:
        logging.error(f"Failed to get collections: {e}")
        return jsonify({"error": f"Failed to get collections"}), 500


@bp.route('/<int:collection_id>', methods=['GET'])
def get_collection(collection_id):
    """
    Endpoint for getting a specific collection by ID
    ---
    tags:
        - Collections
    parameters:
        - name: collection_id
          in: path
          type: integer
          required: true
          description: ID of collection
    responses:
        200:
            description: A Collections list recovered successfully
        404:
            description: Collection not found
        500:
            description: Internal server error
    """
    try:
        # 1. Fazemos a mesma consulta, mas filtramos pelo ID
        result = get_collection_by_id(collection_id)

        # 2. Verificamos se o cliente foi encontrado
        if not result:
            return jsonify({"error": "Collection not found"}), 404

        # 3. Desempacotamos os resultados
        collection = result

        # 4. Formatamos o JSON de resposta
        collection_data = {
            'idCollection': collection.idCollection,
            'Name': collection.Name,
        }
        return jsonify(collection_data), 200

    except Exception as e:
        logging.error(f"Failed to get collection: {e}")
        return jsonify({"error": f"Failed to get collection: {e}"}), 500


@bp.route('/<int:collection_id>', methods=['PUT', 'PATCH'])
def update_collection(collection_id):
    """
    Endpoint for updating a collection
    ---
    tags:
        - Collections
    parameters:
        - name: collection_id
          in: path
          type: integer
          required: true
          description: ID of collection
    responses:
        200:
            description: Collection updated successfully
        400:
            description: No data provided
        404:
            description: Collection not found
        500:
            description: Internal server error

    """

    # 1. Obter os dados da requisição
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # 2. -- Reaproveitando o código ---
        result = get_collection_by_id(collection_id)

        if not result:
            return jsonify({"error": "Client not found"}), 404

        # 3. Desempacotando os objetos
        collection = result

        # 4. Atualização
        # Atualizamos os campos principais do Cliente
        # data.get('Phone', client.Phone) significa:
        # "Pegue o 'Phone' do JSON, se não existir, use o valor original
        collection.Name = data.get('Name', collection.Name)

        # 5. Salvar as mudanças no banco
        db.session.commit()

        return jsonify({"error": "Collection updated successfully"}), 200
    except Exception as e:
        logging.error(f"Failed to update collection: {e}")
        return jsonify({"error": f"Failed to update collection: {e}"}), 500


@bp.route('/<int:collection_id>', methods=['DELETE'])
def delete_collection(collection_id):
    """
    Endpoint for deleting a collection
    Verify if the collection has pendencies
    ---
    tags:
        - Collections
    parameters:
        - name: collection_id
          in: path
          type: integer
          required: true
          description: ID of collection
    responses:
        204:
            description: Collection deleted successfully
        404:
            description: Collection not found
    """
    # Soft Delete
    collection = db.session.query(Collection).filter_by(idCollection=collection_id).first()
    if not collection:
        return jsonify({"error": "Collection not found"}), 404

    # Apenas marca como inativo
    collection.is_active = False
    db.session.commit()

    return '', 204


def get_collection_by_id(collection_id):
    return db.session.query(
        Collection
    ).filter(
        Collection.idCollection == collection_id,
    ).first()  # .first() pega apenas um


def get_collection_by_name(collection_name):
    return db.session.query(
        Collection
    ).filter(
        Collection.FName == collection_name
    ).first()
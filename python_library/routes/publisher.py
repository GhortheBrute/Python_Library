import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Address, Publisher

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('publishers', __name__, url_prefix='/api/publishers')

@bp.route('/', methods=['POST'])
def create_publisher():
    """
    Endpoint for creating a publisher
    Awaits a JSON with publisher details and address
    ---
    tags:
        - Publishers
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            required:
                - Address
                - CNPJ
                - Name
            properties:
                CNPJ:
                    type: string
                    example: 10123456000100
                    description: Unique CNPJ of publisher
                Name:
                    type: string
                    example: Publisher A
                    description: Publisher name
                Address:
                    type: object
                    description: Address information
                    required:
                        - Road
                        - Neighbourhood
                        - City
                        - State
                        - ZipCode
                    properties:
                        Road:
                          type: string
                          example: "Rua das Flores"
                          description: Street name
                        Number:
                          type: string
                          example: "123"
                          description: Address number
                        Neighbourhood:
                          type: string
                          example: "Centro"
                          description: Neighbourhood name
                        City:
                          type: string
                          example: "Curitiba"
                          description: City name
                        State:
                          type: string
                          example: "PR"
                          description: State/Province name
                        ZipCode:
                          type: string
                          example: "80000-000"
                          description: Zip Code
                        Complement:
                          type: string
                          example: "Apto 101"
                          description: Any complementary address info
    responses:
        201:
            description: Publisher successfully created
        400:
            description: No data provided
        404:
            description: One or more required fields are missing
        500:
            description: Internal server error
    """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validação simples
    required_fields = ['Address', 'CNPJ', 'Name']

    # Validação de dados Pessoa Física
    for field in required_fields:
        if field not in data:
            return jsonify({"Error": f"Required field {field} is missing"}), 400

    # Transação de Banco de Dados
    try:
        # 1. Criar o Endereço primeiro
        address_data = data['Address']
        new_address = Address(
            Road=address_data.get('Road'),
            Neighbourhood=address_data.get('Neighbourhood'),
            Number=address_data.get('Number'),
            City=address_data.get('City'),
            State=address_data.get('State'),
            ZipCode=address_data.get('ZipCode'),
            Complement=address_data.get('Complement')
        )
        db.session.add(new_address)

        # Flush para gerar os dados de Address
        db.session.flush()

        # 2. Criar o Publisher
        new_publisher = Publisher(
            idAddress=new_address.idAddress, #Usar o ID do endereço gerado
            CNPJ=data.get('CNPJ'),
            Name=data.get('Name')
        )
        db.session.add(new_publisher)

        # 4. Se tudo certo, comitar a transação
        db.session.commit()

        return jsonify({'message': 'Publisher successfully created'}), 201

    except Exception as e:
        # 5. Se algo deu errado, reverter tudo
        db.session.rollback()
        logging.error(f"Failed to create publisher: {e}")
        return jsonify({"error": f"Failed to create publisher: {e}"}), 500

@bp.route('/', methods=['GET'])
def get_publishers():
    """
    Endpoint for getting all publishers
    ---
    tags:
        - Publishers
    responses:
        200:
            description: Publishers list successfully recovered
        400:
            description: Invalid 'status' parameters
        500:
            description: Internal server error
    """
    try:
        # Filtros
        status_filter = request.args.get('status', 'active')

        # 1. Fazer consulta juntando Publisher e Address
        query = db.session.query(
            Publisher,
            Address
        ).join(
            Address
        ).filter(

        )

        # Adicionamos o filtro de status
        if status_filter == 'active':
            query = query.filter(Publisher.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(Publisher.is_active == False)
        elif status_filter == 'all':
            pass
        else:
            return jsonify({"error": "Invalid 'status' parameter. Use 'active', 'inactive', or 'all'."}), 400

        results = query.all()

        output = []
        for publisher, address in results:
            publisher_data = {
                'idPublisher': publisher.idPublisher,
                'Name': publisher.Name,
                'CNPJ': publisher.CNPJ,
                'Address': {
                    'Road': address.Road,
                    'Neighbourhood': address.Neighbourhood,
                    'Number': address.Number,
                    'City': address.City,
                    'State': address.State,
                    'ZipCode': address.ZipCode,
                    'Complement': address.Complement
                }
            }
            output.append(publisher_data)

        return jsonify({'publishers': output}), 200
    except Exception as e:
        logging.error(f"Failed to get publishers: {e}")
        return jsonify({"error": f"Failed to get publishers: {e}"}), 500

@bp.route('/<publisher_id>', methods=['GET'])
def get_publisher(publisher_id):
    """
    Endpoint for getting a publisher by ID
    ---
    tags:
        - Publishers
    parameters:
        - name: publisher_id
          in: path
          type: integer
          required: true
          description: Publisher ID that needs to be found
    responses:
        200:
            description: Publisher successfully recovered
        404:
            description: Publisher not found
        500:
            description: Internal server error
    """
    try:
        result = get_publisher_by_id(publisher_id)

        if not result:
            return jsonify({'message': 'Publisher not found'}), 404

        publisher, address = result

        publisher_data = {
            'idPublisher': publisher.idPublisher,
            'Name': publisher.Name,
            'CNPJ': publisher.CNPJ,
            'Address': {
                'Road': address.Road,
                'Neighbourhood': address.Neighbourhood,
                'Number': address.Number,
                'City': address.City,
                'State': address.State,
                'ZipCode': address.ZipCode,
                'Complement': address.Complement
            }
        }
        return jsonify({'publisher': publisher_data}), 200
    except Exception as e:
        logging.error(f"Failed to get publisher: {e}")
        return jsonify({"error": f"Failed to get publisher: {e}"}), 500

@bp.route('/<publisher_id>', methods=['PUT', 'PATCH'])
def update_publisher(publisher_id):
    """
    Endpoint for updating a publisher
    ---
    tags:
        - Publishers
    parameters:
        - name: publisher_id
          in: path
          type: integer
          required: true
          description: Publisher ID that needs to be updated

        - name: body
          in: body
          required: true
          schema:
          type: object
          properties:
            Name:
                type: string
                example: Publisher A
                description: Publisher Name
            Address:
                    type: object
                    description: Address information
                    properties:
                        Road:
                          type: string
                          example: "Rua das Flores"
                          description: Street name
                        Number:
                          type: string
                          example: "123"
                          description: Address number
                        Neighbourhood:
                          type: string
                          example: "Centro"
                          description: Neighbourhood name
                        City:
                          type: string
                          example: "Curitiba"
                          description: City name
                        State:
                          type: string
                          example: "PR"
                          description: State/Province name
                        ZipCode:
                          type: string
                          example: "80000-000"
                          description: Zip Code
                        Complement:
                          type: string
                          example: "Apto 101"
                          description: Any complementary address info
    responses:
        200:
            description: Publisher details updated successfully
        400:
            description: No data provided
        404:
            description: Publisher not found
        500:
            description: Internal server error

    """
    try:
        # Obtém os dados do body
        data = request.get_json()

        # Se não houver nada no body, cancela o processo
        if not data:
            return jsonify({'message': 'No data provided'}), 400

        # Reaproveita o código de busca por ID
        result = get_publisher_by_id(publisher_id)

        # Se retornar a busca vazia, cancela o processo
        if not result:
            return jsonify({'message': 'Publisher not found'}), 404

        # Descompacta os objetos
        publisher, address = result

        # Atualiza o único campo possível de Publisher
        # Senão, mantém o atual
        publisher.Name = data.get('Name', publisher.Name)

        # Atualizamos o endereço, se enviado no JSON
        if 'Address' in data:
            address_data = data['Address']
            address.Road = address_data.get('Road', address.Road)
            address.Neighbourhood = address_data.get('Neighbourhood', address.Neighbourhood)
            address.Number = address_data.get('Number', address.Number)
            address.City = address_data.get('City', address.City)
            address.State = address_data.get('State', address.State)
            address.ZipCode = address_data.get('ZipCode', address.ZipCode)
            address.Complement = address_data.get('Complement', address.Complement)

        # Salva as mudanças no banco
        db.session.commit()

        return jsonify({'publisher': "Publisher updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to update publisher: {e}")
        return jsonify({"error": f"Failed to update publisher: {e}"}), 500

@bp.route('/<publisher_id>', methods=['DELETE'])
def delete_publisher(publisher_id):
    """
    Endpoint for soft-deleting a publisher
    ---
    tags:
        - Publishers
    parameters:
        - name: publisher_id
          in: path
          type: integer
          required: true
          description: Publisher ID that needs to be deleted
    responses:
        204:
            description: Publisher successfully marked as inactive
        404:
            description: Publisher not found
        500:
            description: Internal server error
    """
    try:
        result = get_publisher_by_id(publisher_id)

        if not result:
            return jsonify({'message': 'Publisher not found'}), 404

        publisher, address = result

        publisher.is_active = False
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to delete publisher: {e}")
        return jsonify({"error": f"Failed to delete publisher: {e}"}), 500

def get_publisher_by_id(publisher_id):
    return db.session.query(
        Publisher,
        Address
    ).join(
        Address
    ).filter(
        Publisher.idPublisher == publisher_id
    ).first()
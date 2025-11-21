import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Address, Client, ClientFP, ClientJP, BookReview, Book

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('clients', __name__, url_prefix='/api/clients')


@bp.route('/', methods=['POST'], strict_slashes=False)
def create_client():
    """
    Endpoint for creating a client
    Awaits a JSON with client details and address
    ---
    tags:
      - Clients
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - Type
            - Email
            - Phone
            - Address
          properties:
            Type:
              type: string
              enum: ['PF', 'PJ']
              description: Tipo de pessoa (Física ou Jurídica)
            Email:
              type: string
              example: "cliente@email.com"
            Phone:
              type: string
              example: "(41) 99999-8888"

            # --- Campos Específicos de PF ---
            CPF:
              type: string
              description: (Obrigatório se Type=PF)
              example: "12345678900"
            FName:
              type: string
              description: (Obrigatório se Type=PF) Primeiro Nome
            MName:
              type: string
              description: (Opcional) Nome do Meio
            LName:
              type: string
              description: (Obrigatório se Type=PF) Sobrenome
            Birthdate:
              type: string
              format: date
              description: (Obrigatório se Type=PF) YYYY-MM-DD

            # --- Campos Específicos de PJ ---
            CNPJ:
              type: string
              description: (Obrigatório se Type=PJ)
            Name:
              type: string
              description: (Obrigatório se Type=PJ) Razão Social
            FantasyName:
              type: string
              description: (Opcional) Nome Fantasia

            # --- O OBJETO ANINHADO (ADDRESS) ---
            Address:
              type: object
              description: Dados do endereço do cliente
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
                Number:
                  type: string
                  example: "123"
                Neighbourhood:
                  type: string
                  example: "Centro"
                City:
                  type: string
                  example: "Curitiba"
                State:
                  type: string
                  example: "PR"
                ZipCode:
                  type: string
                  example: "80000-000"
                Complement:
                  type: string
                  example: "Apto 101"
    responses:
      201:
        description: Cliente criado com sucesso
      400:
        description: Dados inválidos ou faltando
      500:
        description: Erro interno
    """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validação simples
    required_fields_fp = ['Email', 'Phone', 'Address', 'CPF', 'FName', 'LName', 'Birthdate']
    required_fields_jp = ['Email', 'Phone', 'Address', 'CNPJ', 'Name']

    # Validação de dados Pessoa Física
    if data.get('Type') == 'PF':
        for field in required_fields_fp:
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

            # 2. Criar o Cliente pai
            new_client = Client(
                Type='PF',
                idAddress=new_address.idAddress,  #Usar o ID do endereço gerado
                Phone=data.get('Phone'),
                Email=data.get('Email')
            )
            db.session.add(new_client)

            # Flush para ter o idClient
            db.session.flush()

            new_client_fp = ClientFP(
                idClient=new_client.idClient,
                CPF=data.get('CPF'),
                FName=data.get('FName'),
                MName=data.get('MName'),
                LName=data.get('LName'),
                Birthdate=data.get('Birthdate')
            )
            db.session.add(new_client_fp)

            # 4. Se tudo certo, comitar a transação
            db.session.commit()

            return jsonify({'message': 'Client successfully created'}), 201

        except Exception as e:
            # 5. Se algo deu errado, reverter tudo
            db.session.rollback()
            logging.error(f"Failed to create client: {e}")
            return jsonify({"error": f"Failed to create client"}), 500

    elif data.get('Type') == 'PJ':
        # Validação de dados Pessoa Física
        if data.get('Type') == 'PJ':
            for field in required_fields_jp:
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

            # 2. Criar o Cliente pai
            new_client = Client(
                Type='PJ',
                idAddress=new_address.idAddress,  #Usar o ID do endereço gerado
                Phone=data.get('Phone'),
                Email=data.get('Email')
            )
            db.session.add(new_client)

            # Flush para ter o idClient
            db.session.flush()

            new_client_jp = ClientJP(
                idClient=new_client.idClient,
                CNPJ=data.get('CNPJ'),
                Name=data.get('Name'),
                FantasyName=data.get('FantasyName'),
            )
            db.session.add(new_client_jp)

            # 4. Se tudo certo, comitar a transação
            db.session.commit()

            return jsonify({'message': 'Client PJ successfully created'}), 201
        except Exception as e:
            # 5. Se algo deu errado, reverter tudo
            db.session.rollback()
            logging.error(f"Failed to create client: {e}")
            return jsonify({"error": f"Failed to create client"}), 500

    else:
        return jsonify({"error": "Client type must be 'PF'"}), 201


@bp.route('/', methods=['GET'])
def get_clients():
    """
    Endpoint for getting all clients
    Accepts a 'status' query param:
    - ?status=active (default)
    - ?status=inactive
    - ?status=all
    ---
    tags:
        - Clients
    parameters:
      - name: status
        in: query
        type: string
        default: active
        enum: ['active', 'inactive', 'all']
        description: Filter clients by is_active (active, inactive or all)
    responses:
      200:
        description: Clients list recovered successfully
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
        query = db.session.query(
            Client,
            ClientFP,
            ClientJP,
            Address
        ).join(
            Address, Client.idAddress == Address.idAddress
        ).outerjoin(
            ClientJP, Client.idClient == ClientJP.idClient
        ).outerjoin(
            ClientFP, Client.idClient == ClientFP.idClient
        )

        # Adicionamos o filtro de status
        if status_filter == 'active':
            query = query.filter(Client.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(Client.is_active == False)
        elif status_filter == 'all':
            pass
        else:
            return jsonify({"error": "Invalid 'status' parameter. Use 'active', 'inactive', or 'all'."}), 400

        results = query.all()

        # 2. Formatamos os resultados para JSON
        output = []
        for client, client_fp, client_jp, address in results:
            # Foco em Pessoas Físicas por enquanto
            if client.Type == 'PF':
                client_data = {
                    'idClient': client.idClient,
                    'Type': client.Type,
                    'CPF': client_fp.CPF,
                    'Name': f"{client_fp.FName} {client_fp.MName  or ''} {client_fp.LName}".strip(),
                    'Birthdate': client_fp.Birthdate.isoformat() if client_fp.Birthdate else None,
                    'Phone': client.Phone,
                    'Email': client.Email,
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
                output.append(client_data)

            # Para Pessoa Jurídica
            elif client.Type == 'PJ':
                client_data = {
                    'idClient': client.idClient,
                    'Type': client.Type,
                    'CNPJ': client_jp.CNPJ,
                    'Name': client_jp.Name,
                    'FantasyName': client_jp.FantasyName,
                    'Phone': client.Phone,
                    'Email': client.Email,
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
                output.append(client_data)

        return jsonify({'clients': output}), 200

    except Exception as e:
        logging.error(f"Failed to get clients: {e}")
        return jsonify({"error": f"Failed to get clients"}), 500


@bp.route('/<int:client_id>', methods=['GET'])
def get_client(client_id):
    """
    Endpoint for getting a specific client by ID
    ---
    tags:
      - Clients
    parameters:
      - name: client_id
        in: path
        type: integer
        required: true
        description: Unique Client ID that needs search
    responses:
      200:
        description: Client successfully found
      404:
        description: Client not found
      500:
        description: Erro interno do servidor
    """
    try:
        # 1. Fazemos a mesma consulta, mas filtramos pelo ID
        result = get_client_by_id(client_id)

        # 2. Verificamos se o cliente foi encontrado
        if not result:
            return jsonify({"error": "Client not found"}), 404

        # 3. Desempacotamos os resultados
        client, client_fp, client_jp, address = result

        # 4. Formatamos o JSON de resposta
        # Para PF
        if client.Type == 'PF':
            client_data = {
                'idClient': client.idClient,
                'Type': client.Type,
                'CPF': client_fp.CPF,
                'FName': client_fp.FName,
                'MName': client_fp.MName,
                'LName': client_fp.LName,
                'Birthdate': client_fp.Birthdate.isoformat() if client_fp.Birthdate else None,
                'Phone': client.Phone,
                'Email': client.Email,
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
            return jsonify(client_data), 200

        elif client.Type == 'PJ':
            client_data = {
                'idClient': client.idClient,
                'Type': client.Type,
                'CNPJ': client_jp.CNPJ,
                'Name': client_jp.Name,
                'FantasyName': client_jp.FantasyName,
                'Phone': client.Phone,
                'Email': client.Email,
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
            return jsonify(client_data), 200

        else:
            return jsonify({"error": "Client not found"}), 404

    except Exception as e:
        logging.error(f"Failed to get client: {e}")
        return jsonify({"error": f"Failed to get client: {e}"}), 500


@bp.route('/<int:client_id>', methods=['PUT', 'PATCH'])
def update_client(client_id):
    """
    Endpoint for updating a client
    ---
    tags:
      - Clients
    parameters:
      - name: client_id
        in: path
        type: integer
        required: true
        description: Unique Client ID that needs search

      - name: body
        in: body
        required: true
        schema:
            type: object
            properties:
                Email:
                  type: string
                  example: "cliente@email.com"
                Phone:
                  type: string
                  example: "(41) 99999-8888"

                # --- Campos Específicos de PF ---
                FName:
                  type: string
                  description: Primeiro Nome
                MName:
                  type: string
                  description: (Opcional) Nome do Meio
                LName:
                  type: string
                  description: Sobrenome

                # --- Campos Específicos de PJ ---
                Name:
                  type: string
                  description: Razão Social
                FantasyName:
                  type: string
                  description: Nome Fantasia
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
        description: Client successfully updated
      400:
        description: No data provided
      404:
        description: Client not found
      500:
        description: Server internal error
    """

    # 1. Obter os dados da requisição
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # 2. -- Reaproveitando o código ---
        result = get_client_by_id(client_id)

        if not result:
            return jsonify({"error": "Client not found"}), 404

        # 3. Desempacotando os objetos
        client, client_fp, client_jp, address = result

        # 4. Atualização
        # Atualizamos os campos principais do Cliente
        # data.get('Phone', client.Phone) significa:
        # "Pegue o 'Phone' do JSON, se não existir, use o valor original
        client.Phone = data.get('Phone', client.Phone)
        client.Email = data.get('Email', client.Email)

        # Atualizamos o endereço, se já foi enviado no JSON
        if 'Address' in data:
            address_data = data['Address']
            address.Road = address_data.get('Road', address.Road)
            address.Neighbourhood = address_data.get('Neighbourhood', address.Neighbourhood)
            address.Number = address_data.get('Number', address.Number)
            address.City = address_data.get('City', address.City)
            address.State = address_data.get('State', address.State)
            address.ZipCode = address_data.get('ZipCode', address.ZipCode)
            address.Complement = address_data.get('Complement', address.Complement)

        # Atualizamos os dados da Pessoa Física
        if client.Type == 'PF' and client_fp:
            client_fp.FName = data.get('FName', client_fp.FName)
            client_fp.MName = data.get('MName', client_fp.MName)
            client_fp.LName = data.get('LName', client_fp.LName)
            client_fp.Birthdate = data.get('Birthdate', client_fp.Birthdate)
            # O CPF não é permitido ser alterado

        # Atualizamos os dados de Pessoa Jurídica
        elif client.Type == 'PJ' and client_jp:
            client_jp.Name = data.get('Name', client_jp.Name)
            client_jp.FantasyName = data.get('FantasyName', client_jp.FantasyName)
            # O CNPJ não é permitido ser alterado

        # 5. Salvar as mudanças no banco
        db.session.commit()

        return jsonify({"error": "Client updated successfully"}), 200
    except Exception as e:
        logging.error(f"Failed to update client: {e}")
        return jsonify({"error": f"Failed to update client: {e}"}), 500


@bp.route('/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
    """
    Endpoint for deleting a client
    Verify if the client has pendencies
    ---
    tags:
        - Clients
    parameters:
        - name: client_id
          in: path
          type: integer
          required: true
          description: Client ID to be found
    responses:
        204:
            description: Client deleted successfully
        404:
            description: Client not found
    """
    # Soft Delete
    client = db.session.query(Client).filter_by(idClient=client_id).first()
    if not client:
        return jsonify({"error": "Client not found"}), 404

    # Apenas marca como inativo
    client.is_active = False
    db.session.commit()

    return '', 204

    # HARD DELETE
    # try:
    #
    #     # 1. Pesquisar se o cliente existe
    #     result = get_client_by_id(client_id)
    #
    #     if not result:
    #         return jsonify({"error": "Client not found"}), 404
    #
    #     # 2. Descompacta o resultado
    #     client, client_fp, client_jp, address = result
    #
    #     # 3. Verifica se há empréstimos (Regras de Negócio)
    #     active_loans = db.session.query(BookLoan).filter(
    #         BookLoan.idClient == client_id,
    #         BookLoan.Status != 'RETURNED'
    #     ).count()
    #
    #     if active_loans > 0:
    #         # 409 Conflict é o status ideal para a "Ação conflita"
    #         return jsonify({
    #             "error": "Cannot delete. Client has pendencies",
    #             "pendencies": active_loans
    #         }), 409
    #
    #     # 4. Limpar Reservas (Regra de Negócio 2)
    #     # Deleta todas as reservas associadas ao este cliente
    #     # .delete() é muito mais eficiente em um loop
    #     db.sessio.query(Reserve).filter_by(idClient=client_id).delete()
    #
    #     # 5. Limpar o histórico
    #     # Devemos deletar o histórico de empréstimos
    #     # antes de deletar o cliente, para evitar erro de Foreign Key
    #     db.session.query(BookLoan).filter_by(idClient=client_id).delete()
    #
    #     # 6. Deleção principal
    #     # A Ordem importa
    #     # Primeiro os filhos, depois o pai
    #     if client_fp:
    #         db.session.delete(client_fp)
    #     if client_jp:
    #         db.session.delete(client_jp)
    #
    #     # Deleta o pai
    #     db.session.delete(client)
    #
    #     # Deleta a dependência de endereço
    #     db.session.delete(address)
    #
    #     # Comita a transação inteira
    #     db.session.commit()
    #     return '', 204
    #
    # except Exception as e:
    #     db.session.rollback()
    #     logging.error(f"Failed to delete client: {e}")
    #     return jsonify({"error": f"Failed to delete client: {e}"}), 500


@bp.route('/<client_id>/reviews', methods=['GET'])
def get_client_review_history(client_id):
    """
    Endpoint for getting client review history
    ---
    tags:
        - Clients
    parameters:
      - name: client_id
        in: path
        type: integer
        required: true
        description: ID do cliente
    responses:
      200:
        description: Histórico recuperado com sucesso
        schema:
          type: object
          properties:
            client:
              type: string
              example: "João Silva"
            history:
              type: array
              items:
                type: object
                properties:
                  BookTitle:
                    type: string
                  Rating:
                    type: integer
                  Comment:
                    type: string
                  Date:
                    type: string
                  Status:
                    type: string
                    example: "Atual"
      404:
        description: Cliente não encontrado
    """
    try:
        # 1. Verificar se o cliente existe
        client = db.session.get(Client, client_id)
        if not client:
            return jsonify({"error": "Client not found"}), 404

        # 2. Buscar as reviews
        # Juntando com Book para pegar o título
        # Ordenamos por data decrescente
        results = db.session.query(
            BookReview,
            Book
        ).join(
            Book, BookReview.ISBN == Book.ISBN
        ).filter(
            BookReview.idClient == client_id
        ).order_by(
            BookReview.ReviewDate.desc()
        ).all()

        # 3. Formatar a saída
        history = []
        for review, book in results:
            history.append({
                'BookTitle': book.Title,
                'ISBN': book.ISBN,
                'Rating': review.Rating,
                'Comment': review.Comment,
                'Date': review.ReviewDate.isoformat(),
                'Status': 'Atual' if review.is_active else 'Arquivado'
            })

        client_name = 'Cliente'
        if client.Type == 'PF' and client.client_fp:
            client_name = f"{client.client_fp.FName} {client.client_fp.MName} {client.client_fp.LName}".strip()
        elif client.Type == 'PJ' and client.client_jp:
            client_name = client.client_jp.FantasyName

        return jsonify({
            "client": client_name,
            "count": len(history),
            "history": history
        }), 200
    except Exception as e:
        logging.error(f"Failed to get client history: {e}")
        return jsonify({"error": f"Failed to get client history: {e}"}), 500

def get_client_by_id(client_id):
    return db.session.query(
        Client,
        ClientFP,
        ClientJP,
        Address
    ).join(
        Address, Client.idAddress == Address.idAddress
    ).outerjoin(
        ClientJP, Client.idClient == ClientJP.idClient
    ).outerjoin(
        ClientFP, Client.idClient == ClientFP.idClient
    ).filter(
        Client.idClient == client_id,
    ).first()  # .first() pega apenas um
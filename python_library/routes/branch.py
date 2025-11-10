import logging

from flask import Blueprint, request, jsonify

from .. import db
from ..models import Branch, Address

# 'Blueprint' é como organizamos um grupo de rotas
bp = Blueprint('branchs', __name__, url_prefix='/api/branchs')


@bp.route('/', methods=['POST'])
def create_branch():
    """
    Endpoint for creating a branch
    Awaits a JSON with branch details and address
    """
    data = request.get_json()

    if not data:
        return jsonify({'message': 'No data provided'}), 400

    # Validação simples
    required_fields = ['Address', 'BranchName']

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

        # Criar a Branch
        new_branch = Branch(
            BranchName='BranchName',
            idAddress=new_address.idAddress
        )
        db.session.add(new_branch)

        # Se tudo certo, comitar a transação
        db.session.commit()

        return jsonify({'message': 'Branch successfully created'}), 201

    except Exception as e:
        # Se algo deu errado, reverter tudo
        db.session.rollback()
        logging.error(f"Failed to create branch: {e}")
        return jsonify({"error": f"Failed to create branch: {e}"}), 500


@bp.route('/', methods=['GET'])
def get_branches():
    """
    Endpoint for getting all branches
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
            Branch,
            Address
        ).join(
            Address
        )

        # Adicionamos o filtro de status
        if status_filter == 'active':
            query = query.filter(Branch.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(Branch.is_active == False)
        elif status_filter == 'all':
            pass
        else:
            return jsonify({"error": "Invalid 'status' parameter. Use 'active', 'inactive', or 'all'."}), 400

        results = query.all()

        # 2. Formatamos os resultados para JSON
        output = []
        for branch, address in results:
            branch_data = {
                'idBranch': branch.idBranch,
                'BranchName': branch.BranchName,
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
            output.append(branch_data)

        return jsonify({'branches': output}), 200

    except Exception as e:
        logging.error(f"Failed to get branches: {e}")
        return jsonify({"error": f"Failed to get branches"}), 500


@bp.route('/<int:branch_id>', methods=['GET'])
def get_branch(branch_id):
    """
    Endpoint for getting a specific branch by ID
    """
    try:
        # 1. Fazemos a mesma consulta, mas filtramos pelo ID
        result = get_branch_by_id(branch_id)

        # 2. Verificamos se o cliente foi encontrado
        if not result:
            return jsonify({"error": "Branch not found"}), 404

        # 3. Desempacotamos os resultados
        branch, address = result

        # 4. Formatamos o JSON de resposta
        branch_data = {
            'idBranch': branch.idBranch,
            'BranchName': branch.BranchName,
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
        return jsonify(branch_data), 200

    except Exception as e:
        logging.error(f"Failed to get branch: {e}")
        return jsonify({"error": f"Failed to get branch: {e}"}), 500


@bp.route('/<int:branch_id>', methods=['PUT', 'PATCH'])
def update_branch(branch_id):
    """
    Endpoint for updating a branch
    """

    # 1. Obter os dados da requisição
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    try:
        # 2. -- Reaproveitando o código ---
        result = get_branch_by_id(branch_id)

        if not result:
            return jsonify({"error": "Client not found"}), 404

        # 3. Desempacotando os objetos
        branch, address = result

        # 4. Atualização
        # Atualizamos os campos principais do Cliente
        # data.get('Phone', client.Phone) significa:
        # "Pegue o 'Phone' do JSON, se não existir, use o valor original
        branch.BranchName = data.get('BranchName', branch.BranchName)

        if 'Address' in data:
            address_data = data['Address']
            address.Road = address_data.get('Road', address.Road)
            address.Neighbourhood = address_data.get('Neighbourhood', address.Neighbourhood)
            address.Number = address_data.get('Number', address.Number)
            address.City = address_data.get('City', address.City)
            address.State = address_data.get('State', address.State)
            address.ZipCode = address_data.get('ZipCode', address.ZipCode)
            address.Complement = address_data.get('Complement', address.Complement)

        # 5. Salvar as mudanças no banco
        db.session.commit()

        return jsonify({"error": "Branch updated successfully"}), 200
    except Exception as e:
        logging.error(f"Failed to update branch: {e}")
        return jsonify({"error": f"Failed to update branch: {e}"}), 500


@bp.route('/<int:branch_id>', methods=['DELETE'])
def delete_branch(branch_id):
    """
    Endpoint for deleting a branch
    Verify if the branch has pendencies
    """
    # Soft Delete
    branch = db.session.query(Branch).filter_by(idBranch=branch_id).first()
    if not branch:
        return jsonify({"error": "Branch not found"}), 404

    # Apenas marca como inativo
    branch.is_active = False
    db.session.commit()

    return '', 204

def get_branch_by_id(branch_id):
    return db.session.query(
        Branch,
        Address
    ).join(
        Address
    ).filter(
        Branch.idBranch == branch_id,
    ).first()  # .first() pega apenas um

def get_branch_by_name(branch_name):
    return db.session.query(
        Branch,
        Address
    ).join(
        Address
    ).filter(
        Branch.FName == branch_name
    ).first()
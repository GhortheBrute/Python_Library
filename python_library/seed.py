import logging
import random
from datetime import datetime, timedelta
from faker import Faker
from . import db
from .models import (
    Address, Branch, Publisher, Author, Language, Collection,
    Book, PhysicalBook, Client, ClientFP, ClientJP, BookLoan, Reserve
)

# Inicializa o Faker para gerar dados em português
fake = Faker('pt_BR')

def register_seed_command(app):
    """Register commands 'seed-db' for this application"""

    @app.cli.command("seed-db")
    def seed_db():
        """
        Popula o banco de dados com dados iniciais realistas.
        """
        try:
            # --- LIMPEZA (CUIDADO!) ---
            # Deleta em ordem inversa das dependências
            print("Limpando dados antigos...")
            db.session.query(Reserve).delete()
            db.session.query(BookLoan).delete()
            db.session.query(PhysicalBook).delete()
            db.session.query(Book).delete()
            db.session.query(Collection).delete()
            db.session.query(Language).delete()
            db.session.query(Author).delete()
            db.session.query(Publisher).delete()
            db.session.query(ClientFP).delete()
            db.session.query(ClientJP).delete()
            db.session.query(Client).delete()
            db.session.query(Branch).delete()
            db.session.query(Address).delete()
            db.session.commit()
            print("Dados antigos limpos.")

            print("Iniciando a população do banco...")

            # --- 1. Endereços (Muitos) ---
            addresses = []
            for _ in range(15): # Criar endereços para filiais, editoras e clientes
                addr = Address(
                    Road=fake.street_name(),
                    Neighbourhood=fake.bairro(),
                    Number=fake.building_number(),
                    City=fake.city(),
                    State=fake.state_abbr(),
                    ZipCode=fake.postcode().replace('-', ''),
                    Complement=fake.bothify(text='Apto ###') if random.choice([True, False]) else None
                )
                addresses.append(addr)
            db.session.add_all(addresses)
            db.session.commit() # Commit para que os endereços tenham IDs

            # --- 2. Filiais (Branches) (2) ---
            branch1 = Branch(BranchName="Filial Central", address=addresses.pop())
            branch2 = Branch(BranchName="Filial Bairro", address=addresses.pop())
            db.session.add_all([branch1, branch2])
            branches = [branch1, branch2]

            # --- 3. Editoras (Publishers) (3) ---
            pub1 = Publisher(Name="Editora Fantasia", CNPJ=fake.cnpj().replace('.','').replace('/','').replace('-',''), address=addresses.pop())
            pub2 = Publisher(Name="Livros Acadêmicos", CNPJ=fake.cnpj().replace('.','').replace('/','').replace('-',''), address=addresses.pop())
            pub3 = Publisher(Name="Cia das Letras Fictícia", CNPJ=fake.cnpj().replace('.','').replace('/','').replace('-',''), address=addresses.pop())
            db.session.add_all([pub1, pub2, pub3])
            publishers = [pub1, pub2, pub3]

            # --- 4. Autores (5) ---
            authors = []
            for _ in range(5):
                authors.append(Author(FName=fake.first_name(), LName=fake.last_name()))
            db.session.add_all(authors)

            # --- 5. Coleções (4) ---
            collections = []
            for name in ["Crônicas de Gelo e Fogo", "Harry Potter", "Fundação", "Investigação Policial"]:
                collections.append(Collection(Name=name))
            db.session.add_all(collections)

            # --- 6. Idiomas (Fonte ISO 639-1) ---
            print("Populando idiomas...")

            # Esta é a sua "fonte" de dados padrão
            language_list_source = [
                {'code': 'pt-BR', 'name': 'Português (Brasil)'},
                {'code': 'pt-PT', 'name': 'Português (Portugal)'},
                {'code': 'en-US', 'name': 'Inglês (EUA)'},
                {'code': 'en-GB', 'name': 'Inglês (Reino Unido)'},
                {'code': 'en-AU', 'name': 'Inglês (Austrália)'},
                {'code': 'en-CA', 'name': 'Inglês (Canadá)'},
                {'code': 'es-ES', 'name': 'Espanhol (Espanha)'},
                {'code': 'es-MX', 'name': 'Espanhol (México)'},
                {'code': 'es-AR', 'name': 'Espanhol (Argentina)'},
                {'code': 'es-CL', 'name': 'Espanhol (Chile)'},
                {'code': 'fr-FR', 'name': 'Francês (França)'},
                {'code': 'fr-CA', 'name': 'Francês (Canadá)'},
                {'code': 'fr-BE', 'name': 'Francês (Bélgica)'},
                {'code': 'fr-CH', 'name': 'Francês (Suíça)'},
                {'code': 'de-DE', 'name': 'Alemão (Alemanha)'},
                {'code': 'de-AT', 'name': 'Alemão (Áustria)'},
                {'code': 'de-CH', 'name': 'Alemão (Suíça)'},
                {'code': 'it-IT', 'name': 'Italiano (Itália)'},
                {'code': 'it-CH', 'name': 'Italiano (Suíça)'},
                {'code': 'ja-JP', 'name': 'Japonês'},
                {'code': 'zh-CN', 'name': 'Chinês (Simplificado, China)'},
                {'code': 'zh-TW', 'name': 'Chinês (Tradicional, Taiwan)'},
                {'code': 'zh-HK', 'name': 'Chinês (Hong Kong)'},
                {'code': 'ru-RU', 'name': 'Russo'},
                {'code': 'ar-SA', 'name': 'Árabe (Arábia Saudita)'},
                {'code': 'ar-EG', 'name': 'Árabe (Egito)'},
                {'code': 'ar-MA', 'name': 'Árabe (Marrocos)'},
                {'code': 'ko-KR', 'name': 'Coreano (Coreia do Sul)'},
                {'code': 'ko-KP', 'name': 'Coreano (Coreia do Norte)'},
                {'code': 'nl-NL', 'name': 'Holandês (Países Baixos)'},
                {'code': 'nl-BE', 'name': 'Holandês (Bélgica)'},
                {'code': 'sv-SE', 'name': 'Sueco (Suécia)'},
                {'code': 'sv-FI', 'name': 'Sueco (Finlândia)'},
                {'code': 'no-NO', 'name': 'Norueguês (Noruega)'},
                {'code': 'fi-FI', 'name': 'Finlandês'},
                {'code': 'pl-PL', 'name': 'Polonês'},
                {'code': 'tr-TR', 'name': 'Turco'},
                {'code': 'el-GR', 'name': 'Grego'},
                {'code': 'he-IL', 'name': 'Hebraico'},
                {'code': 'hi-IN', 'name': 'Hindi (Índia)'},
                {'code': 'id-ID', 'name': 'Indonésio'},
                {'code': 'th-TH', 'name': 'Tailandês'},
                {'code': 'vi-VN', 'name': 'Vietnamita'},
                {'code': 'uk-UA', 'name': 'Ucraniano'},
                {'code': 'cs-CZ', 'name': 'Tcheco'},
                {'code': 'sk-SK', 'name': 'Eslovaco'},
                {'code': 'sl-SI', 'name': 'Esloveno'},
                {'code': 'ro-RO', 'name': 'Romeno'},
                {'code': 'bg-BG', 'name': 'Búlgaro'},
                {'code': 'hu-HU', 'name': 'Húngaro'},
                {'code': 'et-EE', 'name': 'Estoniano'},
                {'code': 'lv-LV', 'name': 'Letão'},
                {'code': 'lt-LT', 'name': 'Lituano'},
                {'code': 'ga-IE', 'name': 'Irlandês'},
                {'code': 'cy-GB', 'name': 'Galês'},
                {'code': 'la', 'name': 'Latim'} # Exemplo sem região
            ]


            languages_to_add = []
            for lang_data in language_list_source:
                languages_to_add.append(
                    Language(Code=lang_data['code'], Name=lang_data['name'])
                )

            db.session.add_all(languages_to_add)

            # Commit para salvar os idiomas no banco
            db.session.commit()

            # Busca todos os idiomas que acabamos de criar para usar na criação de livros
            languages = db.session.query(Language).all()

            # --- 7. Clientes (5) ---
            clients = []
            for i in range(5):
                client_type = random.choice(['PF', 'PJ'])
                client_addr = addresses.pop()

                client = Client(
                    Type=client_type,
                    address=client_addr,
                    Phone=fake.phone_number(),
                    Email=fake.email()
                )
                db.session.add(client)
                db.session.flush() # Para pegar o client.idClient

                if client_type == 'PF':
                    client_fp = ClientFP(
                        idClient=client.idClient,
                        CPF=fake.cpf().replace('.','').replace('-',''),
                        FName=fake.first_name(),
                        MName=fake.first_name_male() if random.choice([True, False]) else None,
                        LName=fake.last_name(),
                        Birthdate=fake.date_of_birth(minimum_age=18, maximum_age=90)
                    )
                    db.session.add(client_fp)
                else:
                    client_jp = ClientJP(
                        idClient=client.idClient,
                        CNPJ=fake.cnpj().replace('.','').replace('/','').replace('-',''),
                        Name=fake.company(),
                        FantasyName=fake.company_suffix() if random.choice([True, False]) else None
                    )
                    db.session.add(client_jp)
                clients.append(client)

            db.session.commit() # Commit clientes

            # --- 8. Livros (Conceito) (20) ---
            books = []
            for i in range(20):

                # --- CORREÇÃO LÓGICA ---
                # 1. Primeiro, escolhemos a coleção (pode ser um objeto ou None)
                chosen_collection = random.choice(collections + [None]) if collections else None

                # 2. Agora criamos o livro
                book = Book(
                    ISBN=fake.isbn13().replace('-',''),
                    Title=f"Livro Título Fictício {i}",
                    idAuthor=random.choice(authors).idAuthor,
                    idPublisher=random.choice(publishers).idPublisher,
                    Language=random.choice(languages).idLanguage,

                    # 3. Atribuímos o ID se a coleção existir, senão atribuímos None
                    Collection=chosen_collection.idCollection if chosen_collection else None,

                    Edition=str(random.randint(1, 5))
                )
                books.append(book)

            db.session.add_all(books)
            db.session.commit() # Commit livros

            # --- 9. Livros Físicos (Exemplares) (Aprox 40) ---
            physical_books = []
            for book in books:
                # Cria 1 a 3 exemplares de cada livro
                for _ in range(random.randint(1, 3)):
                    pb = PhysicalBook(
                        ISBN=book.ISBN,
                        idBranch=random.choice(branches).idBranch,
                        Status='AVAILABLE' # Começam disponíveis
                    )
                    physical_books.append(pb)
            db.session.add_all(physical_books)
            db.session.commit() # Commit exemplares

            # --- 10. Empréstimos (4) ---

            # Empréstimo 1: Ativo
            loan1 = BookLoan(
                idPhysicalBook=physical_books[0].idPhysicalBook,
                idClient=clients[0].idClient,
                DueDate=datetime.utcnow() + timedelta(days=14)
            )
            physical_books[0].Status = 'BORROWED'

            # Empréstimo 2: Atrasado (Ativo)
            loan2 = BookLoan(
                idPhysicalBook=physical_books[1].idPhysicalBook,
                idClient=clients[1].idClient,
                BorrowedDate=datetime.utcnow() - timedelta(days=20),
                DueDate=datetime.utcnow() - timedelta(days=6) # Venceu há 6 dias
            )
            physical_books[1].Status = 'BORROWED'

            # Empréstimo 3: Devolvido
            loan3 = BookLoan(
                idPhysicalBook=physical_books[2].idPhysicalBook,
                idClient=clients[0].idClient,
                BorrowedDate=datetime.utcnow() - timedelta(days=30),
                DueDate=datetime.utcnow() - timedelta(days=16),
                ReturnDate=datetime.utcnow() - timedelta(days=15), # Devolveu 1 dia atrasado
                Status='RETURNED'
            )
            # (physical_books[2] continua AVAILABLE)

            # Empréstimo 4: Perdido
            loan4 = BookLoan(
                idPhysicalBook=physical_books[3].idPhysicalBook,
                idClient=clients[2].idClient,
                DueDate=datetime.utcnow() + timedelta(days=10),
                Status='LOST'
            )
            physical_books[3].Status = 'IN REPAIR' # Livro perdido vai para "reparo/análise"

            db.session.add_all([loan1, loan2, loan3, loan4])
            db.session.commit()

            # --- 11. Reservas (2) ---
            # Reservar os livros que estão emprestados (0 e 1)
            reserve1 = Reserve(
                ISBN=physical_books[0].ISBN,
                idBranch=physical_books[0].idBranch,
                idClient=clients[3].idClient # Cliente 3 reserva o livro do cliente 0
            )
            reserve2 = Reserve(
                ISBN=physical_books[1].ISBN,
                idBranch=physical_books[1].idBranch,
                idClient=clients[4].idClient # Cliente 4 reserva o livro do cliente 1
            )
            db.session.add_all([reserve1, reserve2])

            # Comita tudo
            db.session.commit()
            print(f">>> Banco de dados populado com sucesso!")
            print(f"    Criados {len(clients)} clientes, {len(books)} livros, {len(physical_books)} exemplares.")

        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao popular o banco: {e}")
            print(f"XXX Erro ao popular o banco: {e}")
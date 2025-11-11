from . import db
from .models import Author,Book, Branch, Client, Collection, Language, BookLoan, PhysicalBook, Publisher, Reserve, Address
import logging

def register_seed_command(app):
    """Register commands 'seed-db' for this application"""

    @app.cli.command("seed-db")
    def seed_db():
        """
        Seed database
        """
        try:
            # --- Limpa o banco (cuidado!) ---
            # Descomente se quiser limpar tudo antes de popular
            # db.session.query(Author).delete()
            # db.session.query(Address).delete()
            # ...

            # --- Criar Endereço ---
            addr1 = Address(Road="Rua Fictícia", Neighbourhood="Bairro", Number="123", City="Cidade", State="PR", ZipCode="12345-678")

            # --- Criar Editora ---
            pub1 = Publisher(Name="Editora Fantasia", CNPJ="11223344000155", address=addr1)

            # --- Criar Autor ---
            auth1 = Author(FName="João", LName="Silva")

            # --- Criar Idioma ---
            lang1 = Language(Code="pt-BR", Name="Português do Brasil")

            # Adiciona tudo na sessão
            db.session.add(addr1)
            db.session.add(pub1)
            db.session.add(auth1)
            db.session.add(lang1)

            # Comita no banco
            db.session.commit()
            print(">>> Banco de dados populado com sucesso!")

        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao popular o banco: {e}")
            print(f"XXX Erro ao popular o banco: {e}")
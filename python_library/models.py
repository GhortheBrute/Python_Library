from . import db
from sqlalchemy.orm import relationship
from sqlalchemy import DECIMAL, TIMESTAMP

class Language(db.Model):
    # Define o nome da tabela, (opcional, mas recomendado)
    __tablename__ = "Language"

    # Mapeia as colunas do seu ERD
    idLanguage = db.Column(db.Integer, primary_key=True)
    Code = db.Column(db.String(10), unique=True, nullable=False)
    Name = db.Column(db.String(100), nullable=False)

    # -- Relacionamento --
    books = db.relationship('Book', back_populates='language')

class Author(db.Model):
    __tablename__ = "Author"

    idAuthor = db.Column(db.Integer, primary_key=True)
    FName = db.Column(db.String(100), nullable=False)
    MName = db.Column(db.String(45), nullable=True)
    LName = db.Column(db.String(100), nullable=False)

    # -- Relacionamento --
    # Aqui está uma lista de livros ligados ao autor
    # 'back_populates' diz ao SQLAlchemy que este lado da relação
    # se conecta com o atributo 'author' no modelo 'book'
    books = db.relationship('Book', back_populates='author')

class Address(db.Model):
    __tablename__ = "Address"

    idAddress = db.Column(db.Integer, primary_key=True)
    Road = db.Column(db.String(255), nullable=False)
    Neighbourhood = db.Column(db.String(255), nullable=False)
    Number = db.Column(db.String(45), nullable=True)
    City = db.Column(db.String(45), nullable=False)
    State = db.Column(db.String(45), nullable=False)
    ZipCode = db.Column(db.String(9), nullable=False)
    Complement = db.Column(db.String(255), nullable=True)

    # -- Relacionamentos --
    publishers = db.relationship('Publisher', back_populates='address')
    branches = db.relationship('Branch', back_populates='address')
    clients = db.relationship('Client', back_populates='address')

class Publisher(db.Model):
    __tablename__ = "Publisher"

    idPublisher = db.Column(db.Integer, primary_key=True)
    CNPJ = db.Column(db.String(14), unique=True, nullable=False)
    Name = db.Column(db.String(100), nullable=False)

    # Exemplo de chave estrangeira
    idAddress = db.Column(db.Integer, db.ForeignKey('Address.idAddress'), nullable=False)

    # Atributo para aparecer em adição de novos livros
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # -- Relacionamento --
    books = db.relationship('Book', back_populates='publisher')
    address = db.relationship('Address', back_populates='publishers')

class Collection(db.Model):
    __tablename__ = "Collection"

    idCollection = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)

    # -- Relacionamento --
    books = db.relationship('Book', back_populates='collections')

class Client(db.Model):
    __tablename__ = "Client"
    idClient = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.Enum('PF','PJ'), nullable=False)
    idAddress = db.Column(db.Integer, db.ForeignKey('Address.idAddress'), nullable=False)
    Phone = db.Column(db.String(45), nullable=True)
    Email = db.Column(db.String(255), nullable=True, unique=True)

    # -- Status de Ativo
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    # -- Relacionamentos --
    address = db.relationship('Address', back_populates='clients')
    book_loans = db.relationship('BookLoan', back_populates='client')
    client_fp = db.relationship('ClientFP', back_populates='client', uselist=False)
    client_jp = db.relationship('ClientJP', back_populates='client', uselist=False)
    reserves = db.relationship('Reserve', back_populates='client')

class ClientFP(db.Model):
    __tablename__ = "ClientFP"
    idClient = db.Column(db.Integer, db.ForeignKey('Client.idClient'), primary_key=True)
    CPF = db.Column(db.String(11), unique=True, nullable=False)
    FName = db.Column(db.String(100), nullable=False)
    MName = db.Column(db.String(45), nullable=True)
    LName = db.Column(db.String(100), nullable=False)
    Birthdate = db.Column(db.Date, nullable=False)

    # -- Relacionamentos --
    client = db.relationship('Client', back_populates='client_fp')

class ClientJP(db.Model):
    __tablename__ = "ClientJP"
    idClient = db.Column(db.Integer, db.ForeignKey('Client.idClient'), primary_key=True)
    CNPJ = db.Column(db.String(14), unique=True, nullable=False)
    Name = db.Column(db.String(100), nullable=False)
    FantasyName = db.Column(db.String(100), nullable=True)

    # -- Relacionamentos --
    client = db.relationship('Client', back_populates='client_jp')

class Branch(db.Model):
    __tablename__ = "Branch"
    idBranch = db.Column(db.Integer, primary_key=True)
    BranchName = db.Column(db.String(100), nullable=False)
    idAddress = db.Column(db.Integer, db.ForeignKey('Address.idAddress'), nullable=False)

    # -- Relacionamento --
    address = db.relationship('Address', back_populates='branches')
    physical_books = db.relationship('PhysicalBook', back_populates='branch')
    reserves = db.relationship('Reserve', back_populates='branch')

class Book(db.Model):
    __tablename__ = "Book"
    ISBN = db.Column(db.String(13), primary_key=True)
    Title = db.Column(db.String(255), nullable=False)
    idAuthor = db.Column(db.Integer, db.ForeignKey('Author.idAuthor'), nullable=False)
    idPublisher = db.Column(db.Integer, db.ForeignKey('Publisher.idPublisher'), nullable=False)
    Edition = db.Column(db.String(45), nullable=True)
    Language = db.Column(db.Integer, db.ForeignKey('Language.idLanguage'), nullable=False)
    Collection = db.Column(db.Integer, db.ForeignKey('Collection.idCollection'), nullable=True)
    AgeRange = db.Column(db.Integer, nullable=True)
    Review = db.Column(DECIMAL(2,1), nullable=True)

    # -- Relacionamento --
    author = db.relationship('Author', back_populates='books')
    publisher = db.relationship('Publisher', back_populates='books')
    physical_books = db.relationship('PhysicalBook', back_populates='book')
    collections = db.relationship('Collection', back_populates='books')
    language = db.relationship('Language', back_populates='books')
    reserves = db.relationship('Reserve', back_populates='book')

class PhysicalBook(db.Model):
    __tablename__ = "PhysicalBook"
    idPhysicalBook = db.Column(db.Integer, primary_key=True)
    ISBN = db.Column(db.String(13), db.ForeignKey('Book.ISBN'), nullable=False)
    idBranch = db.Column(db.Integer, db.ForeignKey('Branch.idBranch'), nullable=False)
    Status = db.Column(db.Enum('AVAILABLE', 'BORROWED','IN REPAIR'), nullable=False, default='AVAILABLE')

    # -- Relacionamento --
    book = db.relationship('Book', back_populates='physical_books')
    branch = db.relationship('Branch', back_populates='physical_books')
    book_loans = db.relationship('BookLoan', back_populates='physical_book')

class BookLoan(db.Model):
    __tablename__ = "BookLoan"
    idBookLoan = db.Column(db.Integer, primary_key=True)
    idPhysicalBook = db.Column(db.Integer, db.ForeignKey('PhysicalBook.idPhysicalBook'), nullable=False)
    idClient = db.Column(db.Integer, db.ForeignKey('Client.idClient'), nullable=False)
    BorrowedDate = db.Column(TIMESTAMP, nullable=False, default=db.func.now())
    ReturnDate = db.Column(TIMESTAMP, nullable=True)
    DueDate = db.Column(db.Date, nullable=False)
    BorrowTimeSolicited = db.Column(db.Integer, nullable=True, default=14)
    Status = db.Column(db.Enum('ACTIVE', 'RETURNED','LOST'), nullable=False, default='ACTIVE')

    # -- Relacionamentos --
    physical_book = db.relationship('PhysicalBook', back_populates='book_loans')
    client = db.relationship('Client', back_populates='book_loans')

class Reserve(db.Model):
    __tablename__ = "Reserve"
    idReserve = db.Column(db.Integer, primary_key=True)
    ISBN = db.Column(db.String(13), db.ForeignKey('Book.ISBN'), nullable=False)
    idBranch = db.Column(db.Integer, db.ForeignKey('Branch.idBranch'), nullable=False)
    idClient = db.Column(db.Integer, db.ForeignKey('Client.idClient'), nullable=False)
    ReserveDate = db.Column(TIMESTAMP, nullable=False, default=db.func.now())

    # -- Relacionamentos --
    book = db.relationship('Book', back_populates='reserves')
    branch = db.relationship('Branch', back_populates='reserves')
    client = db.relationship('Client', back_populates='reserves')
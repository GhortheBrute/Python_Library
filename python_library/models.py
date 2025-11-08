from . import db

class Language(db.Model):
    # Define o nome da tabela, (opcional, mas recomendado)
    __tablename__ = "Language"

    # Mapeia as colunas do seu ERD
    idLanguage = db.Column(db.Integer, primary_key=True)
    Code = db.Column(db.String(10), unique=True, nullable=False)
    Name = db.Column(db.String(100), nullable=False)

class Author(db.Model):
    __tablename__ = "Author"

    idAuthor = db.Column(db.Integer, primary_key=True)
    FName = db.Column(db.String(100), nullable=False)
    MName = db.Column(db.String(45), nullable=True)
    LName = db.Column(db.String(100), nullable=False)

class Address(db.Model):
    __tablename__ = "Address"

    idAddress = db.Column(db.Integer, primary_key=True)
    Road = db.Column(db.String(255), nullable=False)
    Neighbourhood = db.Column(db.String(255), nullable=False)
    Number = db.Column(db.Integer, nullable=True)
    City = db.Column(db.String(45), nullable=False)
    State = db.Column(db.String(45), nullable=False)
    ZipCode = db.Column(db.String(9), nullable=False)
    Complement = db.Column(db.String(255), nullable=False)

class Publisher(db.Model):
    __tablename__ = "Publisher"

    idPublisher = db.Column(db.Integer, primary_key=True)
    CNPJ = db.Column(db.String(14), unique=True, nullable=False)
    Name = db.Column(db.String(100), nullable=False)

    # Exemplo de chave estrangeira
    idAddress = db.Column(db.Integer, db.ForeignKey('Address.idAddress'), nullable=False)

class Collection(db.Model):
    __tablename__ = "Collection"

    idCollection = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)

class Client(db.Model):
    __tablename__ = "Client"
    idClient = db.Column(db.Integer, primary_key=True)
    Type = db.Column(db.Enum('PF','PJ'), nullable=False)
    idAddress = db.Column(db.Integer, db.ForeignKey('Address.idAddress'), nullable=False)
    Phone = db.Column(db.String(45), nullable=False)
    Email = db.Column(db.String(255), nullable=False)

class ClientFP(db.Model):
    __tablename__ = "ClientFP"
    idClient = db.Column(db.Integer, db.ForeignKey('Client.idClient'), primary_key=True)
    CPF = db.Column(db.String(11), unique=True, nullable=False)
    FName = db.Column(db.String(100), nullable=False)
    MName = db.Column(db.String(45), nullable=False)
    LName = db.Column(db.String(100), nullable=False)
    Birthdate = db.Column(db.Date, nullable=False)

class ClientJP(db.Model):
    __tablename__ = "ClientJP"
    idClient = db.Column(db.Integer, db.ForeignKey('Client.idClient'), primary_key=True)
    CNPJ = db.Column(db.String(14), unique=True, nullable=False)
    Name = db.Column(db.String(100), nullable=False)
    FantasyName = db.Column(db.String(100), nullable=False)

class Branch(db.Model):
    __tablename__ = "Branch"
    idBranch = db.Column(db.Integer, primary_key=True)
    BranchName = db.Column(db.String(100), nullable=False)
    idAddress = db.Column(db.Integer, db.ForeignKey('Address.idAddress'), nullable=False)

class Book(db.Model):
    __tablename__ = "Book"
    ISBN = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    idAuthor = db.Column(db.Integer, db.ForeignKey('Author.idAuthor'), nullable=False)
    idPublisher = db.Column(db.Integer, db.ForeignKey('Publisher.idPublisher'), nullable=False)
    Edition = db.Column(db.String(45), nullable=True)
    Language = db.Column(db.Integer, db.ForeignKey('Language.idLanguage'), nullable=False)
    Collection = db.Column(db.Integer, db.ForeignKey('Collection.idCollection'), nullable=True)
    AgeRange = db.Column(db.Integer, nullable=True)
    Review = db.Column(db.Decimal(2,1), nullable=True)

class PhysicalBook(db.Model):
    __tablename__ = "PhysicalBook"
    idPhysicalBook = db.Column(db.Integer, primary_key=True)
    ISBN = db.Column(db.Integer, db.ForeignKey('Book.ISBN'), nullable=False)
    idBranch = db.Column(db.Integer, db.ForeignKey('Branch.idBranch'), nullable=False)
    Status = db.Column(db.Enum('AVAILABLE', 'BORROWED','IN REPAIR'), nullable=False, default='Available')

class BookLoan(db.Model):
    __tablename__ = "BookLoan"
    idBookLoan = db.Column(db.Integer, primary_key=True)
    idPhysicalBook = db.Column(db.Integer, db.ForeignKey('PhysicalBook.idPhysicalBook'), nullable=False)
    idClient = db.Column(db.Integer, db.ForeignKey('Client.idClient'), nullable=False)
    BorrowedDate = db.Column(db.Timestamp, nullable=False, default=db.func.now())
    ReturnDate = db.Column(db.Timestamp, nullable=True)
    DueDate = db.Column(db.Date, nullable=False)
    BorrowTimeSolicited = db.Column(db.Integer, nullable=True, default=14)
    Status = db.Column(db.Enum('ACTIVE', 'RETURNED','LOST'), nullable=False, default='ACTIVE')

class Reserve(db.Model):
    __tablename__ = "Reserve"
    idReserve = db.Column(db.Integer, primary_key=True)
    ISBN = db.Column(db.Integer, db.ForeignKey('Book.ISBN'), nullable=False)
    idBranch = db.Column(db.Integer, db.ForeignKey('Branch.idBranch'), nullable=False)
    idClient = db.Column(db.Integer, db.ForeignKey('Client.idClient'), nullable=False)
    ReserveDate = db.Column(db.Timestamp, nullable=False, default=db.func.now())
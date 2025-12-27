"""
Enunciado:
Desarrolla una API REST utilizando Flask que permita realizar operaciones básicas sobre una biblioteca
con dos modelos relacionados: Autores y Libros.
La API debe exponer los siguientes endpoints:

Autores:
1. `GET /authors`: Devuelve la lista completa de autores.
2. `POST /authors`: Agrega un nuevo autor. El cuerpo de la solicitud debe incluir un JSON con el campo "name".
3. `GET /authors/<author_id>`: Obtiene los detalles de un autor específico y su lista de libros.

Libros:
1. `GET /books`: Devuelve la lista completa de libros.
2. `POST /books`: Agrega un nuevo libro. El cuerpo de la solicitud debe incluir JSON con campos "title", "author_id", y "year" (opcional).
3. `DELETE /books/<book_id>`: Elimina un libro específico por su ID.
4. `PUT /books/<book_id>`: Actualiza la información de un libro existente. El cuerpo puede incluir "title" y/o "year".

Esta versión utiliza Flask-SQLAlchemy como ORM para persistir los datos en una base de datos SQLite.
"""

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Integer, BigInteger, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List


db = SQLAlchemy()

# Define aquí tus modelos
# Usa los mismos modelos que en el ejercicio anterior: Author y Book

class Author(db.Model):
    """
    Modelo de autor usando SQLAlchemy ORM
    Debe tener: id, name y una relación con los libros
    """
    # Define la tabla 'authors' con:
    # - __tablename__ para especificar el nombre de la tabla
    # - id: clave primaria autoincremental
    # - name: nombre del autor (obligatorio)
    # - Una relación con los libros usando db.relationship

    # copio mateixa estructura ej3b1
    __tablename__='authors'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable= False)

    # relació entre Authors i Books
    books: Mapped[List["Book"]] = relationship(back_populates='author')

    def to_dict(self):
        """Convierte el autor a un diccionario para la respuesta JSON"""
        # Implementa este método para devolver id y name
        # No incluyas la lista de libros para evitar recursión infinita
        return { 
                'id': self.id,
                'name': self.name
                }


class Book(db.Model):
    """
    Modelo de libro usando SQLAlchemy ORM
    Debe tener: id, title, year (opcional), author_id y relación con el autor
    """
    # Define la tabla 'books' con:
    # - __tablename__ para especificar el nombre de la tabla
    # - id: clave primaria autoincremental
    # - title: título del libro (obligatorio)
    # - year: año de publicación (opcional)
    # - author_id: clave foránea que relaciona con la tabla 'authors'
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(primary_key=True)
    title:  Mapped[str] = mapped_column(String(200), nullable= False)
    year: Mapped[int] = mapped_column(nullable=True)
    author_id = mapped_column(ForeignKey('authors.id'), nullable=False)

    # relació amb autors i books  many to many
    author:Mapped[Author] = relationship(back_populates='books')

    def to_dict(self):
        """Convierte el libro a un diccionario para la respuesta JSON"""
        # Implementa este método para devolver id, title, year y author_id
        return {
            'id': self.id,
            'title': self.title,
            'year': self.year,
            'author_id': self.author_id
            }

def create_app():
    """
    Crea y configura la aplicación Flask con SQLAlchemy
    """
    app = Flask(__name__)
    
    # Configuración de la base de datos SQLite en memoria
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Inicializa la base de datos con la aplicación
    db.init_app(app)
    
    # Crea todas las tablas en la base de datos
    with app.app_context():
        db.create_all()
    
    # Endpoints de Autores
    @app.route('/authors', methods=['GET'])
    def get_authors():
        """
        Devuelve la lista completa de autores
        """
        # Implementa este endpoint:
        # - Consulta todos los autores
        # - Convierte cada autor a diccionario usando to_dict()
        # - Devuelve la lista en formato JSON
        
        # obting llista (iterable) d'objected
        authors_list = db.session.execute(select(Author))

        # creo una llista de diccinaris amb els authors
        result = [x.to_dict() for x in authors_list.scalars()]
        return result

    @app.route('/authors', methods=['POST'])
    def add_author():
        """
        Agrega un nuevo autor
        El cuerpo de la solicitud debe incluir un JSON con el campo "name"
        """
        # Implementa este endpoint:
        # - Obtiene los datos JSON de la solicitud
        # - Crea un nuevo autor con el nombre proporcionado
        # - Lo guarda en la base de datos
        # - Devuelve el autor creado con código 201
        
        # miro si hi ha parametres a capcalera 
        data_json = request.get_json()
        author_name = data_json['name'] or None
        if author_name:
            new_author = Author(name=author_name)
            db.session.add(new_author)
            db.session.commit()
            return jsonify(new_author.to_dict()),201
        else:
            return jsonify({'error': 'No author passed'}),400


    @app.route('/authors/<int:author_id>', methods=['GET'])
    def get_author(author_id):
        """
        Obtiene los detalles de un autor específico y su lista de libros
        """
        # Implementa este endpoint:
        # - Busca el autor por ID (usa get_or_404 para gestionar el error 404)
        # - Devuelve los detalles del autor y su lista de libros
        
        author_object = db.get_or_404(Author,author_id)
        result = author_object.to_dict()
        result['books']=[x.to_dict() for x in author_object.books]
        return jsonify(result)

    # Endpoints de Libros
    @app.route('/books', methods=['GET'])
    def get_books():
        """
        Devuelve la lista completa de libros
        """
        # Implementa este endpoint:
        # - Consulta todos los libros
        # - Convierte cada libro a diccionario
        # - Devuelve la lista en formato JSON

        # consulto tota la llista de llibres
        book_list = db.session.execute(select(Book))

        # cada objecte Book el converteixo a diccionari i el poso en una llista
        return [x.to_dict() for x in book_list.scalars()]

    @app.route('/books', methods=['POST'])
    def add_book():
        """
        Agrega un nuevo libro
        El cuerpo de la solicitud debe incluir JSON con campos "title", "author_id", y "year" (opcional)
        """
        # Implementa este endpoint:
        # - Obtiene los datos JSON de la solicitud
        # - Crea un nuevo libro con título, autor_id y año (opcional)
        # - Lo guarda en la base de datos
        # - Devuelve el libro creado con código 201
        data_json = request.get_json()
        title = data_json['title'] or None
        year = data_json['year'] or  None
        author_id = data_json['author_id'] or None

        if author_id:
            author=db.get_or_404(Author, author_id)
        
        if title is None or author_id is None:
            return jsonify({f'error': 'Missing either book title or Author info in header: (title)-(author_id) {title} - {author_id}'}),400

        # Creo book object
        if year is None:
            new_book = Book(title=title, author_id=author_id)
        else:
            new_book = Book(title=title, year=year, author_id=author_id)
        
        # affegeixo llibre i faig commit
        db.session.add(new_book)
        db.session.commit()
        return jsonify(new_book.to_dict()),201

    @app.route('/books/<int:book_id>', methods=['GET'])
    def get_book(book_id):
        """
        Obtiene un libro específico por su ID
        """
        # Implementa este endpoint:
        # - Busca el libro por ID (usa get_or_404 para gestionar el error 404)
        # - Devuelve los detalles del libro

        # miro si hi ha un llibre amb book_id i si retorno 404
        book = db.get_or_404(Book, book_id)
        return jsonify(book.to_dict())

    @app.route('/books/<int:book_id>', methods=['DELETE'])
    def delete_book(book_id):
        """
        Elimina un libro específico por su ID
        """
        # Implementa este endpoint:
        # - Busca el libro por ID (usa get_or_404)
        # - Elimina el libro de la base de datos
        # - Devuelve respuesta vacía con código 204
        
        # obtinc objecte Book amb book_id i si no retorno un 404
        book_to_del =db.get_or_404(Book, book_id)
        db.session.delete(book_to_del)
        return jsonify({}),204


    @app.route('/books/<int:book_id>', methods=['PUT'])
    def update_book(book_id):
        """
        Actualiza la información de un libro existente
        El cuerpo puede incluir "title" y/o "year"
        """
        # Implementa este endpoint:
        # - Obtiene los datos JSON de la solicitud
        # - Busca el libro por ID (usa get_or_404)
        # - Actualiza los campos proporcionados (título y/o año)
        # - Guarda los cambios en la base de datos
        # - Devuelve el libro actualizado

        # obtinc objecte Book amb book_id o si no retorno 404
        book_to_update = db.get_or_404(Book, book_id)

        # obtinc els nous valors del header, json, valors = None si no existeixen
        params = request.get_json()
        title_new = params['title'] or None
        year_new = params['year'] or None

        # actualitzo camps
        if title_new:
            book_to_update.title = title_new
        if year_new:
            book_to_update.year = year_new

        # write changes to the DB
        db.session.commit()
        return book_to_update.to_dict()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5005)

"""
Enunciado:
En este ejercicio, crearás una API REST sencilla con validación de esquema JSON para los endpoints POST.
La validación de esquemas JSON asegura que los datos enviados por los clientes cumplan con la estructura
y requisitos esperados antes de procesarlos.

Tareas:
1. Implementar validación de esquema JSON para el endpoint POST /authors
   usando el archivo author_schema.json
2. Implementar validación de esquema JSON para el endpoint POST /books
   usando el archivo book_schema.json
3. Devolver errores apropiados cuando los datos enviados no cumplan con los esquemas

Requerimientos de error:
- Si los datos no cumplen con el esquema JSON, debes devolver un error HTTP 400 (Bad Request)
- Para el endpoint /books, si el autor_id no existe, debes devolver un error HTTP 404 (Not Found)
- Debes incluir mensajes claros que indiquen la naturaleza del error

Esta versión utiliza Flask-SQLAlchemy como ORM para persistir los datos en una base de datos SQLite
y la biblioteca jsonschema para la validación de los datos de entrada.
"""

import os
import json
from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate, ValidationError
from sqlalchemy import String, Integer, ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

# Configura la base de datos
db = SQLAlchemy()

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
    
    # utilitzo els mateixos dels exercicis anteriors
    __tablename__='authors'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable= False)

    # relació entre Authors i Books
    books: Mapped[List["Book"]] = relationship(back_populates='author')

    # class variable
    schema_validator = ""

    @classmethod
    def load_schema(cls):
        """Carga el esquema JSON para validar datos de autor"""
        # Implementa este método para cargar el esquema desde el archivo 'author_schema.json'.
        with open(os.path.dirname(__file__ )+ r'/author_schema.json') as file_handle:
            cls.schema_validator = json.load(file_handle)

    @classmethod
    def check_schema(cls, data):
        """Valida los datos contra el esquema JSON de autor"""
        # Implementa este método para validar los datos usando jsonschema.validate()
        try:
            validate(data,cls.schema_validator)
        except:
            return False
        else:
            return True

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
    
    # utilitzo el mateix que els dos exercicis anteriors
    __tablename__ = 'books'
    id: Mapped[int] = mapped_column(primary_key=True)
    title:  Mapped[str] = mapped_column(String(200), nullable= False)
    year: Mapped[int] = mapped_column(nullable=True)
    author_id = mapped_column(ForeignKey('authors.id'), nullable=False)

    # relació amb autors i books  many to many
    author:Mapped[Author] = relationship(back_populates='books')


    # class variable 
    schema_validator = ""

    @classmethod
    def load_schema(cls):
        """ Carga el esquema JSON para validar datos de libro """
        # Implementa este método para cargar el esquema desde el archivo 'book_schema.json'
        with open(os.path.dirname(__file__)+r'/book_schema.json') as file_handler:
            cls.schema_validator = json.load(file_handler)


    @classmethod
    def check_schema(cls, data):
        """Valida los datos contra el esquema JSON de libro"""
        # Implementa este método similar a Author.check_schema()
        try:
            validate(data,cls.schema_validator)
        except:
            return False
        else:
            return True
        

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

    Author.load_schema()
    Book.load_schema()
    
    # Crea todas las tablas en la base de datos
    with app.app_context():
        db.create_all()
    
    @app.route('/authors', methods=['POST'])
    def add_author():
        """
        Agrega un nuevo autor con validación de esquema JSON
        
        Implementa este endpoint para:
        1. Obtener los datos JSON de la solicitud
        2. Validar los datos usando el método Author.check_schema()
        3. Si la validación falla, devolver un error 400 con el mensaje de error
        4. Si la validación pasa, crear un nuevo autor con el nombre proporcionado
        5. Guardar el autor en la base de datos
        6. Devolver el autor creado con código 201
        
        Ejemplo de uso:
            POST /authors
            Content-Type: application/json
            
            {
                "name": "Gabriel García Márquez"
            }
            
        Respuesta exitosa:
            Status: 201 Created
            {
                "id": 1,
                "name": "Gabriel García Márquez"
            }
            
        Respuesta de error (si los datos no son válidos):
            Status: 400 Bad Request
            {
                "error": "Mensaje descriptivo del error de validación"
            }
        """
        # TODO: Implementa este endpoint según las instrucciones
        data_json = request.get_json()
        Author.load_schema()
        if not Author.check_schema(data_json):
            return jsonify({'error': 'Data Validation Error'}),400
        
        author_new = Author(name = data_json['name'])
        db.session.add(author_new)
        db.session.commit()

        return author_new.to_dict(),201


    @app.route('/books', methods=['POST'])
    def add_book():
        """
        Agrega un nuevo libro con validación de esquema JSON
        
        Implementa este endpoint para:
        1. Obtener los datos JSON de la solicitud
        2. Validar los datos usando el método Book.check_schema()
        3. Si la validación falla, devolver un error 400 con el mensaje de error
        4. Si la validación pasa, verificar que el author_id existe:
           - Buscar el autor en la base de datos
           - Si no existe, devolver un error 404 con mensaje adecuado
        5. Crear un nuevo libro con título, autor_id y año (si está presente)
        6. Guardar el libro en la base de datos
        7. Devolver el libro creado con código 201
        
        Ejemplo de uso:
            POST /books
            Content-Type: application/json
            
            {
                "title": "Cien años de soledad",
                "author_id": 1,
                "year": 1967
            }
            
        Respuesta exitosa:
            Status: 201 Created
            {
                "id": 1,
                "title": "Cien años de soledad",
                "author_id": 1,
                "year": 1967
            }
            
        Respuesta de error (si los datos no son válidos):
            Status: 400 Bad Request
            {
                "error": "Mensaje descriptivo del error de validación"
            }
            
        Respuesta de error (si el autor no existe):
            Status: 404 Not Found
            {
                "error": "No existe un autor con el id proporcionado"
            }
        """
        # TODO: Implementa este endpoint según las instrucciones
        data_json = request.get_json()
        Book.load_schema()
        if not Book.check_schema(data_json):
            return jsonify({'error': 'Data Validation Error'}),400
        
        # comprobo existencia autor
        # ATENCIÓ: get_or_404 no es pot fer servir, per cause dels tests
        autor_exists = db.session.get(Author,data_json['author_id'])
        if autor_exists is None:
            return jsonify({'error': 'Author does not exist'}),404

        # Miro si hi ha any en json            
        try:
            year_new = data_json['year']
        except:
            year_new = None


        book_new = Book(
            title=data_json['title'],
            year=year_new,
            author_id =data_json['author_id'])
        db.session.add(book_new)
        db.session.commit()

        return book_new.to_dict(),201

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)

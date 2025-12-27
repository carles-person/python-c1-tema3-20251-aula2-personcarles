"""
Enunciado:
En este ejercicio aprenderás a utilizar SQLAlchemy como ORM (Object-Relational Mapper)
independiente de cualquier framework web. SQLAlchemy es una biblioteca potente
que permite trabajar con bases de datos relacionales utilizando objetos de Python.

Tarea:
Implementa un sistema simple de gestión de biblioteca utilizando SQLAlchemy para:
1. Crear modelos para Libros y Autores con una relación entre ellos
2. Realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
3. Realizar consultas básicas y avanzadas

Este ejercicio se enfoca en SQLAlchemy Core y ORM sin depender de Flask u otro framework web.
"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, inspect, select, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, joinedload, Session, DeclarativeBase, Mapped, mapped_column
from typing import List
# Crea el motor de base de datos (usamos SQLite en memoria para simplificar)
engine = create_engine('sqlite:///:memory:', echo=True)

# Crea la clase Base para los modelos declarativos

# ATENCIO: Això esta obsolet desde versio 2.0 de SQL Alchemy
# Base = declarative_base()

# Nou mètode per fer una declaraative Base
class Base(DeclarativeBase):
    pass


# Define aquí tus modelos
# Debes crear al menos:
# 1. Un modelo Author (autor) con campos id, name (nombre) y una relación con Book
# 2. Un modelo Book (libro) con campos id, title (título), year (año, opcional) y una relación con Author

class Author(Base):
    # Define la tabla 'authors' con:
    # - __tablename__ para especificar el nombre de la tabla
    # - id: clave primaria autoincremental
    # - name: nombre del autor (obligatorio)
    # - Una relación con los libros (books) usando relationship --> check SQLAlchemy
    __tablename__ = 'authors'

    # creo els camps
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable= False)

    # relació entre Authors i Books
    books: Mapped[List["Book"]] = relationship(back_populates='author')

    def __repr__(self) -> str:
        return f'name: {self.id} - {self.name}'


class Book(Base):
    # Define la tabla 'books' con:
    # - __tablename__ para especificar el nombre de la tabla
    # - id: clave primaria autoincremental
    # - title: título del libro (obligatorio)
    # - year: año de publicación (opcional)
    # - author_id: clave foránea que relaciona con la tabla 'authors'
    # - Una relación con el autor usando relationship
    __tablename__ = 'books'
    #camps de la taula
    id: Mapped[int] = mapped_column(primary_key=True)
    title:  Mapped[str] = mapped_column(String(200), nullable= False)
    year: Mapped[int] = mapped_column(nullable=True)
    author_id = mapped_column(ForeignKey('authors.id'), nullable=False)

    # relació amb autors i books  many to many
    author:Mapped[Author] = relationship(back_populates='books')

    def __repr__(self) -> str:
        return f'{self.id}: title: {self.title}, {self.year}, by {self.author_id}'


# Función para configurar la base de datos
def setup_database():
    """Configura la base de datos y crea las tablas"""
    # Implementa la creación de tablas en la base de datos usando Base.metadata.create_all()
    Base.metadata.create_all(engine)
    


# Función para crear datos de ejemplo
def create_sample_data(session:Session):
    """Crea datos de ejemplo en la base de datos"""
    # Crea al menos dos autores
    # Crea al menos tres libros asociados a los autores
    # Añade todos los objetos a la sesión y haz commit
    
    # autors... creats a partir de la info dels tests
    author_list = [
        Author(name = 'Gabriel García Márquez'),
        Author(name = 'Isabel Allende')
    ]

    # afegeixo authors a la llista
    session.add_all(author_list)
    session.flush() # -> força assignació de IDs als autors

    # faig el mateix pels books... com ja he fet un commit dels autors, existeix un id
    book_list = [
        Book(title="Cien años de soledad", year=1967, author_id=author_list[0].id),
        Book(title="El amor en los tiempos del cólera", year=1985, author_id=author_list[0].id),
        Book(title="La casa de los espíritus", year=1982, author_id=author_list[1].id)
    ]

    session.add_all(book_list)
    session.commit() # força un commit i fes canvis permanents



# Funciones para operaciones CRUD
def create_book(session: Session, title, author_name, year=None):
    """
    Crea un nuevo libro con su autor
    Si el autor ya existe, se utiliza el existente
    """
    # Busca si ya existe un autor con ese nombre
    # Si no existe, crea un nuevo autor
    # Crea un nuevo libro asociado al autor
    # Añade y haz commit a la sesión
    # Retorna el libro creado

    # busco autor
    statement = select(Author.id).where(Author.name == author_name)
    author_id = session.scalars(statement).one_or_none()

    # si no existeix, aleshores creao un nout autor 
    if not author_id:
        author_new = Author(name=author_name)
        #commit per forçar id
        session.add(author_new)
        session.flush() # --> obting ID, pero encara canvi no persistent.
        author_id = author_new.id

    # creo nou llibre i affegeixo
    new_book = Book(
        title=title,
        year=year,
        author_id = author_id
    )

    session.add(new_book)

    # faig canvis permanents
    session.commit()

    return new_book


def get_all_books(session:Session):
    """Obtiene todos los libros con sus autores"""
    # Consulta todos los libros y carga también los autores (joinedload)
    # Retorna la lista de libros
    
    statement = select(Book).options(joinedload(Book.author))
    # retorno llista d'objectes Books
    return session.scalars(statement).all()




def get_book_by_id(session:Session, book_id):
    """Obtiene un libro específico por su ID"""
    # Busca un libro por su ID y retórnalo
    # Si no existe, retorna None
    
    statement = select(Book).where(Book.id == book_id)

    try:
        result = session.scalar(statement) # --> equivalent a scalars().one()
    except:
        # no ha trobat objecte
        return None
    else:
        return result


def update_book(session:Session, book_id, new_title=None, new_year=None):
    """Actualiza la información de un libro existente"""
    # Busca el libro por ID
    # Si existe, actualiza los campos que tienen nuevos valores
    # Haz commit a la sesión
    # Retorna el libro actualizado o None si no existe
    
    statement = (update(Book).where(Book.id == book_id).values(title=new_title,year=new_year))
    session.execute(statement)
    session.commit()

    return session.get(Book, book_id)



def delete_book(session:Session, book_id):
    """Elimina un libro de la base de datos"""
    # Busca el libro por ID
    # Si existe, elimínalo y haz commit
    
    statement = select(Book).where(Book.id == book_id)

    # busco llibre, si no existeix genera excepció y ja es pot tornar
    try:
        book_to_delete = session.scalar(statement)
    except:
        return
    else:
        session.delete(book_to_delete)
        session.commit()


def find_books_by_author(session:Session, author_name):
    """Busca libros por el nombre del autor"""
    # Consulta los libros uniendo (join) con la tabla de autores
    # Filtra por el nombre del autor
    # Retorna la lista de libros
    
    statement = select(Book).join(Author).where(Author.name == author_name)

    try:
        books_found = session.scalars(statement).all()
    
    except:
        # not found
        return []
    else:
        return books_found


# Función principal para demostrar el uso de SQLAlchemy
def main():
    """Función principal que demuestra el uso de SQLAlchemy"""
    # Crea un motor y una sesión

    session = Session(bind=engine)
    
    # Configura la base de datos
    setup_database()
    
    try:
        # Crea datos de ejemplo
        create_sample_data(session)
        
        # Demuestra las operaciones CRUD
        print("\n--- Todos los libros ---")
        books = get_all_books(session)
        for book in books:
            print(f"Libro: {book.title}, Año: {book.year}, Autor: {book.author.name}")
        
        print("\n--- Crear un nuevo libro ---")
        new_book = create_book(session, "Nuevo libro de ejemplo", "Autor de Prueba", 2025)
        print(f"Libro creado: {new_book.title} por {new_book.author.name}")
        
        print("\n--- Buscar libro por ID ---")
        book = get_book_by_id(session, 1)
        if book:
            print(f"Libro encontrado: {book.title} por {book.author.name}")
        
        print("\n--- Actualizar libro ---")
        updated_book = update_book(session, 1, new_title="Título Actualizado", new_year=2026)
        if updated_book:
            print(f"Libro actualizado: {updated_book.title}, Año: {updated_book.year}")
        
        print("\n--- Buscar libros por autor ---")
        author_books = find_books_by_author(session, "Autor de Prueba")
        for book in author_books:
            print(f"Libro: {book.title}, Año: {book.year}")
        
        print("\n--- Eliminar libro ---")
        delete_book(session, 2)
        print("Libro eliminado. Lista actualizada de libros:")
        for book in get_all_books(session):
            print(f"Libro: {book.title}, Autor: {book.author.name}")
    finally:
        # Cierra la sesión
        session.close()


if __name__ == "__main__":
    main()

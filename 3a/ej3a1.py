"""
Enunciado:
En este ejercicio aprenderás a utilizar la biblioteca sqlite3 de Python para trabajar
con bases de datos SQLite. SQLite es una base de datos liviana que no requiere un servidor
y almacena la base de datos completa en un solo archivo.

Tareas:
1. Conectar a una base de datos SQLite
2. Crear tablas usando SQL
3. Insertar, actualizar, consultar y eliminar datos
4. Manejar transacciones y errores

Este ejercicio se enfoca en las operaciones básicas de SQL desde Python sin utilizar un ORM.
"""

import sqlite3 as sql
import os

# Ruta de la base de datos (en memoria para este ejemplo)
# Para una base de datos en archivo, usar: 'biblioteca.db'
DB_PATH = ':memory:'
# DB_PATH = r'./db.sql'

def crear_conexion():
    """
    Crea y devuelve una conexión a la base de datos SQLite
    """
    # Implementa la creación de la conexión y retorna el objeto conexión -- objecte de memoria
    return sql.connect(DB_PATH)

def crear_tablas(conexion):
    """
    Crea las tablas necesarias para la biblioteca:
    - autores: id (entero, clave primaria), nombre (texto, no nulo)
    - libros: id (entero, clave primaria), titulo (texto, no nulo),
              anio (entero), autor_id (entero, clave foránea a autores.id)
    """
    # Implementa la creación de tablas usando SQL
    
    # Usa conexion.cursor() para crear un cursor y ejecutar comandos SQL
    cur = conexion.cursor()
    
    # creo taula autores
    cur.execute('CREATE TABLE autores (id INTEGER PRIMARY KEY AUTOINCREMENT,nombre TEXT NOT NULL)')
    
    # creo taula libros
    cur.execute('CREATE TABLE libros (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, anio INTEGER ,autor_id INTEGER, FOREIGN KEY(autor_id) REFERENCES autores(id))')
    

def insertar_autores(conexion, autores):
    """
    Inserta varios autores en la tabla 'autores'
    Parámetro autores: Lista de tuplas (nombre,)
    """
    # Implementa la inserción de autores usando SQL INSERT
    # Usa consultas parametrizadas para mayor seguridad

    SQL = 'INSERT INTO autores(nombre) VALUES(?)'
    cur = conexion.cursor()
    cur.executemany(SQL, autores)
    conexion.commit()

    return
    

def insertar_libros(conexion, libros):
    """
    Inserta varios libros en la tabla 'libros'
    Parámetro libros: Lista de tuplas (titulo, anio, autor_id)
    """
    # Implementa la inserción de libros usando SQL INSERT
    # Usa consultas parametrizadas para mayor seguridad
    SQL = 'INSERT INTO libros(titulo, anio, autor_id) VALUES(?,?,?)'
    cur = conexion.cursor()
    cur.executemany(SQL, libros)
    conexion.commit()

def consultar_libros(conexion):
    """
    Consulta todos los libros y muestra título, año y nombre del autor
    """
    # Implementa una consulta SQL JOIN para obtener libros con sus autores
    # Imprime los resultados formateados
    SQL = "SELECT  t1.titulo, t1.anio, t2.nombre FROM libros t1 LEFT JOIN autores t2 ON t1.autor_id = t2.id"

    cur = conexion.cursor()
    resultado = []
    for row in cur.execute(SQL):
        print(','.join([str(x) for x in row]))



def buscar_libros_por_autor(conexion, nombre_autor):
    """
    Busca libros por el nombre del autor
    """
    # Implementa una consulta SQL con WHERE para filtrar por autor
    # Retorna una lista de tuplas (titulo, anio)
    SQL= f'SELECT  t1.titulo, t1.anio  FROM libros t1 LEFT JOIN autores t2 ON t1.autor_id = t2.id WHERE t2.nombre="{nombre_autor}"'
    cur = conexion.cursor()
    cur.execute(SQL)
    resultado = cur.fetchall()
    return resultado


def actualizar_libro(conexion, id_libro, nuevo_titulo=None, nuevo_anio=None):
    """
    Actualiza la información de un libro existente
    """
    # Implementa la actualización usando SQL UPDATE
    # Solo actualiza los campos que no son None
    
    SQL_BASE = f'UPDATE libros SET ' 
    updated_fields=[]

    if nuevo_titulo:
        updated_fields.append(f'titulo="{nuevo_titulo}"')
    if nuevo_anio:
        updated_fields.append(f'anio={nuevo_anio}')

    if len(updated_fields)>0:
        SQL = SQL_BASE + ','.join(updated_fields) + f' WHERE id={id_libro}'
        cur=conexion.cursor()
        cur.execute(SQL)
        conexion.commit()

def eliminar_libro(conexion, id_libro):
    """
    Elimina un libro por su ID
    """
    # Implementa la eliminación usando SQL DELETE
    SQL = f'DELETE FROM libros WHERE id={id_libro}'
    cur=conexion.cursor()
    cur.execute(SQL)
    conexion.commit()


def ejemplo_transaccion(con:sql.Connection):
    """
    Demuestra el uso de transacciones para operaciones agrupadas
    """
    # Implementa una transacción que:
    # 1. Comience con conexion.execute("BEGIN TRANSACTION")
    # 2. Realice varias operaciones
    # 3. Si todo está bien, confirma con conexion.commit()
    # 4. En caso de error, revierte con conexion.rollback()

    con.execute('BEGIN TRANSACTION')
    new_authors = [('autor 1',), ('Autor 2',), ('Autor 3',)]
    new_books = [("book of one",2995,1),("book of two",1996,2), ("book of three",1997,3)]

    try:
        con.executemany('INSERT INTO autores(nombre) VALUES(?)', new_authors)
        con.executemany('INSERT INTO libros(titulo, anio, autor_id) VALUES(?,?,?)', new_books)

        # executa un commit si no hi ha error
        con.commit()

    except Exception as e:
        print(f'Error: {e}')
        print('ROLLING BACK changes')
        con.rollback()





    

if __name__ == "__main__":
    try:
        # Crear una conexión
        conexion = crear_conexion()

        print("Creando tablas...")
        crear_tablas(conexion)

        # Insertar autores
        autores = [
            ("Gabriel García Márquez",),
            ("Isabel Allende",),
            ("Jorge Luis Borges",)
        ]
        insertar_autores(conexion, autores)
        print("Autores insertados correctamente")

        # Insertar libros
        libros = [
            ("Cien años de soledad", 1967, 1),
            ("El amor en los tiempos del cólera", 1985, 1),
            ("La casa de los espíritus", 1982, 2),
            ("Paula", 1994, 2),
            ("Ficciones", 1944, 3),
            ("El Aleph", 1949, 3)
        ]
        insertar_libros(conexion, libros)
        print("Libros insertados correctamente")

        print("\n--- Lista de todos los libros con sus autores ---")
        consultar_libros(conexion)

        print("\n--- Búsqueda de libros por autor ---")
        nombre_autor = "Gabriel García Márquez"
        libros_autor = buscar_libros_por_autor(conexion, nombre_autor)
        print(f"Libros de {nombre_autor}:")
        for titulo, anio in libros_autor:
            print(f"- {titulo} ({anio})")

        print("\n--- Actualización de un libro ---")
        actualizar_libro(conexion, 1, nuevo_titulo="Cien años de soledad (Edición especial)")
        print("Libro actualizado. Nueva información:")
        consultar_libros(conexion)

        print("\n--- Eliminación de un libro ---")
        eliminar_libro(conexion, 6)  # Elimina "El Aleph"
        print("Libro eliminado. Lista actualizada:")
        consultar_libros(conexion)

        print("\n--- Demostración de transacción ---")
        ejemplo_transaccion(conexion)

    except sql.Error as e:
        print(f"Error de SQLite: {e}")
    finally:
        if conexion:
            conexion.close()
            print("\nConexión cerrada.")

            
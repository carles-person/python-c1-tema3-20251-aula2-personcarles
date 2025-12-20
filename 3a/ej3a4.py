"""
Enunciado:
En este ejercicio aprenderás a utilizar MongoDB con Python para trabajar
con bases de datos NoSQL. MongoDB es una base de datos orientada a documentos que
almacena datos en formato similar a JSON (BSON).

Tareas:
1. Conectar a una base de datos MongoDB
2. Crear colecciones (equivalentes a tablas en SQL)
3. Insertar, actualizar, consultar y eliminar documentos
4. Manejar transacciones y errores

Este ejercicio se enfoca en las operaciones básicas de MongoDB desde Python utilizando PyMongo.
"""

import subprocess
import time
import os
import sys
from typing import List, Tuple, Optional

import pymongo
from bson.objectid import ObjectId

# Configuración de MongoDB (la debes obtener de "docker-compose.yml"):
DB_NAME = "biblioteca"
MONGODB_PORT = 27017
MONGODB_HOST = "localhost"
MONGODB_USERNAME = "testuser"
MONGODB_PASSWORD = "testpass"

def verificar_docker_instalado() -> bool:
    """
    Verifica si Docker está instalado en el sistema y el usuario tiene permisos
    """
    try:
        # Verificar si docker está instalado
        result = subprocess.run(["docker", "--version"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
        if result.returncode != 0:
            return False

        # Verificar si docker-compose está instalado
        result = subprocess.run(["docker", "compose", "version"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
        if result.returncode != 0:
            return False

        # Verificar permisos de Docker
        result = subprocess.run(["docker", "ps"],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def iniciar_mongodb_docker() -> bool:
    """
    Inicia MongoDB usando Docker Compose
    """

    try:
        # Obtener la ruta al directorio actual donde está el docker-compose.yml
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Detener cualquier contenedor previo
        subprocess.run(
            ["docker", "compose", "down"],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        # Iniciar MongoDB con docker-compose
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            print(f"Error al iniciar MongoDB: {result.stderr}")
            return False

        # Dar tiempo para que MongoDB se inicie completamente
        time.sleep(5)
        return True

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar Docker Compose: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado: {e}")
        return False

def detener_mongodb_docker() -> None:
    """
    Detiene el contenedor de MongoDB
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(
            ["docker", "compose", "down"],
            cwd=current_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
    except Exception as e:
        print(f"Error al detener MongoDB: {e}")

def crear_conexion() -> pymongo.database.Database:
    """
    Crea y devuelve una conexión a la base de datos MongoDB
    """
    # Debes conectarte a la base de datos MongoDB usando PyMongo
    client = pymongo.MongoClient(f'mongodb://{MONGODB_USERNAME}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/')
    return client[DB_NAME]

def crear_colecciones(db: pymongo.database.Database) -> None:
    """
    Crea las colecciones necesarias para la biblioteca.
    En MongoDB, no es necesario definir el esquema de antemano,
    pero podemos crear índices para optimizar el rendimiento.
    """
    # Debes crear colecciones para 'autores' y 'libros'
    # 1. Crear colección de autores con índice por nombre
    # 2. Crear colección de libros con índices
    # drop collections if exists
    db.drop_collection('autores')
    db.drop_collection('libros')
    # recreate the collections
    autores=db.create_collection('autores')
    libros=db.create_collection('libros')
    autores.create_index('nombre', unique=True)
    libros.create_index('titulo')
    libros.create_index('anio')
    libros.create_index('autor_id')


def insertar_autores(db: pymongo.database.Database, autores: List[Tuple[str]]) -> List[str]:
    """
    Inserta varios autores en la colección 'autores'
    """
    # Debes realizar los siguientes pasos:
    # 1. Convertir las tuplas a documentos
    # 2. Insertar los documentos
    # 3. Devolver los IDs como strings
    autores_col = db['autores']
    doc_list = [ {'nombre': x[0]} for x in autores]
    result=autores_col.insert_many(doc_list)
    # Retorno list dels id insertats en format string
    return [str(_id) for _id in result.inserted_ids]

def insertar_libros(db: pymongo.database.Database, libros: List[Tuple[str, int, str]]) -> List[str]:
    """
    Inserta varios libros en la colección 'libros'
    """
    # Debes realizar los siguientes pasos:
    # 1. Convertir las tuplas a documentos
    # 2. Insertar los documentos
    # 3. Devolver los IDs como strings
    libros_col = db['libros']
    doc_list = [{'titulo': t, 'anio': y, 'autor_id': ObjectId(a) if isinstance(a,str) else a} for t,y,a in libros]
    result = libros_col.insert_many(doc_list)
    return [str(_id) for _id in result.inserted_ids]


def consultar_libros(db: pymongo.database.Database) -> None:
    """
    Consulta todos los libros y muestra título, año y nombre del autor
    """
    # Debes realizar los siguientes pasos:
    # 1. Realizar una agregación para unir libros con autores
    # 2. Mostrar los resultados
    libros_col = db['libros']
    agg_pipeline = []
    agg_pipeline.append({
        "$lookup": {
                "from": "autores",
                "localField": "autor_id",
                "foreignField": "_id",
                "as": "autor_mapping"
            }
    })
    agg_pipeline.append({
        "$unwind": "$autor_mapping"
    })

    agg_pipeline.append({
        "$project": {
            "titulo": 1,
            "anio": 1,
            "autor_nombre": "$autor_mapping.nombre"
        }
    })


    results = libros_col.aggregate(agg_pipeline) # selecciona tota la collection de libros amb autors
    for document in results:
        print(f'título: {document['titulo']}, año: {document['anio']}, autor: {document['autor_nombre']}')
        

def buscar_libros_por_autor(db: pymongo.database.Database, nombre_autor: str) -> List[Tuple[str, int]]:
    """
    Busca libros por el nombre del autor
    """
    # Debes realizar los siguientes pasos:
    # 1. Primero encontrar el autor y buscar todos los libros del autor
    # 2. Convertir a lista de tuplas (titulo, anio)
    libros_col = db['libros']

    autor_id = db['autores'].find_one({"nombre": nombre_autor})

    # si esta buit retorna empty
    result = []
    if not autor_id:
        return result

    # buscar els autor_id amb oject_id = autor_id
    for doc in libros_col.find({'autor_id':ObjectId(autor_id['_id'])}):
        result.append((doc['titulo'],doc['anio']))
 
    return result



def actualizar_libro(
        db: pymongo.database.Database,
        id_libro: str,
        nuevo_titulo: Optional[str]=None,
        nuevo_anio: Optional[int]=None
) -> bool:
    """
    Actualiza la información de un libro existente
    """
    # Debes realizar los siguientes pasos:
    # 1. Crear diccionario de actualización
    # 2. Realizar la actualización
    libros_col = db['libros']
    search_dict={'_id': ObjectId(id_libro)}
    newvals_dict={}
    if nuevo_titulo:
        newvals_dict['titulo'] = nuevo_titulo
    if nuevo_anio:
        newvals_dict['anio'] = nuevo_anio
    
    if not newvals_dict:
        # res a actualitzar
        return True
    
    res=libros_col.update_one(search_dict,{'$set': newvals_dict})

    if res.modified_count > 0:
        return True
    else:
        return False


def eliminar_libro(
        db: pymongo.database.Database,
        id_libro: str
) -> bool:
    """
    Elimina un libro por su ID
    """
    # Debes eliminar el libro con el ID proporcionado
    libros_col = db['libros']
    res=libros_col.delete_one({'_id': ObjectId(id_libro)})
    if res.deleted_count>0:
        return True
    else:
        return False

def ejemplo_transaccion(db: pymongo.database.Database) -> bool:
    """
    Demuestra el uso de operaciones agrupadas
    """
    # Debes realizar los siguientes pasos:
    # 1. Insertar un nuevo autor
    # 2. Insertar dos libros del autor
    # Intentar limpiar los datos en caso de error

    # Ejemplo sacado de MongoDB manual
    try:
        def add_autor_libro_callback(session):
            autcol = session.client.biblioteca.autores
            libcol = session.client.biblioteca.libros

            autcol.insert_one({"nombre": 'autor 4'})
            libcol.insert_one({'titulo':'titulo libro de 4', 'anio': 2013, 'autor':'autor 4'})
            libcol.insert_one({'titulo':'titulo libro de 4 (segunda edición)', 'anio': 2014, 'autor':'autor 4'})
                
        # creación de la session
        with db.client.start_session() as session:
            session.with_transaction(add_autor_libro_callback)

            # with session.start_transaction(
            #     read_concern=ReadConcern('snapshot'),
            #     write_concern=WriteConcern(w='majority'),
            #     read_preference=ReadPreference.PRIMARY
            # ):
            session.commit_transaction()
        return True
    except Exception as err:
        print(f'{err}')
        return False


if __name__ == "__main__":
    mongodb_proceso = None
    db = None

    try:
        # Verificar si Docker está instalado
        if not verificar_docker_instalado():
            print("Error: Docker no está instalado o no está disponible en el PATH.")
            print("Por favor, instala Docker y asegúrate de que esté en tu PATH.")
            sys.exit(1)

        # Iniciar MongoDB usando Docker
        print("Iniciando MongoDB con Docker...")
        if not iniciar_mongodb_docker():
            print("No se pudo iniciar MongoDB. Asegúrate de tener los permisos necesarios.")
            sys.exit(1)

        print("MongoDB iniciado correctamente.")

        # Crear una conexión
        print("Conectando a MongoDB...")
        db = crear_conexion()
        print("Conexión establecida correctamente.")

        # TODO: Implementar el código para probar las funciones

        # crear autores
        autores_lista = [
            ('autor 1',),
            ('autor 2',),
            ('autor 3',)
        ]

        # para passar lost test ... se tiene que poner esta lista de autores
        autores_lista= [
            ("Gabriel García Márquez",),
            ("Isabel Allende",),
            ("Jorge Luis Borges",)
        ]

        crear_colecciones(db)
        ids = insertar_autores(db,autores_lista)
        print(f'----------\nAutores Insertados con id:\n{ids}')

        # create a list named "libros_lista" containing tuples like (title, year, author). title is a random title of max 60 characters, year is between 1990 and 2015 and authors is limited to "autor 1", "autor 2" and "autor 3"
        # libros_lista = [
        #     ('libro 1', 2024, ids[0]),
        #     ('libro 2', 1995, ids[2]),
        #     ('libro 33', 2002, ids[1]),
        #     ('libro 24', 1999, ids[2]),
        #     ('libro 14', 2020, ids[0])
        # ]

        # Para pasar lost test... se tiene que poner esta lista
        libros_lista = [
            ("Cien años de soledad", 1967, ids[0]),
            ("El amor en los tiempos del cólera", 1985, ids[0]),
            ("La casa de los espíritus", 1982, ids[1]),
            ("Paula", 1994, ids[1]),
            ("Ficciones", 1944, ids[2]),
            ("El Aleph", 1949, ids[2])
        ]

        ids = insertar_libros(db,libros_lista)
        print(f'----------\nLibros Insertados con id:\n{ids}')

        # listar todos los autores y todos los libros
        consultar_libros(db)

        # buscar libro por autor
        resultado = buscar_libros_por_autor(db,autores_lista[1][0])
        print(f'------------\nLibros de autor:\n{resultado}')

        # actualizar libro
        print('ACTUALIZAR LIBROS')
        print('Lista antes de Actualizar')
        consultar_libros(db)

        resultado = buscar_libros_por_autor(db,autores_lista[0][0])
        actualizar_libro(db,resultado[0]['_id'],'el titulo 2 del nuevo titulo', nuevo_anio=9999)

        print('UPDATE: Nueva lista de libros')
        consultar_libros(db)

        # borrar libro
        print('BORRANDO LIBROS')
        print('Lista antes de Borrar')
        consultar_libros(db)

        resultado = buscar_libros_por_autor(db, autores_lista[1][0])
        eliminar_libro(db,resultado[0]['_id'])

        print('DELETE: Nueva lista de libros')
        consultar_libros(db)

        # Transacción
        print('---------\nTRANSACCION')
        ejemplo_transaccion(db)
        consultar_libros(db)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        # Cerrar la conexión a MongoDB
        if db is not None:
            db.client.close()
            print("\nConexión a MongoDB cerrada.")

        # Detener el proceso de MongoDB si lo iniciamos nosotros
        if mongodb_proceso:
            print("Deteniendo MongoDB...")
            detener_mongodb_docker()

            print("MongoDB detenido correctamente.")

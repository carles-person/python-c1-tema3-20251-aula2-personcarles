"""
Enunciado:
En este ejercicio aprenderás a trabajar con bases de datos SQLite existentes.
Aprenderás a:
1. Conectar a una base de datos SQLite existente
2. Convertir datos de SQLite a formatos compatibles con JSON
3. Extraer datos de SQLite a pandas DataFrame

El archivo ventas_comerciales.db contiene datos de ventas con tablas relacionadas
que incluyen productos, vendedores, regiones y ventas. Debes analizar estos datos
usando diferentes técnicas.
"""

import sqlite3
import pandas as pd
import os
import json
from typing import List, Dict, Any, Optional, Tuple, Union

# Ruta a la base de datos SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), 'ventas_comerciales.db')

def conectar_bd() -> sqlite3.Connection:
    """
    Conecta a una base de datos SQLite existente

    Returns:
        sqlite3.Connection: Objeto de conexión a la base de datos SQLite
    """
    # Implementa aquí la conexión a la base de datos:
    # 1. Verifica que el archivo de base de datos existe
    # 2. Conecta a la base de datos
    # 3. Configura la conexión para que devuelva las filas como diccionarios (opcional)
    # 4. Retorna la conexión
    
    if os.path.exists(DB_PATH):
        try:
            con:sqlite3.connection = sqlite3.connect(DB_PATH)
            return con
        except:
            return None
    else:
        return None

def convertir_a_json(conexion: sqlite3.Connection) -> Dict[str, List[Dict[str, Any]]]:
    """
    Convierte los datos de la base de datos en un objeto compatible con JSON

    Args:
        conexion (sqlite3.Connection): Conexión a la base de datos SQLite

    Returns:
        Dict[str, List[Dict[str, Any]]]: Diccionario con todas las tablas y sus registros
        en formato JSON-serializable
    """
    # Implementa aquí la conversión de datos a formato JSON:
    # 1. Crea un diccionario vacío para almacenar el resultado
    # 2. Obtén la lista de tablas de la base de datos
    # 3. Para cada tabla:
    #    a. Ejecuta una consulta SELECT * FROM tabla
    #    b. Obtén los nombres de las columnas
    #    c. Convierte cada fila a un diccionario (clave: nombre columna, valor: valor celda)
    #    d. Añade el diccionario a una lista para esa tabla
    # 4. Retorna el diccionario completo con todas las tablas
    
    result = {}

    tablas = conexion.execute('SELECT name FROM sqlite_master WHERE type="table";').fetchall()

    for tabla in tablas:
        val_list = []
        cur = conexion.cursor()
        values= cur.execute(f'SELECT * from {tabla[0]};').fetchall()
        # després query, cur.description conté nom de les columnes
        col_names = [x[0] for x in cur.description]

        for value in values:
            rows={}
            for key,value in zip(col_names,value):
                rows[key] = value
            
            val_list.append(rows)

        result[tabla[0]] = val_list
    
    return result
        




def convertir_a_dataframes(conexion: sqlite3.Connection) -> Dict[str, pd.DataFrame]:
    """
    Extrae los datos de la base de datos a DataFrames de pandas

    Args:
        conexion (sqlite3.Connection): Conexión a la base de datos SQLite

    Returns:
        Dict[str, pd.DataFrame]: Diccionario con DataFrames para cada tabla y para
        consultas combinadas relevantes
    """
    # Implementa aquí la extracción de datos a DataFrames:
    # 1. Crea un diccionario vacío para los DataFrames
    # 2. Obtén la lista de tablas de la base de datos
    # 3. Para cada tabla, crea un DataFrame usando pd.read_sql_query
    # 4. Añade consultas JOIN para relaciones importantes:
    #    - Ventas con información de productos
    #    - Ventas con información de vendedores
    #    - Vendedores con regiones
    # 5. Retorna el diccionario con todos los DataFrames
    result = {}

    tablas = conexion.execute('SELECT name FROM sqlite_master WHERE type="table";').fetchall()

    for tabla in tablas:
        val_list = []
        df = pd.read_sql_query(f'SELECT * from {tabla[0]};',conexion)
        result[tabla[0]] = df

    # JOIN ventas productos
    str_sql = "SELECT t1.*, t2.* FROM ventas t1 LEFT JOIN productos t2 on t1.producto_id = t2.id"
    result['ventas_productos'] = pd.read_sql_query(str_sql,conexion)
    # JOIN ventas vendedores
    str_sql = "SELECT t1.*, t2.* FROM ventas t1 LEFT JOIN vendedores t2 on t1.vendedor_id = t2.id"
    result['ventas_vendedores']=pd.read_sql_query(str_sql,conexion)
    # JOIN ventas regiones
    str_sql = "SELECT t1.*, t2.* FROM vendedores t1 LEFT JOIN regiones t2 on t1.region_id = t2.id"
    result['vendedores_regiones']=pd.read_sql_query(str_sql,conexion)
    
        
        
    return result

if __name__ == "__main__":
    try:
        # Conectar a la base de datos existente
        print("Conectando a la base de datos...")
        conexion = conectar_bd()
        print("Conexión establecida correctamente.")

        # Verificar la conexión mostrando las tablas disponibles
        cursor = conexion.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()
        print(f"\nTablas en la base de datos: {[t[0] for t in tablas]}")

        # Conversión a JSON
        print("\n--- Convertir datos a formato JSON ---")
        datos_json = convertir_a_json(conexion)
        print("Estructura JSON (ejemplo de una tabla):")
        if datos_json:
            # Muestra un ejemplo de la primera tabla encontrada
            primera_tabla = list(datos_json.keys())[0]
            print(f"Tabla: {primera_tabla}")
            if datos_json[primera_tabla]:
                print(f"Primer registro: {datos_json[primera_tabla][0]}")

            # Opcional: guardar los datos en un archivo JSON
            # ruta_json = os.path.join(os.path.dirname(__file__), 'ventas_comerciales.json')
            # with open(ruta_json, 'w', encoding='utf-8') as f:
            #     json.dump(datos_json, f, ensure_ascii=False, indent=2)
            # print(f"Datos guardados en {ruta_json}")

        # Conversión a DataFrames de pandas
        print("\n--- Convertir datos a DataFrames de pandas ---")
        dataframes = convertir_a_dataframes(conexion)
        if dataframes:
            print(f"Se han creado {len(dataframes)} DataFrames:")
            for nombre, df in dataframes.items():
                print(f"- {nombre}: {len(df)} filas x {len(df.columns)} columnas")
                print(f"  Columnas: {', '.join(df.columns.tolist())}")
                print(f"  Vista previa:\n{df.head(2)}\n")

    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conexion' in locals() and conexion:
            conexion.close()
            print("\nConexión cerrada.")

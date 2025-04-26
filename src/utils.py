"""
Utilidades para la generación de esquemas y datos
"""

from typing import Dict
from src.database import MariaDBManager


def export_sql_to_file(queries: Dict[str, str], output_file: str):
    """
    Exporta las consultas SQL a un archivo

    Args:
        queries: Diccionario con nombres de tablas como claves y consultas como valores
        output_file: Ruta del archivo de salida
    """
    with open(output_file, "w") as f:
        for table_name, query in queries.items():
            f.write(f"-- Inserciones para la tabla {table_name}\n")
            f.write(query)
            f.write("\n\n")
    print(f"SQL exportado a {output_file}")

def export_sql_to_mariadb(queries: Dict[str, str], host: str, user: str, password: str, database: str, port: int = 3306):
    """
    Exporta las consultas SQL directamente a una base de datos MariaDB

    Args:
        queries: Diccionario con nombres de tablas como claves y consultas como valores
        host: Host de la base de datos
        user: Usuario de la base de datos
        password: Contraseña del usuario
        database: Nombre de la base de datos
        port: Puerto de la base de datos (por defecto 3306)
    """
    try:
        with MariaDBManager(host, user, password, database, port) as db:
            db.execute_queries(queries)
        print(f"SQL exportado exitosamente a la base de datos {database}")
    except Exception as e:
        print(f"Error al exportar a MariaDB: {str(e)}")
        raise

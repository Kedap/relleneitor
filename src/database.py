"""
Módulo para manejar operaciones de base de datos MariaDB
"""

import mariadb
from typing import Dict
import logging
from contextlib import contextmanager

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MariaDBManager:
    def __init__(self, host: str = "localhost", user: str = "root", 
                 password: str = "", database: str = "relleneitor_db", 
                 port: int = 3306):
        """
        Inicializa el gestor de base de datos MariaDB

        Args:
            host: Host de la base de datos (por defecto: localhost)
            user: Usuario de la base de datos (por defecto: root)
            password: Contraseña del usuario (por defecto: "")
            database: Nombre de la base de datos (por defecto: relleneitor_db)
            port: Puerto de la base de datos (por defecto: 3306)
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    @contextmanager
    def get_connection(self):
        """
        Context manager para obtener una conexión a la base de datos
        """
        try:
            conn = mariadb.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            logger.info(f"Conexión exitosa a la base de datos {self.database}")
            yield conn
        except mariadb.Error as e:
            logger.error(f"Error al conectar a la base de datos: {e}")
            raise
        finally:
            if 'conn' in locals():
                conn.close()
                logger.info("Conexión cerrada")

    def execute_queries(self, queries: Dict[str, str]) -> None:
        """
        Ejecuta un conjunto de queries en la base de datos

        Args:
            queries: Diccionario con nombres de tablas como claves y consultas como valores
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                for table_name, query in queries.items():
                    logger.info(f"Ejecutando queries para la tabla {table_name}")
                    cursor.execute(query)
                conn.commit()
                logger.info("Todas las queries se ejecutaron exitosamente")
            except mariadb.Error as e:
                logger.error(f"Error al ejecutar queries: {e}")
                conn.rollback()
                raise
            finally:
                cursor.close()

    def __enter__(self):
        """Método para usar con el contexto 'with'"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Método para usar con el contexto 'with'"""
        pass  # La conexión se cierra automáticamente en el context manager 
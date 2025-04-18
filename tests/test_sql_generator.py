"""
Tests para el generador de consultas SQL
"""

import os
import tempfile
import pytest
from faker import Faker
from src.schema import Table, Column, ForeignKey, registry
from src.generator import generate_insert_query, generate_insert_queries_in_order
from src.utils import export_sql_to_file
from src.test_utils import generate_testing_schemas, generate_custom_testing_sql

faker = Faker()


@pytest.fixture
def simple_table():
    """Fixture que proporciona una tabla simple para testing"""
    return Table(
        name="test_table",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(name="name", type="VARCHAR(50)", faker_provider="first_name"),
            Column(name="email", type="VARCHAR(100)", faker_provider="email"),
        ],
    )


@pytest.fixture
def related_tables():
    """Fixture que proporciona dos tablas relacionadas para testing"""
    # Asegurarse de limpiar el registro global
    registry.tables = {}

    # Tabla de usuarios
    users_table = Table(
        name="users",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(name="name", type="VARCHAR(50)", faker_provider="name"),
            Column(name="email", type="VARCHAR(100)", faker_provider="email"),
        ],
    )

    # Registrar la tabla de usuarios primero
    registry.register(users_table)

    # Tabla de posts que depende de users
    posts_table = Table(
        name="posts",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(name="title", type="VARCHAR(100)", faker_provider="sentence"),
            Column(
                name="user_id",
                type="INTEGER",
                foreign_key=ForeignKey(
                    column="user_id", references_table="users", references_column="id"
                ),
            ),
            Column(name="content", type="TEXT", faker_provider="paragraph"),
        ],
    )

    registry.register(posts_table)

    return {users_table: 5, posts_table: 5}


def test_generate_insert_query(simple_table):
    """Test para verificar que genera consultas INSERT válidas"""
    # Generar consulta para 5 filas
    sql = generate_insert_query(simple_table, 5)

    # Verificaciones básicas
    assert sql.startswith(f"INSERT INTO {simple_table.name}")
    assert "VALUES" in sql
    assert sql.endswith(";")

    # Verificar que contiene 5 conjuntos de valores
    # Contar los paréntesis de apertura de cada conjunto de valores
    value_count = (
        sql.count("(") - 1
    )  # Restamos 1 por el paréntesis de los nombres de columnas
    assert value_count == 5


def test_foreign_key_relationship(related_tables):
    """Test para verificar que las relaciones de llaves foráneas son válidas"""

    # Generar consultas en el orden correcto
    queries = generate_insert_queries_in_order(related_tables)

    # Debe generar consultas para ambas tablas
    assert len(queries) == 2
    assert "users" in queries
    assert "posts" in queries

    # La consulta de users debe aparecer antes en el diccionario ordenado
    keys = list(queries.keys())
    assert keys.index("users") < keys.index("posts")

    # Extraer los valores de ID de usuarios generados
    users_sql = queries["users"]
    user_ids = extract_ids_from_sql(users_sql)

    # Extraer los user_id de los posts
    posts_sql = queries["posts"]
    post_user_ids = []
    for line in posts_sql.split("\n"):
        if line.startswith("("):
            # El user_id es el tercer valor en la tupla
            values = parse_sql_values(line)
            if len(values) >= 3:
                user_id = values[2].strip()
                # Eliminar comillas si existen
                if user_id.startswith("'") and user_id.endswith("'"):
                    user_id = user_id[1:-1]
                post_user_ids.append(user_id)

    for user_id in post_user_ids:
        assert user_id in user_ids, f"El ID de usuario {user_id} no es válido."

    # Asegurarse de que los IDs de usuario sean únicos
    assert len(user_ids) == len(set(user_ids)), "Los IDs de usuario no son únicos."


def test_generate_testing_schemas():
    """Test para verificar la generación de esquemas de testing"""
    schemas = generate_testing_schemas()

    # Verificar que se generan suficientes tablas
    assert len(schemas) >= 5

    # Verificar la presencia de tablas importantes
    table_names = list(schemas.keys())
    assert "usuarios" in table_names
    assert "articulos" in table_names
    assert "comentarios" in table_names

    # Verificar que cada elemento es una tupla (Table, int)
    for table_name, (table, num_rows) in schemas.items():
        assert isinstance(table, Table)
        assert isinstance(num_rows, int)
        assert table.name == table_name


def test_custom_testing_sql():
    """Test para verificar la generación de SQL personalizado para testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = os.path.join(temp_dir, "test_custom.sql")

        tables_config = [
            # (nombre_tabla, [(nombre_columna, tipo, faker_provider)], num_filas)
            (
                "productos",
                [
                    ("id", "INTEGER", "random_int"),
                    ("nombre", "VARCHAR(50)", "word"),
                    ("precio", "DECIMAL", "random_int(min=10,max=1000)"),
                ],
                5,
            ),
            (
                "categorias",
                [("id", "INTEGER", "random_int"), ("nombre", "VARCHAR(30)", "word")],
                3,
            ),
            (
                "productos_categorias",
                [
                    ("id", "INTEGER", "random_int"),
                    ("producto_id", "INTEGER", None),  # FK
                    ("categoria_id", "INTEGER", None),  # FK
                ],
                8,
            ),
        ]

        # Relaciones entre tablas
        relationships = [
            ("productos_categorias", "producto_id", "productos", "id"),
            ("productos_categorias", "categoria_id", "categorias", "id"),
        ]

        result_file = generate_custom_testing_sql(
            tables_config=tables_config,
            output_file=output_file,
            relationships=relationships,
        )

        assert os.path.exists(result_file)

        with open(result_file, "r") as f:
            content = f.read()
            assert "-- Inserciones para la tabla productos" in content
            assert "-- Inserciones para la tabla categorias" in content
            assert "-- Inserciones para la tabla productos_categorias" in content

            assert "INSERT INTO" in content
            assert "VALUES" in content


def test_export_sql_to_file():
    """Test para verificar la exportación de SQL a archivos"""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = os.path.join(temp_dir, "test_export.sql")

        test_queries = {
            "tabla1": "INSERT INTO tabla1 (id, nombre) VALUES (1, 'test');",
            "tabla2": "INSERT INTO tabla2 (id, valor) VALUES (1, 100);",
        }

        export_sql_to_file(test_queries, output_file)

        assert os.path.exists(output_file)

        with open(output_file, "r") as f:
            content = f.read()
            assert "-- Inserciones para la tabla tabla1" in content
            assert "-- Inserciones para la tabla tabla2" in content
            assert "INSERT INTO tabla1" in content
            assert "INSERT INTO tabla2" in content


def extract_ids_from_sql(sql):
    """Extrae los IDs (primer campo) de una consulta SQL"""
    ids = []
    for line in sql.split("\n"):
        if line.startswith("("):
            # Extraer el primer valor (ID) de la tupla
            id_value = line.split(",")[0].strip("(").strip()
            # Eliminar comillas si existen
            if id_value.startswith("'") and id_value.endswith("'"):
                id_value = id_value[1:-1]
            ids.append(id_value)
    return ids


def parse_sql_values(values_line):
    """
    Analiza una línea de valores SQL para extraer cada valor individual
    respetando las comillas, etc.
    """
    # Eliminar los paréntesis externos
    values_str = values_line.strip().strip("(),")

    result = []
    current = ""
    in_quotes = False

    for char in values_str:
        if char == "'" and (len(current) == 0 or current[-1] != "\\"):
            in_quotes = not in_quotes
            current += char
        elif char == "," and not in_quotes:
            result.append(current.strip())
            current = ""
        else:
            current += char

    if current:
        result.append(current.strip())

    return result

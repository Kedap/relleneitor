"""
Ejemplo de generación de datos para un sistema de ventas con múltiples tablas relacionadas
"""

from src.schema import Table, Column, ForeignKey
from src.generator import generate_insert_queries_in_order
from src.utils import MariaDBManager, export_sql_to_file
import random


def saldo_provider():
    return f"{random.uniform(0.00,1000000.00)}"


def limite_credito_provider():
    return f"{random.uniform(0.00,3000000.00)}"


def descuento_provider():
    return f"{random.uniform(0,1)}"


def create_ventas_schema():
    """
    Crea el esquema de la base de datos del sistema de ventas
    """
    # Tabla de clientes
    clientes = Table(
        name="clientes",
        columns=[
            Column(
                "numero_cliente",
                "INTEGER",
                is_primary_key=True,
                primary_key_autoincrement=True,
            ),
            Column("direccion_envio", "TEXT", faker_provider="address"),
            Column("saldo", "DECIMAL", custom_provider=saldo_provider),
            Column(
                "limite_credito", "DECIMAL", custom_provider=limite_credito_provider
            ),
            Column("descuento", "DECIMAL", custom_provider=descuento_provider),
        ],
    )

    # Tabla de fabricas
    fabricas = Table(
        name="fabricas",
        columns=[
            Column(
                "numero_fabrica",
                "INTEGER",
                is_primary_key=True,
                primary_key_autoincrement=True,
            ),
            Column("telefono_contacto", "PHONE", faker_provider="phone_number"),
        ],
    )

    # Tabla de artículos
    articulos = Table(
        name="articulos",
        columns=[
            Column(
                "numero_articulo",
                "INTEGER",
                is_primary_key=True,
                primary_key_autoincrement=True,
            ),
            Column(
                "id_proveedor",
                "INTEGER",
                foreign_key=ForeignKey("id_proveedor", "fabricas", "numero_fabrica"),
            ),
            Column("existencias", "INTEGER", faker_provider="random_digit_not_null"),
            Column("fabricas_descripcion", "TEXT", faker_provider="company"),
        ],
    )

    # Tabla de pedidos
    pedidos = Table(
        name="pedidos",
        columns=[
            Column(
                "id_pedido",
                "INTEGER",
                is_primary_key=True,
                primary_key_autoincrement=True,
            ),
            Column(
                "numero_cliente",
                "INTEGER",
                foreign_key=ForeignKey("numero_cliente", "clientes", "numero_cliente"),
            ),
            Column("direccion_envio", "TEXT", faker_provider="address"),
            Column("fecha_pedido", "DATE", faker_provider="date"),
            Column(
                "articulo_pedido",
                "INTEGER",
                foreign_key=ForeignKey(
                    "articulo_pedido", "articulos", "numero_articulo"
                ),
            ),
            Column("cantidad", "INTEGER", faker_provider="random_digit_not_null"),
        ],
    )

    return [clientes, fabricas, articulos, pedidos]


def main():
    # Crear el esquema
    tables = create_ventas_schema()

    # Definir cuántas filas generar para cada tabla
    rows_per_table = {
        tables[0]: 10,
        tables[1]: 10,
        tables[2]: 10,
        tables[3]: 10,
    }

    # Generar las queries
    queries = generate_insert_queries_in_order(rows_per_table)
    export_sql_to_file(queries, "pedidos.sql")

    # Crear instancia de MariaDBManager
    db = MariaDBManager(
        database="pedidos_encargos", user="kedapdb", password="12345678"
    )

    # Exportar a MariaDB
    try:
        db.execute_queries(queries)
        print("Datos generados y exportados exitosamente a la base de datos")
    except Exception as e:
        print(f"Error al exportar datos: {str(e)}")


if __name__ == "__main__":
    main()

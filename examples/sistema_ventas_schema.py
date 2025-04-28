"""
Ejemplo de generación de datos para un sistema de ventas con múltiples tablas relacionadas
"""

from src.schema import Table, Column, ForeignKey
from src.generator import generate_insert_queries_in_order
from src.utils import MariaDBManager
from typing import List, Tuple
import random


def _categoria_provider() -> str:
    """Genera una categoría aleatoria con su descripción."""
    categorias: List[Tuple[str, str]] = [
        ("Electrónica", "Productos electrónicos y dispositivos tecnológicos"),
        ("Ropa", "Prendas de vestir para todas las edades y estilos"),
        ("Alimentos", "Productos alimenticios y comestibles"),
        ("Hogar", "Artículos para el hogar y decoración"),
        ("Deportes", "Equipamiento y accesorios deportivos"),
        ("Juguetes", "Juguetes y juegos para todas las edades"),
        ("Libros", "Libros y material de lectura"),
        ("Música", "Instrumentos musicales y accesorios"),
        ("Cine", "Películas y material audiovisual"),
        ("Jardinería", "Herramientas y productos para jardinería")
    ]
    
    categoria, descripcion = random.choice(categorias)
    return f"'{categoria}'"


def _descripcion_categoria_provider() -> str:
    """Genera la descripción correspondiente a la categoría seleccionada."""
    categorias: List[Tuple[str, str]] = [
        ("Electrónica", "Productos electrónicos y dispositivos tecnológicos"),
        ("Ropa", "Prendas de vestir para todas las edades y estilos"),
        ("Alimentos", "Productos alimenticios y comestibles"),
        ("Hogar", "Artículos para el hogar y decoración"),
        ("Deportes", "Equipamiento y accesorios deportivos"),
        ("Juguetes", "Juguetes y juegos para todas las edades"),
        ("Libros", "Libros y material de lectura"),
        ("Música", "Instrumentos musicales y accesorios"),
        ("Cine", "Películas y material audiovisual"),
        ("Jardinería", "Herramientas y productos para jardinería")
    ]
    
    categoria, descripcion = random.choice(categorias)
    return f"'{descripcion}'"


def create_ventas_schema():
    """
    Crea el esquema de la base de datos del sistema de ventas
    """
    # Tabla de teléfonos de proveedores
    telefono_proveedor = Table(
        name="telefono_proveedor",
        columns=[
            Column("id", "INTEGER", is_primary_key=True, primary_key_autoincrement=True),
            Column("casa", "TEXT", faker_provider="phone_number"),
            Column("movil", "TEXT", faker_provider="phone_number"),
            Column("oficina", "TEXT", faker_provider="phone_number"),
            Column("personal", "TEXT", faker_provider="phone_number"),
        ],
    )

    # Tabla de proveedores
    proveedores = Table(
        name="proveedores",
        columns=[
            Column("rut", "INTEGER", is_primary_key=True, primary_key_autoincrement=True),
            Column("nombre", "TEXT", faker_provider="company"),
            Column("direccion", "TEXT", faker_provider="address"),
            Column(
                "telefono",
                "INTEGER",
                foreign_key=ForeignKey("telefono", "telefono_proveedor", "id"),
            ),
            Column("pagina_web", "TEXT", faker_provider="url"),
        ],
    )

    # Tabla de categorías
    categorias = Table(
        name="categorias",
        columns=[
            Column("id_categoria", "INTEGER", is_primary_key=True, primary_key_autoincrement=True),
            Column("nombre", "TEXT", custom_provider=_categoria_provider),
            Column("descripcion", "TEXT", custom_provider=_descripcion_categoria_provider),
        ],
    )

    # Tabla de productos
    productos = Table(
        name="productos",
        columns=[
            Column("id_producto", "INTEGER", is_primary_key=True, primary_key_autoincrement=True),
            Column("nombre", "TEXT", faker_provider="product_name"),
            Column("precio_actual", "DECIMAL(10,2)", faker_provider="random_int"),
            Column("stock", "INTEGER", faker_provider="random_int"),
            Column(
                "categoria",
                "INTEGER",
                foreign_key=ForeignKey("categoria", "categorias", "id_categoria"),
            ),
            Column(
                "proveedor",
                "INTEGER",
                foreign_key=ForeignKey("proveedor", "proveedores", "rut"),
            ),
        ],
    )

    # Tabla de teléfonos de clientes
    telefono_cliente = Table(
        name="telefono_cliente",
        columns=[
            Column("id", "INTEGER", is_primary_key=True, primary_key_autoincrement=True),
            Column("casa", "TEXT", faker_provider="phone_number"),
            Column("movil", "TEXT", faker_provider="phone_number"),
            Column("oficina", "TEXT", faker_provider="phone_number"),
            Column("personal", "TEXT", faker_provider="phone_number"),
        ],
    )

    # Tabla de clientes
    clientes = Table(
        name="clientes",
        columns=[
            Column("rut", "INTEGER", is_primary_key=True, primary_key_autoincrement=True),
            Column("nombre", "TEXT", faker_provider="name"),
            Column("direccion", "TEXT", faker_provider="address"),
            Column(
                "telefono",
                "INTEGER",
                foreign_key=ForeignKey("telefono", "telefono_cliente", "id"),
            ),
        ],
    )

    # Tabla de ventas
    ventas = Table(
        name="ventas",
        columns=[
            Column("id_venta", "INTEGER", is_primary_key=True, primary_key_autoincrement=True),
            Column("fecha", "DATE", faker_provider="date"),
            Column(
                "cliente",
                "INTEGER",
                foreign_key=ForeignKey("cliente", "clientes", "rut"),
            ),
            Column("cantidad", "INTEGER", faker_provider="random_int"),
            Column(
                "producto",
                "INTEGER",
                foreign_key=ForeignKey("producto", "productos", "id_producto"),
            ),
            Column("subtotal", "DECIMAL(10,2)", faker_provider="random_int"),
            Column("descuento", "DECIMAL(10,2)", faker_provider="random_int"),
            Column("monto_final", "DECIMAL(10,2)", faker_provider="random_int"),
        ],
    )

    return [
        telefono_proveedor,
        proveedores,
        categorias,
        productos,
        telefono_cliente,
        clientes,
        ventas,
    ]


def main():
    # Crear el esquema
    tables = create_ventas_schema()

    # Definir cuántas filas generar para cada tabla
    rows_per_table = {
        tables[0]: 20,  # 20 teléfonos de proveedores
        tables[1]: 15,  # 15 proveedores
        tables[2]: 10,  # 10 categorías
        tables[3]: 100,  # 100 productos
        tables[4]: 50,  # 50 teléfonos de clientes
        tables[5]: 40,  # 40 clientes
        tables[6]: 200,  # 200 ventas
    }

    # Generar las queries
    queries = generate_insert_queries_in_order(rows_per_table)

    # Crear instancia de MariaDBManager
    db = MariaDBManager(database="ventas", user="kedapdb", password="12345678")

    # Exportar a MariaDB
    try:
        db.execute_queries(queries)
        print("Datos generados y exportados exitosamente a la base de datos")
    except Exception as e:
        print(f"Error al exportar datos: {str(e)}")


if __name__ == "__main__":
    main()

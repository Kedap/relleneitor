"""
Tests específicos para las funcionalidades de llaves foráneas
"""
import pytest
import re
from src.schema import Table, Column, ForeignKey, registry, TableRegistry
from src.generator import generate_insert_query, generate_insert_queries_in_order, _generate_foreign_key_value
from src.test_utils import create_related_schemas_example

@pytest.fixture
def clear_registry():
    """Fixture para limpiar el registro global antes de cada test"""
    registry.tables = {}
    return registry

@pytest.fixture
def complex_schema(clear_registry):
    """Fixture para crear un esquema complejo con múltiples relaciones"""
    return create_related_schemas_example()

def test_table_registry():
    """Test para verificar que el registro de tablas funciona correctamente"""
    test_registry = TableRegistry()
    
    table1 = Table(
        name="tabla1",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(name="nombre", type="VARCHAR(50)", faker_provider="name")
        ]
    )
    
    table2 = Table(
        name="tabla2",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(name="tabla1_id", type="INTEGER", 
                  foreign_key=ForeignKey(
                      column="tabla1_id",
                      references_table="tabla1",
                      references_column="id"
                  ))
        ]
    )
    
    test_registry.register(table1)
    test_registry.register(table2)
    
    # Verificar que las tablas están registradas
    assert "tabla1" in test_registry.tables
    assert "tabla2" in test_registry.tables
    assert test_registry.get("tabla1") == table1
    assert test_registry.get("tabla2") == table2

def test_automatic_primary_key():
    """Test para verificar que se marca automáticamente la primera columna como PK"""
    # Crear una tabla sin especificar primary_key
    table = Table(
        name="test_auto_pk",
        columns=[
            Column(name="id", type="INTEGER"),
            Column(name="nombre", type="VARCHAR(50)")
        ]
    )
    
    # Verificar que la primera columna se marcó como PK
    assert table.primary_key == "id"
    assert table.columns[0].is_primary_key == True
    assert table.columns[1].is_primary_key == False

def test_explicit_primary_key():
    """Test para verificar que se respeta la PK explícita"""
    # Crear una tabla especificando primary_key
    table = Table(
        name="test_explicit_pk",
        columns=[
            Column(name="id", type="INTEGER"),
            Column(name="codigo", type="VARCHAR(20)")
        ],
        primary_key="codigo"
    )
    
    # Verificar que se usó la PK especificada
    assert table.primary_key == "codigo"
    assert table.columns[0].is_primary_key == False
    assert table.columns[1].is_primary_key == True

def test_store_and_retrieve_values(clear_registry):
    """Test para verificar el almacenamiento y recuperación de valores en tablas"""
    table = Table(
        name="test_values",
        columns=[
            Column(name="id", type="INTEGER"),
            Column(name="nombre", type="VARCHAR(50)")
        ]
    )
    
    table.store_generated_value("id", "1")
    table.store_generated_value("id", "2")
    table.store_generated_value("nombre", "'Test1'")
    table.store_generated_value("nombre", "'Test2'")
    
    id_values = table.get_generated_values("id")
    nombre_values = table.get_generated_values("nombre")
    
    assert len(id_values) == 2
    assert "1" in id_values
    assert "2" in id_values
    
    assert len(nombre_values) == 2
    assert "Test1" in nombre_values
    assert "Test2" in nombre_values

def test_ordering_by_dependencies(complex_schema, clear_registry):
    """Test para verificar que las tablas se ordenan correctamente según sus dependencias"""
    # Generar consultas en el orden correcto
    queries = generate_insert_queries_in_order(complex_schema)
    
    # Verificar el orden de las tablas (categorias debe ir antes que productos, etc.)
    order_list = list(queries.keys())
    
    # Verificar que las tablas padres van antes que las hijas
    assert order_list.index("categorias") < order_list.index("productos")
    assert order_list.index("clientes") < order_list.index("pedidos")
    assert order_list.index("pedidos") < order_list.index("detalles_pedido")
    assert order_list.index("productos") < order_list.index("detalles_pedido")

def test_foreign_key_validity(complex_schema, clear_registry):
    """Test para verificar que las llaves foráneas son válidas"""
    # Generar consultas en el orden correcto
    queries = generate_insert_queries_in_order(complex_schema)
    
    # Extraer IDs de clientes
    cliente_ids = extract_ids_from_sql(queries["clientes"])
    
    # Extraer IDs de pedidos y sus clientes asociados
    pedido_data = extract_fk_from_sql(queries["pedidos"], 1)  # cliente_id está en la posición 1
    
    # Verificar que todos los cliente_id en pedidos existen en clientes
    for _, cliente_id in pedido_data:
        assert cliente_id in cliente_ids

    # Extraer IDs de pedidos
    pedido_ids = [pedido_id for pedido_id, _ in pedido_data]
    
    # Extraer IDs de productos
    producto_ids = extract_ids_from_sql(queries["productos"])
    
    # Extraer datos de detalles_pedido
    detalle_pedido_lines = queries["detalles_pedido"].split("\n")
    for line in detalle_pedido_lines:
        if line.startswith("("):
            values = parse_sql_values(line)
            if len(values) >= 3:  # Al menos id, pedido_id, producto_id
                pedido_id = values[1]
                producto_id = values[2]
                
                # Verificar que las referencias son válidas
                assert pedido_id in pedido_ids
                assert producto_id in producto_ids

def test_error_on_invalid_foreign_key(clear_registry):
    """Test para verificar que se lanza un error cuando una FK referencia una tabla inexistente"""
    # Tabla con FK a una tabla que no existe
    invalid_table = Table(
        name="invalid_relation",
        columns=[
            Column(name="id", type="INTEGER"),
            Column(
                name="nonexistent_id", 
                type="INTEGER",
                foreign_key=ForeignKey(
                    column="nonexistent_id",
                    references_table="nonexistent_table",
                    references_column="id"
                )
            )
        ]
    )
    
    # Debería lanzar una excepción cuando intente generar datos
    with pytest.raises(ValueError):
        generate_insert_query(invalid_table, 3)

# Funciones auxiliares para extraer y analizar los datos de SQL

def extract_ids_from_sql(sql):
    """Extrae los IDs (primer campo) de una consulta SQL"""
    ids = []
    for line in sql.split("\n"):
        if line.startswith("("):
            # Extraer el primer valor (ID) de la tupla
            id_value = line.split(",")[0].strip("(").strip()
            ids.append(id_value)
    return ids

def extract_fk_from_sql(sql, fk_position):
    """Extrae la columna ID y una columna FK de una consulta SQL"""
    data = []
    for line in sql.split("\n"):
        if line.startswith("("):
            values = parse_sql_values(line)
            if len(values) > fk_position:
                id_value = values[0]
                fk_value = values[fk_position]
                data.append((id_value, fk_value))
    return data

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
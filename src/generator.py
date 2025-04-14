from faker import Faker
from typing import List, Dict, Any, Optional
from src.schema import Table, Column, ForeignKey, registry
import random
from datetime import datetime

faker = Faker()

def generate_insert_query(table: Table, num_rows: int) -> str:
    """
    Generar una consulta INSERT para una tabla dada

    Args:
        table: El esquema de la tabla
        num_rows: Número de filas a generar

    Devuelve:
        Cadena que contiene una única sentencia SQL INSERT con varias filas
    """
    # Registrar la tabla en el registro global si aún no está registrada
    if table.name not in registry.tables:
        registry.register(table)
        
    columns = table.columns
    column_names = [column.name for column in columns]
    
    value_rows = []
    
    # Antes de generar filas, verificar todas las llaves foráneas que no tengan datos
    for column in columns:
        if column.foreign_key and not registry.get_foreign_key_values(column.foreign_key):
            raise ValueError(f"La tabla '{column.foreign_key.references_table}' debe generarse antes que '{table.name}' "
                           f"ya que '{column.name}' hace referencia a '{column.foreign_key.references_column}'")
    
    for _ in range(num_rows):
        values = []
        
        for column in columns:
            value = None
            
            # Si es una llave foránea, usar un valor de la tabla referenciada
            if column.foreign_key:
                value = _generate_foreign_key_value(column.foreign_key)
            else:
                if column.faker_provider:
                    value = _get_value_from_provider(column.faker_provider)
                else:
                    value = _infer_value_from_type(column.type)
            
            # Almacenar el valor generado para posible uso como llave foránea
            table.store_generated_value(column.name, value)
            values.append(value)
        
        # Formatear como una tupla para SQL
        row_values = f"({', '.join(values)})"
        value_rows.append(row_values)
    
    # Crear una sentencia INSERT con múltiples conjuntos de valores
    query = f"INSERT INTO {table.name} ({', '.join(column_names)}) VALUES \n"
    query += ",\n".join(value_rows) + ";"
    
    return query

def _generate_foreign_key_value(foreign_key: ForeignKey) -> str:
    """
    Genera un valor válido para una llave foránea
    
    Args:
        foreign_key: Definición de la llave foránea
        
    Devuelve:
        Un valor válido que existe en la tabla referenciada
    """
    values = registry.get_foreign_key_values(foreign_key)
    
    if not values:
        raise ValueError(f"No se encontraron valores para la llave foránea en la tabla '{foreign_key.references_table}'")
    
    # Seleccionar un valor aleatorio de la tabla referenciada
    value = random.choice(values)
    
    # Formatear el valor adecuadamente para SQL
    if isinstance(value, str) and not value.startswith("'"):
        return f"'{value}'"
    return str(value)

def generate_insert_queries_in_order(tables_and_rows: Dict[Table, int]) -> Dict[str, str]:
    """
    Genera consultas INSERT para múltiples tablas, respetando el orden de las dependencias de llaves foráneas
    
    Args:
        tables_and_rows: Diccionario de tablas y número de filas a generar para cada una
        
    Devuelve:
        Diccionario con nombres de tablas como claves y consultas INSERT como valores
    """
    # Ordenar las tablas basado en sus dependencias
    ordered_tables = _order_tables_by_dependencies(list(tables_and_rows.keys()))
    
    # Generar consultas en el orden correcto
    queries = {}
    for table in ordered_tables:
        num_rows = tables_and_rows[table]
        queries[table.name] = generate_insert_query(table, num_rows)
    
    return queries

def _order_tables_by_dependencies(tables: List[Table]) -> List[Table]:
    """
    Ordena las tablas basándose en sus dependencias de llaves foráneas
    Las tablas sin dependencias van primero
    """
    # Registrar todas las tablas primero
    for table in tables:
        registry.register(table)
    
    result = []
    visited = set()
    
    def visit(table):
        if table.name in visited:
            return
        
        # Encontrar dependencias
        deps = []
        for column in table.columns:
            if column.foreign_key and column.foreign_key.references_table != table.name:  # Evitar auto-referencias
                for t in tables:
                    if t.name == column.foreign_key.references_table:
                        deps.append(t)
        
        # Visitar dependencias primero
        for dep in deps:
            visit(dep)
        
        visited.add(table.name)
        result.append(table)
    
    # Visitar cada tabla
    for table in tables:
        visit(table)
        
    return result

def _get_value_from_provider(provider: str) -> str:
    """Obtener un valor de un provider faker específico"""
    # Dividir el provider para manejar parámetros como "random_int(min=1,max=100)"
    if "(" in provider:
        provider_name, params_str = provider.split("(", 1)
        params_str = params_str.rstrip(")")
        if provider_name == "random_int":
            params = dict(param.split("=") for param in params_str.split(","))
            min_val = int(params.get("min", 1))
            max_val = int(params.get("max", 1000))
            return str(faker.random_int(min=min_val, max=max_val))
    else:
        # Usar getattr para llamar al método del provider dinámicamente
        try:
            provider_method = getattr(faker, provider)
            return _format_value(provider_method())
        except AttributeError:
            return f"'unknown_provider:{provider}'"

def _infer_value_from_type(column_type: str) -> str:
    """Infer an appropriate Faker provider based on column type"""
    column_type = column_type.upper()
    
    if column_type in ("INTEGER", "INT", "SMALLINT", "BIGINT", "TINYINT"):
        return str(faker.random_int(min=0, max=1000))
    
    elif column_type in ("DECIMAL", "NUMERIC", "FLOAT", "REAL", "DOUBLE"):
        return str(round(random.uniform(0.0, 1000.0), 2))
    
    elif column_type in ("TEXT", "VARCHAR", "CHAR", "CLOB"):
        max_chars = 100  # Default
        if "(" in column_type:  # Como cuando es VARCHAR(50)
            try:
                size = int(column_type.split("(")[1].split(")")[0])
                max_chars = size
            except (IndexError, ValueError):
                pass
        return f"'{faker.text(max_nb_chars=max_chars)}'"
    
    elif column_type in ("BOOLEAN", "BOOL"):
        return str(faker.boolean()).lower()
    
    elif column_type == "DATE":
        return f"'{faker.date()}'"
    elif column_type in ("DATETIME", "TIMESTAMP"):
        return f"'{faker.date_time().strftime('%Y-%m-%d %H:%M:%S')}'"
    elif column_type == "TIME":
        return f"'{faker.time()}'"
    
    elif column_type == "EMAIL" or "EMAIL" in column_type:
        return f"'{faker.email()}'"
    elif column_type == "NAME" or "NAME" in column_type:
        return f"'{faker.name()}'"
    elif column_type == "URL" or "URL" in column_type:
        return f"'{faker.url()}'"
    elif column_type == "IP" or "IPADDRESS" in column_type:
        return f"'{faker.ipv4()}'"
    elif "PHONE" in column_type:
        return f"'{faker.phone_number()}'"
    elif "ADDRESS" in column_type:
        return f"'{faker.address().replace('\n', ', ')}'"
    
    elif column_type in ("BLOB", "BINARY", "VARBINARY"):
        return f"X'{faker.hexify('?' * 10)}'"
    
    else:
        return f"'Tipo desconocido:{column_type}'"

def _format_value(value) -> str:
    """Formatear un valor para incluir en SQL"""
    if value is None:
        return "NULL"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, datetime):
        return f"'{value.strftime('%Y-%m-%d %H:%M:%S')}'"
    else:
        # Escapar comillas simples para SQL
        return f"'{str(value).replace('\'', '\'\'')}'"
            
            
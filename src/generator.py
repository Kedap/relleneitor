from faker import Faker
from typing import List
from src.schema import Table, Column
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
    columns = table.columns
    column_names = [column.name for column in columns]
    
    value_rows = []
    
    for _ in range(num_rows):
        values = []
        
        for column in columns:
            # Usando un provider faker si es especificado, de lo contrario inferir desde el tipo según el tipo de dato
            if column.faker_provider:
                value = _get_value_from_provider(column.faker_provider)
            else:
                value = _infer_value_from_type(column.type)
            
            values.append(value)
        
        # Formatear como una tupla para SQL
        row_values = f"({', '.join(values)})"
        value_rows.append(row_values)
    
    # Crear una sentencia INSERT con múltiples conjuntos de valores
    query = f"INSERT INTO {table.name} ({', '.join(column_names)}) VALUES \n"
    query += ",\n".join(value_rows) + ";"
    
    return query

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
            
            
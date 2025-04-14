"""
Utilidades específicas para testing con el generador de SQL
"""
import os
from typing import Dict, List, Tuple, Optional
from src.schema import Table, Column, ForeignKey, registry
from src.generator import generate_insert_queries_in_order, generate_insert_query
from src.utils import export_sql_to_file

def generate_testing_schemas() -> Dict[Table, int]:
    """
    Crea un conjunto completo de esquemas para testing con diferentes relaciones
    
    Devuelve:
        Un diccionario con las tablas y el número de filas a generar para cada una
    """
    usuarios_table = Table(
        name="usuarios",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(name="nombre", type="VARCHAR(50)", faker_provider="first_name"),
            Column(name="apellido", type="VARCHAR(50)", faker_provider="last_name"),
            Column(name="email", type="VARCHAR(100)", faker_provider="email"),
            Column(name="fecha_registro", type="DATE", faker_provider="date_this_decade"),
            Column(name="activo", type="BOOLEAN", faker_provider="boolean")
        ]
    )
    
    perfiles_table = Table(
        name="perfiles",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(
                name="usuario_id", 
                type="INTEGER",
                foreign_key=ForeignKey(
                    column="usuario_id",
                    references_table="usuarios",
                    references_column="id"
                )
            ),
            Column(name="bio", type="TEXT", faker_provider="paragraph"),
            Column(name="avatar", type="VARCHAR(255)", faker_provider="image_url"),
            Column(name="telefono", type="VARCHAR(20)", faker_provider="phone_number")
        ]
    )
    
    categorias_table = Table(
        name="categorias",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(name="nombre", type="VARCHAR(50)", faker_provider="word"),
            Column(name="slug", type="VARCHAR(50)", faker_provider="slug")
        ]
    )
    
    articulos_table = Table(
        name="articulos",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(name="titulo", type="VARCHAR(100)", faker_provider="sentence"),
            Column(
                name="autor_id", 
                type="INTEGER",
                foreign_key=ForeignKey(
                    column="autor_id",
                    references_table="usuarios",
                    references_column="id"
                )
            ),
            Column(name="contenido", type="TEXT", faker_provider="text"),
            Column(name="fecha_publicacion", type="DATETIME", faker_provider="date_time_this_month"),
            Column(
                name="categoria_id", 
                type="INTEGER",
                foreign_key=ForeignKey(
                    column="categoria_id",
                    references_table="categorias",
                    references_column="id"
                )
            ),
            Column(name="publicado", type="BOOLEAN", faker_provider="boolean")
        ]
    )
    
    comentarios_table = Table(
        name="comentarios",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(
                name="articulo_id", 
                type="INTEGER",
                foreign_key=ForeignKey(
                    column="articulo_id",
                    references_table="articulos",
                    references_column="id"
                )
            ),
            Column(
                name="usuario_id", 
                type="INTEGER",
                foreign_key=ForeignKey(
                    column="usuario_id",
                    references_table="usuarios",
                    references_column="id"
                )
            ),
            Column(name="contenido", type="TEXT", faker_provider="paragraph"),
            Column(name="fecha", type="DATETIME", faker_provider="date_time_this_month")
        ]
    )
    
    etiquetas_table = Table(
        name="etiquetas",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(name="nombre", type="VARCHAR(30)", faker_provider="word")
        ]
    )
    
    articulos_etiquetas_table = Table(
        name="articulos_etiquetas",
        columns=[
            Column(name="id", type="INTEGER", faker_provider="random_int"),
            Column(
                name="articulo_id", 
                type="INTEGER",
                foreign_key=ForeignKey(
                    column="articulo_id",
                    references_table="articulos",
                    references_column="id"
                )
            ),
            Column(
                name="etiqueta_id", 
                type="INTEGER",
                foreign_key=ForeignKey(
                    column="etiqueta_id",
                    references_table="etiquetas",
                    references_column="id"
                )
            )
        ]
    )
    
    # Retornar las tablas con el número de filas a generar para cada una
    return {
        usuarios_table: 50,
        perfiles_table: 40,
        categorias_table: 10,
        articulos_table: 100,
        comentarios_table: 200,
        etiquetas_table: 30,
        articulos_etiquetas_table: 150
    }

def generate_testing_sql(output_dir: str = "testing", prefix: str = "test_data") -> Tuple[int, int]:
    """
    Genera SQL para testing con múltiples esquemas relacionados
    
    Args:
        output_dir: Directorio donde se guardarán los archivos
        prefix: Prefijo para los nombres de archivo
        
    Devuelve:
        Tuple con (número de tablas, número total de filas)
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    tables_and_rows = generate_testing_schemas()
    
    queries = generate_insert_queries_in_order(tables_and_rows)
    
    all_sql_file = os.path.join(output_dir, f"{prefix}_all.sql")
    export_sql_to_file(queries, all_sql_file)
    
    for table_name, query in queries.items():
        table_sql_file = os.path.join(output_dir, f"{prefix}_{table_name}.sql")
        export_sql_to_file({table_name: query}, table_sql_file)
    
    return len(queries), sum(tables_and_rows.values())

def generate_custom_testing_sql(tables_config: List[Tuple[str, List[Tuple[str, str, Optional[str]]], int]], 
                               output_file: str = "custom_test_data.sql",
                               relationships: List[Tuple[str, str, str, str]] = None) -> str:
    """
    Genera SQL para testing basado en una configuración personalizada
    
    Args:
        tables_config: Lista de tuplas (nombre_tabla, [(nombre_columna, tipo, faker_provider)], num_filas)
        output_file: Ruta del archivo de salida
        relationships: Lista de tuplas (tabla_origen, columna_origen, tabla_destino, columna_destino)
        
    Devuelve:
        Ruta del archivo SQL generado
    """
    tables = {}
    table_objects = []
    
    # Primero crear todas las tablas sin relaciones
    for table_name, columns_data, num_rows in tables_config:
        columns = []
        for col_name, col_type, faker_provider in columns_data:
            columns.append(Column(name=col_name, type=col_type, faker_provider=faker_provider))
        
        table = Table(name=table_name, columns=columns)
        tables[table_name] = (table, num_rows)
        table_objects.append(table)
    
    # Luego agregar las relaciones
    if relationships:
        for source_table, source_col, target_table, target_col in relationships:
            # Encontrar la columna en la tabla origen
            for table, _ in tables.values():
                if table.name == source_table:
                    for col in table.columns:
                        if col.name == source_col:
                            # Agregar la llave foránea
                            col.foreign_key = ForeignKey(
                                column=source_col,
                                references_table=target_table,
                                references_column=target_col
                            )
    
    # Preparar el diccionario para generate_insert_queries_in_order
    tables_and_rows = {table: num_rows for table, num_rows in tables.values()}
    
    queries = generate_insert_queries_in_order(tables_and_rows)
    
    export_sql_to_file(queries, output_file)
    
    return output_file 
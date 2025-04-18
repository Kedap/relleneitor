"""
Utilidades para la generación de esquemas y datos
"""

from typing import Dict


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

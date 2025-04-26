"""
Ejemplo de generación de datos para un hospital y subida a MariaDB con configuración personalizada
"""

from src.schema import Table, Column, ForeignKey
from src.generator import generate_insert_queries_in_order
from src.utils import export_sql_to_mariadb


def create_hospital_schema():
    """
    Crea el esquema de la base de datos del hospital
    """
    # Tabla de especialidades médicas
    especialidades = Table(
        name="especialidades",
        columns=[
            Column("id", "INTEGER", is_primary_key=True),
            Column("nombre", "VARCHAR(100)"),
            Column("descripcion", "TEXT"),
        ],
    )

    # Tabla de médicos
    medicos = Table(
        name="medicos",
        columns=[
            Column("id", "INTEGER", is_primary_key=True),
            Column("nombre", "VARCHAR(100)"),
            Column("apellido", "VARCHAR(100)"),
            Column("email", "EMAIL"),
            Column("telefono", "PHONE"),
            Column(
                "especialidad_id",
                "INTEGER",
                foreign_key=ForeignKey("especialidad_id", "especialidades", "id"),
            ),
        ],
    )

    # Tabla de pacientes
    pacientes = Table(
        name="pacientes",
        columns=[
            Column("id", "INTEGER", is_primary_key=True),
            Column("nombre", "VARCHAR(100)"),
            Column("apellido", "VARCHAR(100)"),
            Column("fecha_nacimiento", "DATE"),
            Column("email", "EMAIL"),
            Column("telefono", "PHONE"),
            Column("direccion", "ADDRESS"),
        ],
    )

    # Tabla de citas
    citas = Table(
        name="citas",
        columns=[
            Column("id", "INTEGER", is_primary_key=True),
            Column(
                "paciente_id",
                "INTEGER",
                foreign_key=ForeignKey("paciente_id", "pacientes", "id"),
            ),
            Column(
                "medico_id",
                "INTEGER",
                foreign_key=ForeignKey("medico_id", "medicos", "id"),
            ),
            Column("fecha_hora", "DATETIME"),
            Column("motivo", "TEXT"),
            Column("estado", "VARCHAR(50)"),
        ],
    )

    return [especialidades, medicos, pacientes, citas]


def main():
    # Crear el esquema
    tables = create_hospital_schema()

    # Definir cuántas filas generar para cada tabla
    rows_per_table = {
        tables[0]: 10,  # 10 especialidades
        tables[1]: 50,  # 50 médicos
        tables[2]: 200,  # 200 pacientes
        tables[3]: 500,  # 500 citas
    }

    # Generar las queries
    queries = generate_insert_queries_in_order(rows_per_table)

    # Configuración personalizada de la base de datos
    db_config = {
        "host": "192.168.1.100",  # IP del servidor MariaDB
        "user": "hospital_admin",  # Usuario personalizado
        "password": "contraseña_segura123",  # Contraseña personalizada
        "database": "hospital_produccion",  # Base de datos personalizada
        "port": 3307,  # Puerto personalizado
    }

    # Exportar a MariaDB
    try:
        export_sql_to_mariadb(queries, **db_config)
        print("Datos generados y exportados exitosamente a la base de datos")
    except Exception as e:
        print(f"Error al exportar datos: {str(e)}")


if __name__ == "__main__":
    main()

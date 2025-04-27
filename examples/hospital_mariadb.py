"""
Ejemplo de generación de datos para un hospital y subida a MariaDB
"""

from src.schema import Table, Column, ForeignKey
from src.generator import generate_insert_queries_in_order
from src.database import MariaDBManager
import random


def estado_provider():
    Estados = ["Pendiente", "Atendido", "Cancelado"]
    return f"'{random.choice(Estados)}'"


def create_hospital_schema():
    """
    Crea el esquema de la base de datos del hospital
    """
    # Tabla de especialidades médicas
    especialidades = Table(
        name="Especialidades",
        columns=[
            Column(
                "id_especialidad",
                "INTEGER",
                is_primary_key=True,
                primary_key_autoincrement=True,
            ),
            Column("nombre", "TEXT"),
            Column("descripcion", "TEXT"),
        ],
    )

    # Tabla de médicos
    medicos = Table(
        name="Doctores",
        columns=[
            Column(
                "id_doctor",
                "INTEGER",
                is_primary_key=True,
                primary_key_autoincrement=True,
            ),
            Column("nombre", "VARCHAR(100)", faker_provider="name"),
            Column("email", "EMAIL", faker_provider="relleneitor_email"),
            Column("telefono", "PHONE"),
            Column(
                "especialidad_id",
                "INTEGER",
                foreign_key=ForeignKey(
                    "especialidad_id", "Especialidades", "id_especialidad"
                ),
            ),
        ],
    )

    # Tabla de pacientes
    pacientes = Table(
        name="Pacientes",
        columns=[
            Column(
                "id_paciente",
                "INTEGER",
                is_primary_key=True,
                primary_key_autoincrement=True,
            ),
            Column("nombre", "VARCHAR(100)", faker_provider="name"),
            Column("fecha_nacimiento", "DATE"),
            Column("email", "EMAIL", faker_provider="relleneitor_email"),
            Column("telefono", "PHONE"),
            Column(
                "direccion", "ADDRESS", faker_provider="address"
            ),  # Importante utilizar el faker_provider="address" porque de otra forma no se formatea correctamente
        ],
    )

    # Tabla de citas
    citas = Table(
        name="Citas",
        columns=[
            Column(
                "id_cita",
                "INTEGER",
                is_primary_key=True,
                primary_key_autoincrement=True,
            ),
            Column(
                "paciente_id",
                "INTEGER",
                foreign_key=ForeignKey("paciente_id", "Pacientes", "id_paciente"),
            ),
            Column(
                "doctor_id",
                "INTEGER",
                foreign_key=ForeignKey("doctor_id", "Doctores", "id_doctor"),
            ),
            Column("fecha_hora", "DATETIME"),
            Column("estado", "VARCHAR(50)", custom_provider=estado_provider),
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

    db = MariaDBManager(database="Hospital_test", user="userdb", password="12345678")

    # Exportar a MariaDB
    try:
        db.execute_queries(queries)
        print("Datos generados y exportados exitosamente a la base de datos")
    except Exception as e:
        print(f"Error al exportar datos: {str(e)}")


if __name__ == "__main__":
    main()

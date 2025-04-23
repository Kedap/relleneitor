from src.schema import Table, Column
from src.generator import generate_insert_query
from src.utils import export_sql_to_file


import random


def edad_provider():
    return f"{random.randint(1, 80)}"


def genero_provider():
    if random.randint(1, 2) == 1:
        return "'M'"
    else:
        return "'F'"


def estado_provider():
    Estados = ["Pendiente", "Atendido", "Cancelado"]
    return f"'{random.choice(Estados)}'"


def foreign_key_pacientes_provider():
    return str(random.randint(1000, 2000))


def foreign_key_doctores_provider():
    return str(random.randint(2000, 2900))


def especialidad_provider():
    Especialidades = ["Cardiologia", "Pediatria", "Neurologia"]
    return f"'{random.choice(Especialidades)}'"


pacientes_table = Table(
    name="Pacientes",
    columns=[
        Column(name="nombre_completo", type="TEXT", faker_provider="name"),
        Column(name="edad", type="INTEGER", custom_provider=edad_provider),
        Column(name="genero", type="TEXT", custom_provider=genero_provider),
        Column(name="correo", type="TEXT", faker_provider="email"),
    ],
)

num_rows = 10

sql_statements_pacientes = generate_insert_query(
    table=pacientes_table, num_rows=num_rows
)

doctores_table = Table(
    name="Doctores",
    columns=[
        Column(name="nombre", type="TEXT", faker_provider="name"),
        Column(name="especialidad", type="TEXT", custom_provider=especialidad_provider),
    ],
)

sql_statements_doctores = generate_insert_query(table=doctores_table, num_rows=num_rows)

citas_table = Table(
    name="Citas",
    columns=[
        Column(
            name="paciente",
            type="INTEGER",
            custom_provider=foreign_key_pacientes_provider,
        ),
        Column(
            name="doctor",
            type="INTEGER",
            custom_provider=foreign_key_doctores_provider,
        ),
        Column(name="fecha", type="DATE", faker_provider="date"),
        Column(name="estado", type="TEXT", custom_provider=estado_provider),
    ],
)

sql_statements_citas = generate_insert_query(table=citas_table, num_rows=num_rows)
export_sql_to_file(
    {
        "Pacientes": sql_statements_pacientes,
        "Doctores": sql_statements_doctores,
        "Citas": sql_statements_citas,
    },
    "hospital.sql",
)

from src.schema import Table, Column, registry
from src.generator import generate_insert_query
from faker import Faker


def custom_provider_email():
    faker = Faker()
    dominios_correo = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com"]
    return faker.email().replace("example.com", dominios_correo[faker.random_int(0, 3)])


# Esquema para la tabla 'proveedores'
proveedores_table = Table(
    name="proveedores",
    columns=[
        Column(
            name="rut", type="INTEGER", faker_provider="random_int", is_primary_key=True
        ),
        Column(name="nombre", type="TEXT", faker_provider="company"),
        Column(name="direccion", type="TEXT", faker_provider="address"),
        Column(name="telefono", type="INTEGER", faker_provider="phone_number"),
        Column(name="correo", type="TEXT", custom_provider=custom_provider_email),
        Column(name="pagina_web", type="TEXT", faker_provider="url"),
    ],
    primary_key="rut",
)

num_rows = 10

# Registrar la tabla en el registro global para uso con llaves foráneas
registry.register(proveedores_table)

sql_statements = generate_insert_query(table=proveedores_table, num_rows=num_rows)

print(sql_statements)

from src.schema import Table, Column
from src.generator import generate_insert_query

proveedores_table = Table(
    name="proveedores",
    columns=[
        Column(name="rut", type="INTEGER", faker_provider="random_int"),
        Column(name="nombre", type="TEXT", faker_provider="company"),
        Column(name="direccion", type="TEXT", faker_provider="address"),
        Column(name="telefono", type="INTEGER", faker_provider="phone_number"),
        Column(name="pagina_web", type="TEXT", faker_provider="url")
    ]
)

num_rows = 10

sql_statements = generate_insert_query(table=proveedores_table, num_rows=num_rows)

for stmt in sql_statements:
    print(stmt)

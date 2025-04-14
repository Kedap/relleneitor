from src.schema import Table, Column
from src.generator import generate_insert_query

telefono_proveedor_table = Table(
    name="telefono_proveedor",
    columns=[
        Column(name="id", type="INTEGER", faker_provider="random_int"),
        Column(name="proveedor", type="INTEGER", faker_provider="random_int"),
        Column(name="casa", type="TEXT", faker_provider="phone_number"),
        Column(name="movil", type="TEXT", faker_provider="phone_number"),
        Column(name="oficina", type="TEXT", faker_provider="phone_number"),
        Column(name="personal", type="TEXT", faker_provider="phone_number")
    ]
)

num_rows = 10

sql_statements = generate_insert_query(table=telefono_proveedor_table, num_rows=num_rows)

for stmt in sql_statements:
    print(stmt)

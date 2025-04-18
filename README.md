# Relleneitor

Relleneitor es una herramienta Python diseñada para generar datos sintéticos y crear consultas SQL de inserción de manera automática. Es especialmente útil para:

- Generar datos de prueba para bases de datos
- Crear scripts de inserción de datos iniciales
- Mantener la integridad referencial entre tablas
- Automatizar la generación de datos sintéticos realistas

## Características Principales

- Generación de datos sintéticos usando Faker
- Soporte para relaciones entre tablas (llaves foráneas)
- Generación automática de consultas SQL INSERT
- Ordenamiento automático de inserciones según dependencias
- Exportación de consultas a archivos SQL
- Soporte para múltiples tipos de datos SQL

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso Básico

### 1. Definición de Tablas

Primero, necesitas definir la estructura de tus tablas usando las clases `Table` y `Column`:

```python
from src.schema import Table, Column, ForeignKey, registry

# Definir una tabla simple
usuarios_table = Table(
    name="usuarios",
    columns=[
        Column(name="id", type="INTEGER", faker_provider="random_int", is_primary_key=True),
        Column(name="nombre", type="VARCHAR(50)", faker_provider="name"),
        Column(name="email", type="VARCHAR(100)", faker_provider="email"),
    ],
    primary_key="id"
)

# Registrar la tabla en el registro global
registry.register(usuarios_table)
```

### 2. Generación de Consultas SQL

```python
from src.generator import generate_insert_query

# Generar consultas para 10 filas
sql_statements = generate_insert_query(table=usuarios_table, num_rows=10)
print(sql_statements)
```

## Ejemplo Completo: Sistema de Proveedores

### 1. Definición del Esquema

```python
from src.schema import Table, Column, ForeignKey, registry

# Tabla de proveedores
proveedores_table = Table(
    name="proveedores",
    columns=[
        Column(name="rut", type="INTEGER", faker_provider="random_int", is_primary_key=True),
        Column(name="nombre", type="TEXT", faker_provider="company"),
        Column(name="direccion", type="TEXT", faker_provider="address"),
        Column(name="telefono", type="INTEGER", faker_provider="phone_number"),
        Column(name="pagina_web", type="TEXT", faker_provider="url"),
    ],
    primary_key="rut"
)

# Registrar la tabla de proveedores
registry.register(proveedores_table)

# Tabla de teléfonos de proveedores
telefono_proveedor_table = Table(
    name="telefono_proveedor",
    columns=[
        Column(name="id", type="INTEGER", faker_provider="random_int", is_primary_key=True),
        Column(
            name="proveedor",
            type="INTEGER",
            foreign_key=ForeignKey(
                column="proveedor",
                references_table="proveedores",
                references_column="rut"
            )
        ),
        Column(name="casa", type="TEXT", faker_provider="phone_number"),
        Column(name="movil", type="TEXT", faker_provider="phone_number"),
        Column(name="oficina", type="TEXT", faker_provider="phone_number"),
        Column(name="personal", type="TEXT", faker_provider="phone_number"),
    ],
    primary_key="id"
)
```

### 2. Generación de Datos

```python
from src.generator import generate_insert_queries_in_order

# Generar consultas para ambas tablas
queries = generate_insert_queries_in_order({
    proveedores_table: 10,
    telefono_proveedor_table: 20
})

# Exportar a archivo
from src.utils import export_sql_to_file
export_sql_to_file(queries, "datos_iniciales.sql")
```

## Migración desde Estructura SQL Existente

Para migrar una estructura SQL existente a Relleneitor, sigue estos pasos:

### 1. Analiza tu esquema SQL

Por ejemplo, si tienes esta estructura SQL:

```sql
CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(100),
    email VARCHAR(100),
    telefono VARCHAR(20)
);

CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    cliente_id INTEGER,
    fecha DATE,
    total DECIMAL(10,2),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);
```

### 2. Convierte a Esquema Relleneitor

```python
from src.schema import Table, Column, ForeignKey, registry

# Tabla de clientes
clientes_table = Table(
    name="clientes",
    columns=[
        Column(name="id", type="INTEGER", faker_provider="random_int", is_primary_key=True),
        Column(name="nombre", type="VARCHAR(100)", faker_provider="name"),
        Column(name="email", type="VARCHAR(100)", faker_provider="email"),
        Column(name="telefono", type="VARCHAR(20)", faker_provider="phone_number"),
    ],
    primary_key="id"
)

# Registrar la tabla de clientes
registry.register(clientes_table)

# Tabla de pedidos
pedidos_table = Table(
    name="pedidos",
    columns=[
        Column(name="id", type="INTEGER", faker_provider="random_int", is_primary_key=True),
        Column(
            name="cliente_id",
            type="INTEGER",
            foreign_key=ForeignKey(
                column="cliente_id",
                references_table="clientes",
                references_column="id"
            )
        ),
        Column(name="fecha", type="DATE", faker_provider="date"),
        Column(name="total", type="DECIMAL(10,2)", faker_provider="random_int(min=100,max=10000)"),
    ],
    primary_key="id"
)
```

### 3. Genera los Datos

```python
from src.generator import generate_insert_queries_in_order

# Generar consultas manteniendo las relaciones
queries = generate_insert_queries_in_order({
    clientes_table: 50,
    pedidos_table: 100
})

# Exportar a archivo
from src.utils import export_sql_to_file
export_sql_to_file(queries, "datos_iniciales.sql")
```

## Tipos de Datos Soportados

- INTEGER
- VARCHAR(n)
- TEXT
- DATE
- DECIMAL(p,s)
- BOOLEAN
- TIMESTAMP

## Proveedores Faker Disponibles

- name
- email
- address
- phone_number
- company
- date
- random_int
- sentence
- paragraph
- url
- word

## Mejores Prácticas

1. **Orden de Registro**: Registra siempre las tablas padre antes que las tablas hijas.
2. **Llaves Primarias**: Define explícitamente las llaves primarias.
3. **Integridad Referencial**: Asegúrate de que las tablas referenciadas existan antes de crear las llaves foráneas.
4. **Cantidad de Datos**: Genera suficientes datos en las tablas padre para que las tablas hijas puedan referenciarlos.

## Contribuir

Las contribuciones son bienvenidas. Por favor, asegúrate de:

1. Seguir las convenciones de código PEP 8
2. Incluir pruebas para nuevas funcionalidades
3. Actualizar la documentación según sea necesario

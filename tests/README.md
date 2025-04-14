# Tests para Relleneitor

Este directorio contiene los tests automatizados para el generador de SQL con datos sintéticos.

## Estructura de los tests

- `test_sql_generator.py`: Tests generales para la generación de consultas SQL
- `test_foreign_keys.py`: Tests específicos para las funcionalidades de llaves foráneas
- `conftest.py`: Configuración compartida y fixtures para todos los tests

## Ejecución de tests

Para ejecutar todos los tests:

```bash
pytest
```

Para ejecutar un archivo de tests específico:

```bash
pytest tests/test_sql_generator.py
```

Para ejecutar un test específico:

```bash
pytest tests/test_foreign_keys.py::test_foreign_key_validity
```

## Cobertura de los tests

Los tests cubren las siguientes áreas:

1. **Generación básica de SQL**
   - Generación de consultas INSERT válidas
   - Formato adecuado de los valores según el tipo de datos

2. **Relaciones de tablas**
   - Registro correcto de tablas
   - Creación y uso de llaves primarias
   - Validación de llaves foráneas

3. **Utilidades de testing**
   - Generación de esquemas predefinidos
   - Exportación de SQL a archivos
   - Personalización de esquemas

## Notas sobre los tests

- Se utiliza una semilla fija para Faker para garantizar la reproducibilidad de los tests
- Cada test se ejecuta con un registro de tablas limpio
- Los archivos generados durante los tests se almacenan en un directorio temporal 
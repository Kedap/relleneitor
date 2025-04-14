from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class ForeignKey:
    """Define una relación de llave foránea entre columnas."""
    column: str             # Nombre de la columna local que es FK
    references_table: str   # Tabla a la que hace referencia
    references_column: str  # Columna de la tabla referenciada
    
@dataclass
class Column:
    name: str
    type: str
    faker_provider: Optional[str] = None
    is_primary_key: bool = False
    foreign_key: Optional[ForeignKey] = None
    constraints: Optional[List[str]] = None

@dataclass
class Table:
    name: str
    columns: List[Column]
    primary_key: Optional[str] = None  # Nombre de la columna que es PK
    
    # Almacenamiento de valores generados para columnas - usado para llaves foráneas
    _generated_values: Dict[str, List[Any]] = None
    
    def __post_init__(self):
        """Inicializar el diccionario de valores generados."""
        self._generated_values = {}
        
        # Si no se especificó una clave primaria y hay columnas, marcar la primera como PK
        if not self.primary_key and self.columns:
            self.primary_key = self.columns[0].name
            self.columns[0].is_primary_key = True
        elif self.primary_key:
            for col in self.columns:
                if col.name == self.primary_key:
                    col.is_primary_key = True
    
    def store_generated_value(self, column_name: str, value: Any):
        """Almacena un valor generado para una columna específica."""
        if column_name not in self._generated_values:
            self._generated_values[column_name] = []
        
        # Extraer el valor sin comillas si es una cadena SQL
        if isinstance(value, str) and value.startswith("'") and value.endswith("'"):
            clean_value = value[1:-1].replace("''", "'")
        else:
            clean_value = value
            
        self._generated_values[column_name].append(clean_value)
    
    def get_generated_values(self, column_name: str) -> List[Any]:
        """Obtiene los valores generados para una columna específica."""
        return self._generated_values.get(column_name, [])
        
@dataclass
class TableRegistry:
    """Registro central de tablas para gestionar relaciones entre ellas."""
    tables: Dict[str, Table] = None
    
    def __post_init__(self):
        if self.tables is None:
            self.tables = {}
    
    def register(self, table: Table):
        """Registra una tabla en el registro."""
        self.tables[table.name] = table
        return table
    
    def get(self, table_name: str) -> Table:
        """Obtiene una tabla del registro."""
        return self.tables.get(table_name)
    
    def get_foreign_key_values(self, foreign_key: ForeignKey) -> List[Any]:
        """Obtiene los valores generados para una columna referenciada por una llave foránea."""
        referenced_table = self.get(foreign_key.references_table)
        if referenced_table:
            return referenced_table.get_generated_values(foreign_key.references_column)
        return []

# Instancia global del registro de tablas
registry = TableRegistry()

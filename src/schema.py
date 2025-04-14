from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Column:
    name: str
    type: str
    faker_provider: Optional[str] = None

@dataclass
class Table:
    name: str
    columns: List[Column]

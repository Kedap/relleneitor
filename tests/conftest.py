"""
Configuración y fixtures compartidos para los tests
"""
import pytest
import os
import shutil
from faker import Faker
from src.schema import Table, Column, registry

# Inicializar Faker con una semilla fija para tests reproducibles
faker = Faker()
Faker.seed(12345)

@pytest.fixture(scope="session")
def test_dir():
    """Crear un directorio temporal para los tests"""
    test_output_dir = os.path.join(os.getcwd(), "test_output")
    
    if os.path.exists(test_output_dir):
        shutil.rmtree(test_output_dir)
    
    os.makedirs(test_output_dir)
    
    yield test_output_dir
    
    if os.path.exists(test_output_dir):
        shutil.rmtree(test_output_dir)

@pytest.fixture(autouse=True)
def reset_registry():
    """Resetear el registro global antes de cada test"""
    old_registry = registry.tables.copy() if registry.tables else {}
    
    registry.tables = {}
    
    yield
    
    registry.tables = old_registry 
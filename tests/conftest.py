import pytest

from agente_operaciones import herramientas
from agente_operaciones.config import Configuracion

@pytest.fixture
def config():
    """Configuración de prueba: no lee el .env y no necesita una clave real."""
    return Configuracion(groq_api_key="prueba", _env_file=None, pedido_minimo=5)

@pytest.fixture(autouse=True)
def pedidos_limpios():
    """Cada prueba empieza con la lista de pedidos vacía."""
    herramientas.PEDIDOS.clear()
    yield
    herramientas.PEDIDOS.clear()
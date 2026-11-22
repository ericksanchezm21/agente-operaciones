from agente_operaciones.config import cargar_configuracion
from agente_operaciones.herramientas import PEDIDOS, registrar_pedido

config = cargar_configuracion()
print(registrar_pedido(config, "Ana", [{"producto_id": "cuaderno-a4", "cantidad": 2}]))
print(len(PEDIDOS))
print(registrar_pedido(config, "Ana", [{"producto_id": "cuaderno-a4", "cantidad": 0}]))
print(len(PEDIDOS))
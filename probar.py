from agente_operaciones.config import cargar_configuracion
from agente_operaciones.herramientas import PEDIDOS, registrar_pedido

config = cargar_configuracion()

print(config.cantidad_maxima_por_item)  # Afirmación 0: la cantidad máxima por item es la que está en la configuración

# Afirmación 1: una cantidad 0 devuelve error
print(registrar_pedido(config, "Ana", [{"producto_id": "cuaderno-a4", "cantidad": 0}]))
# Afirmación 2: ese error no agrega nada a PEDIDOS
print(len(PEDIDOS))
# Afirmación 3: el máximo sale de la configuración
print(registrar_pedido(config, "Ana", [{"producto_id": "cuaderno-a4", "cantidad": 3}]))
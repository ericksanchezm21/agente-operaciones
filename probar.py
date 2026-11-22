from agente_operaciones.agente import HERRAMIENTAS, ejecutar
from agente_operaciones.config import cargar_configuracion
from agente_operaciones import herramientas

config = cargar_configuracion()

print([h["function"]["name"] for h in HERRAMIENTAS])
print([hasattr(herramientas, h["function"]["name"]) for h in HERRAMIENTAS])
print(ejecutar(config, "consultar_producto", {"nombre": "cuaderno"}))
print(ejecutar(config, "registrar_pedido", {"cliente": "Ana", "items": [{"producto_id": "cuaderno-a4", "cantidad": 2}]}))
print(ejecutar(config, "borrar_todo", {}))
print(ejecutar(config, "consultar_producto", {"producto": "cuaderno"}))
print(ejecutar(config, "registrar_pedido", {"cliente": "Ana"}))
print(ejecutar(config, "registrar_pedido", [1, 2]))
print(len(herramientas.PEDIDOS))
import json
from agente_operaciones import herramientas
from agente_operaciones.config import Configuracion

def cfg(**extra):
    return Configuracion(groq_api_key="prueba", _env_file=None, **extra)

def pedir(config, *items): # cada item es una pareja (producto_id, cantidad)
    datos = [{"producto_id": p, "cantidad": c} for p, c in items]
    return json.loads(herramientas.registrar_pedido(config, "Ana", datos))

assert "error" in pedir(cfg(max_lineas_pedido=2), ("cuaderno-a4", 1), ("boligrafos-caja", 1), ("resma-papel", 1))
assert "error" in pedir(cfg(max_lineas_pedido=2), ("cuaderno-a4", 1), ("boligrafos-caja", 1))
assert "error" in pedir(cfg(max_lineas_pedido=2), ("cuaderno-a4", 1))
assert "error" in pedir(cfg(monto_maximo_pedido=20), ("resma-papel", 3))
assert "error" in pedir(cfg(monto_maximo_pedido=20), ("boligrafos-caja", 2), ("resma-papel", 1))
assert "error" in pedir(cfg(monto_maximo_pedido=20), ("cuaderno-a4", 1))

print("Todas las reglas pasan")
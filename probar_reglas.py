
import json
from agente_operaciones import herramientas
from agente_operaciones.config import Configuracion


def cfg(**extra):
    return Configuracion(groq_api_key="prueba", _env_file=None, **extra)


def pedir(config, *items):
    # Cada ítem es una pareja (producto_id, cantidad)
    datos = [{"producto_id": p, "cantidad": c} for p, c in items]
    return json.loads(
        herramientas.registrar_pedido(config, "Ana", datos)
    )


# REGLA A: Máximo de productos distintos por pedido

# Caso 1: Falla (3 productos, máximo 2)
assert "error" in pedir(
    cfg(max_lineas_pedido=2),
    ("cuaderno-a4", 1),
    ("boligrafos-caja", 1),
    ("resma-papel", 1)
)

# Caso 2: En el límite (2 productos, máximo 2)
assert pedir(
    cfg(max_lineas_pedido=2),
    ("cuaderno-a4", 1),
    ("boligrafos-caja", 1)
)["ok"] is True

# Caso 3: Pasa (1 producto, máximo 2)
assert pedir(
    cfg(max_lineas_pedido=2),
    ("cuaderno-a4", 1)
)["ok"] is True


# REGLA B: Monto máximo por pedido

# Caso 4: Falla (24.0, máximo 20)
assert "error" in pedir(
    cfg(monto_maximo_pedido=20),
    ("resma-papel", 3)
)

# Caso 5: En el límite (20.0, máximo 20)
assert pedir(
    cfg(monto_maximo_pedido=20),
    ("boligrafos-caja", 2),
    ("resma-papel", 1)
)["ok"] is True

# Caso 6: Pasa (4.5, máximo 20)
assert pedir(
    cfg(monto_maximo_pedido=20),
    ("cuaderno-a4", 1)
)["ok"] is True


print("Todas las reglas pasan")

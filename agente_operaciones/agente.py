from agente_operaciones.herramientas import (
    _error,
    consultar_producto,
    registrar_pedido,
)


HERRAMIENTAS = [
    {
        "type": "function",
        "function": {
            "name": "consultar_producto",
            "description": (
                "Consulta el catálogo para encontrar un producto por nombre y conocer "
                "su precio y disponibilidad. Úsala cuando el cliente pregunte por un "
                "producto o necesite información antes de hacer un pedido."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre o parte del nombre del producto que se desea consultar.",
                    }
                },
                "required": ["nombre"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "registrar_pedido",
            "description": (
                "Registra un pedido de productos. Úsala únicamente después de que "
                "el cliente haya confirmado explícitamente el pedido."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "cliente": {
                        "type": "string",
                        "description": "Nombre del cliente que realiza el pedido.",
                    },
                    "items": {
                        "type": "array",
                        "description": "Productos y cantidades incluidos en el pedido confirmado.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "producto_id": {
                                    "type": "string",
                                    "description": "Identificador del producto en el catálogo.",
                                },
                                "cantidad": {
                                    "type": "integer",
                                    "description": "Cantidad solicitada del producto.",
                                },
                            },
                            "required": ["producto_id", "cantidad"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["cliente", "items"],
                "additionalProperties": False,
            },
        },
    },
]


def ejecutar(config, nombre, argumentos):
    try:
        if nombre == "consultar_producto":
            return consultar_producto(**argumentos)
        if nombre == "registrar_pedido":
            return registrar_pedido(config, **argumentos)
        return _error(f"La herramienta '{nombre}' no existe.")
    except (TypeError, AttributeError) as exc:
        return _error(f"Argumentos incorrectos para '{nombre}': {exc}")
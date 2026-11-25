import json

from groq import Groq

from agente_operaciones.config import Configuracion
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


SYSTEM_PROMPT = (
    "Eres el agente de operaciones de Suministros Norte. Mantén un tono amable y "
    "profesional. Utiliza las herramientas para consultar precios y disponibilidad "
    "en el catálogo y para registrar pedidos. No inventes productos, precios, "
    "disponibilidad ni datos de pedidos. Antes de registrar un pedido, solicita y "
    "obtén la confirmación explícita del cliente."
)


class Agente:
    def __init__(self, config: Configuracion, cliente: Groq | None = None):
        self.config = config
        self.cliente = cliente or Groq(api_key=config.groq_api_key.get_secret_value())
        self.historial = [{"role": "system", "content": SYSTEM_PROMPT}]

    def responder(self, mensaje: str) -> str:
        self.historial.append({"role": "user", "content": mensaje})
        llamadas_herramienta = 0

        while True:
            respuesta = self.cliente.chat.completions.create(
                model=self.config.modelo,
                messages=self.historial,
                tools=HERRAMIENTAS,
                tool_choice="auto" if llamadas_herramienta < 2 else "none",
            )
            mensaje_agente = respuesta.choices[0].message
            llamadas = mensaje_agente.tool_calls or []

            if not llamadas:
                contenido = mensaje_agente.content or ""
                self.historial.append({"role": "assistant", "content": contenido})
                return contenido

            restantes = 2 - llamadas_herramienta
            if restantes <= 0:
                contenido = mensaje_agente.content or (
                    "No puedo realizar más consultas de herramientas en esta respuesta."
                )
                self.historial.append({"role": "assistant", "content": contenido})
                return contenido

            llamadas = llamadas[:restantes]
            mensaje_historial = {
                "role": "assistant",
                "content": mensaje_agente.content,
                "tool_calls": [
                    {
                        "id": llamada.id,
                        "type": "function",
                        "function": {
                            "name": llamada.function.name,
                            "arguments": llamada.function.arguments,
                        },
                    }
                    for llamada in llamadas
                ],
            }
            self.historial.append(mensaje_historial)

            for llamada in llamadas:
                nombre = llamada.function.name
                try:
                    argumentos = json.loads(llamada.function.arguments)
                except (json.JSONDecodeError, TypeError) as exc:
                    resultado = _error(f"Argumentos de herramienta ilegibles: {exc}")
                else:
                    resultado = ejecutar(self.config, nombre, argumentos)

                print(f"[herramienta] {nombre} -> {resultado}")
                self.historial.append(
                    {
                        "role": "tool",
                        "tool_call_id": llamada.id,
                        "content": resultado,
                    }
                )
                llamadas_herramienta += 1
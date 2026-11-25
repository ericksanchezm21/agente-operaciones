"""Piezas de mentira para probar al agente sin llamar a Groq."""

import json
from types import SimpleNamespace

class ClienteFalso:

    """Hace de cliente de Groq: devuelve respuestas fijas, en orden."""

    def __init__(self, *respuestas):
        self._respuestas = list(respuestas)
        self.llamadas = 0
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._crear))

    def _crear(self, **kwargs):
        self.llamadas += 1
        if not self._respuestas:
            raise AssertionError("El agente pidió más respuestas de las previstas")
        return self._respuestas.pop(0)
    
def _respuesta(mensaje):
    return SimpleNamespace(choices=[SimpleNamespace(message=mensaje)])

def texto(contenido):
    """Respuesta del modelo con texto, sin herramientas."""
    return _respuesta(SimpleNamespace(content=contenido, tool_calls=None))

def pide(nombre, argumentos):
    """Respuesta del modelo que pide ejecutar una herramienta."""
    if not isinstance(argumentos, str):
        argumentos = json.dumps(argumentos)
    llamada = SimpleNamespace(
        id="llamada-1", function=SimpleNamespace(name=nombre, arguments=argumentos)
    )
    return _respuesta(SimpleNamespace(content=None, tool_calls=[llamada]))
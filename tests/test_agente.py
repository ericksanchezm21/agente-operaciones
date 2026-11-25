import json

from agente_operaciones import herramientas
from agente_operaciones.agente import Agente
from tests.falsos import ClienteFalso, pide, texto


def _mensajes_herramienta(agente):
    return [mensaje for mensaje in agente.historial if mensaje["role"] == "tool"]


def test_respuesta_directa_no_usa_herramientas(config):
    contenido = "La tienda abre a las nueve."
    cliente = ClienteFalso(texto(contenido))
    agente = Agente(config, cliente)

    resultado = agente.responder("¿A qué hora abre la tienda?")

    assert resultado == contenido
    assert cliente.llamadas == 1
    assert not _mensajes_herramienta(agente)
    assert herramientas.PEDIDOS == []


def test_pedido_valido_se_ejecuta_y_devuelve_respuesta_final(config):
    contenido = "Pedido registrado."
    cliente = ClienteFalso(
        pide(
            "registrar_pedido",
            {
                "cliente": "Ana",
                "items": [{"producto_id": "cuaderno-a4", "cantidad": 2}],
            },
        ),
        texto(contenido),
    )
    agente = Agente(config, cliente)

    resultado = agente.responder("Registra el pedido confirmado de Ana.")

    llamadas = [
        llamada
        for mensaje in agente.historial
        for llamada in mensaje.get("tool_calls", [])
    ]
    mensajes_herramienta = _mensajes_herramienta(agente)

    assert resultado == contenido
    assert cliente.llamadas == 2
    assert [llamada["function"]["name"] for llamada in llamadas] == [
        "registrar_pedido"
    ]
    assert len(mensajes_herramienta) == 1
    assert json.loads(mensajes_herramienta[0]["content"])["ok"] is True
    assert len(herramientas.PEDIDOS) == 1
    assert herramientas.PEDIDOS[0]["cliente"] == "Ana"
    assert herramientas.PEDIDOS[0]["items"] == [
        {"producto_id": "cuaderno-a4", "cantidad": 2}
    ]


def test_argumentos_no_json_devuelven_error_ilegible_al_modelo(config):
    cliente = ClienteFalso(
        pide("registrar_pedido", '{"cliente":'),
        texto("No pude procesar la solicitud."),
    )
    agente = Agente(config, cliente)

    agente.responder("Registra un pedido.")

    llamadas = [
        llamada
        for mensaje in agente.historial
        for llamada in mensaje.get("tool_calls", [])
    ]
    mensajes_herramienta = _mensajes_herramienta(agente)

    assert cliente.llamadas == 2
    assert [llamada["function"]["name"] for llamada in llamadas] == [
        "registrar_pedido"
    ]
    assert len(mensajes_herramienta) == 1
    assert "ilegibles" in mensajes_herramienta[0]["content"].lower()
    assert herramientas.PEDIDOS == []


def test_herramienta_inexistente_devuelve_error_al_modelo(config):
    cliente = ClienteFalso(
        pide("herramienta_desconocida", {}),
        texto("No pude completar la solicitud."),
    )
    agente = Agente(config, cliente)

    agente.responder("Usa la herramienta solicitada.")

    llamadas = [
        llamada
        for mensaje in agente.historial
        for llamada in mensaje.get("tool_calls", [])
    ]
    mensajes_herramienta = _mensajes_herramienta(agente)

    assert cliente.llamadas == 2
    assert [llamada["function"]["name"] for llamada in llamadas] == [
        "herramienta_desconocida"
    ]
    assert len(mensajes_herramienta) == 1
    assert "no existe" in mensajes_herramienta[0]["content"].lower()

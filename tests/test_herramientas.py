import json

from agente_operaciones import herramientas
from agente_operaciones.herramientas import registrar_pedido

def test_pedido_valido_se_registra(config):
    items = [{"producto_id": "cuaderno-a4", "cantidad": 2}]
    resultado = json.loads(registrar_pedido(config, "Ana", items))
    assert resultado["ok"] is True
    assert resultado["total"] == 9.0
    assert len(herramientas.PEDIDOS) == 1

def test_el_pedido_queda_guardado(config):
    items = [{"producto_id": "cuaderno-a4", "cantidad": 2}]
    registrar_pedido(config, "Ana", items)
    assert len(herramientas.PEDIDOS) == 1
    assert herramientas.PEDIDOS[0]["cliente"] == "Ana"
import json
from agente_operaciones import config, herramientas
from agente_operaciones.herramientas import registrar_pedido

def registrar(config, producto, cantidad):
    items = [{"producto_id": producto, "cantidad": cantidad}]
    return json.loads(registrar_pedido(config, "Ana", items))

def test_el_total_conserva_los_decimales(config):
    assert registrar(config, "cuaderno-a4", 3)["total"] == 13.5

def test_un_producto_inexistente_se_rechaza_aunque_haya_otros_validos(config):
    items = [
    {"producto_id": "resma-papel", "cantidad": 1},
    {"producto_id": "unicornio", "cantidad": 1},
    ]
    assert "error" in json.loads(registrar_pedido(config, "Ana", items))

def test_dos_renglones_del_mismo_producto_cuentan_como_uno(config):
    config = config.model_copy(update={"max_lineas_pedido": 1})
    items = [
    {"producto_id": "cuaderno-a4", "cantidad": 1},
    {"producto_id": "cuaderno-a4", "cantidad": 1},
    ]
    assert json.loads(registrar_pedido(config, "Ana", items))["ok"] is True
import json

import pytest

from agente_operaciones import config, herramientas
from agente_operaciones.herramientas import registrar_pedido, consultar_producto


def pedir(config, cliente, producto, cantidad):
    items = [{"producto_id": producto, "cantidad": cantidad}]
    return json.loads(registrar_pedido(config, cliente, items))


def test_pedido_valido_se_registra(config):
    items = [{"producto_id": "cuaderno-a4", "cantidad": 2}]
    resultado = json.loads(registrar_pedido(config, "Ana", items))
    assert resultado["ok"] is True
    assert resultado["total"] == 9.0
    assert len(herramientas.PEDIDOS) == 1


def test_pedido_con_dos_productos_suma_correctamente(config):
    items = [
        {"producto_id": "cuaderno-a4", "cantidad": 2},
        {"producto_id": "boligrafos-caja", "cantidad": 1},
    ]

    resultado = json.loads(registrar_pedido(config, "Ana", items))

    assert resultado["ok"] is True
    assert resultado["total"] == 15.0
    assert herramientas.PEDIDOS[0]["items"] == items
    assert herramientas.PEDIDOS[0]["total"] == 15.0


def test_el_pedido_queda_guardado(config):
    items = [{"producto_id": "cuaderno-a4", "cantidad": 2}]
    registrar_pedido(config, "Ana", items)
    assert len(herramientas.PEDIDOS) == 1
    assert herramientas.PEDIDOS[0]["cliente"] == "Ana"


@pytest.mark.parametrize(
    ("cliente", "producto", "cantidad"),
    [
        ("Ana", "cuaderno-a4", 0),
        ("Ana", "cuaderno-a4", -5),
        ("Ana", "cuadernoa4", "tres"),
        ("Ana", "cuaderno-a4", 2.5),
        ("Ana", "cuaderno-a4", 1000000),
        ("Ana", "cuaderno-a4", 1),
        ("Ana", "lapiz-hb", 1),
        ("Ana", "organizador-escritorio", 1),
        ("", "cuaderno-a4", 2),
        ("a" * 81, "cuaderno-a4", 2),
    ],
)
def test_pedido_invalido_devuelve_error_y_no_registra(
    config, cliente, producto, cantidad
):
    resultado = pedir(config, cliente, producto, cantidad)

    assert "error" in resultado
    assert herramientas.PEDIDOS == []

def test_limite_de_cantidad_en_el_borde(config):
    assert pedir(config, "Ana", "cuaderno-a4", 20)["ok"] is True
    assert "error" in pedir(config, "Ana", "cuaderno-a4", 21)

@pytest.mark.parametrize(
    "nombre, esperado",
    [
    ("cuaderno", "Cuaderno A4"),
    (" CUADERNO ", "Cuaderno A4"),
    ("unicornio", None),
    ("", None),
    ],
)
def test_consultar_producto(nombre, esperado):
    resultado = json.loads(consultar_producto(nombre))
    if esperado is None:
        assert "error" in resultado
    else:
        assert resultado["nombre"] == esperado
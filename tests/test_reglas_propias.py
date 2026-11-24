import json

from agente_operaciones import herramientas
from agente_operaciones.catalogo import CATALOGO


def pedir(config, items):
    return json.loads(herramientas.registrar_pedido(config, "Ana", items))


def test_cantidad_maxima_por_item_en_el_limite_y_superada(config):
    config = config.model_copy(update={"cantidad_maxima_por_item": 2})

    en_el_limite = pedir(
        config, [{"producto_id": "cuaderno-a4", "cantidad": 2}]
    )
    superada = pedir(
        config, [{"producto_id": "cuaderno-a4", "cantidad": 3}]
    )

    assert en_el_limite["ok"] is True
    assert "error" in superada


def test_pedido_minimo_en_el_limite_y_por_debajo(config):
    cantidad_en_el_limite = 2
    total_minimo = CATALOGO["cuaderno-a4"].precio * cantidad_en_el_limite
    config = config.model_copy(update={"pedido_minimo": total_minimo})

    en_el_limite = pedir(
        config,
        [{"producto_id": "cuaderno-a4", "cantidad": cantidad_en_el_limite}],
    )
    por_debajo = pedir(
        config, [{"producto_id": "cuaderno-a4", "cantidad": 1}]
    )

    assert en_el_limite["ok"] is True
    assert "error" in por_debajo


def test_max_lineas_pedido_en_el_limite_y_superado(config):
    config = config.model_copy(update={"max_lineas_pedido": 2})
    dos_productos = [
        {"producto_id": "cuaderno-a4", "cantidad": 1},
        {"producto_id": "boligrafos-caja", "cantidad": 1},
    ]
    tres_productos = dos_productos + [
        {"producto_id": "resma-papel", "cantidad": 1}
    ]

    en_el_limite = pedir(config, dos_productos)
    superado = pedir(config, tres_productos)

    assert en_el_limite["ok"] is True
    assert "error" in superado


def test_monto_maximo_en_el_limite_y_superado(config):
    items_en_el_limite = [
        {"producto_id": "boligrafos-caja", "cantidad": 2},
        {"producto_id": "resma-papel", "cantidad": 1},
    ]
    monto_maximo = (
        CATALOGO["boligrafos-caja"].precio * 2
        + CATALOGO["resma-papel"].precio
    )
    config = config.model_copy(update={"monto_maximo_pedido": monto_maximo})

    en_el_limite = pedir(config, items_en_el_limite)
    superado = pedir(
        config,
        items_en_el_limite
        + [{"producto_id": "cuaderno-a4", "cantidad": 1}],
    )

    assert en_el_limite["ok"] is True
    assert "error" in superado


def test_cambiar_regla_cambia_el_resultado_sin_cambiar_el_codigo(config):
    items = [
        {"producto_id": "cuaderno-a4", "cantidad": 1},
        {"producto_id": "boligrafos-caja", "cantidad": 1},
        {"producto_id": "resma-papel", "cantidad": 1},
    ]
    config_permisiva = config.model_copy(update={"max_lineas_pedido": 3})
    config_restrictiva = config.model_copy(update={"max_lineas_pedido": 2})

    permitido = pedir(config_permisiva, items)
    rechazado = pedir(config_restrictiva, items)

    assert permitido["ok"] is True
    assert "error" in rechazado


def test_pedido_rechazado_no_se_registra(config):
    config = config.model_copy(update={"max_lineas_pedido": 1})
    items = [
        {"producto_id": "cuaderno-a4", "cantidad": 1},
        {"producto_id": "boligrafos-caja", "cantidad": 1},
    ]

    resultado = pedir(config, items)

    assert "error" in resultado
    assert herramientas.PEDIDOS == []

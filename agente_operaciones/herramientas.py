import json
from agente_operaciones.catalogo import CATALOGO
from agente_operaciones.config import Configuracion
from agente_operaciones.modelos import Pedido
from pydantic import ValidationError


PEDIDOS: list[dict] = []

def _resultado(datos: dict) -> str:
    return json.dumps(datos, ensure_ascii=False)

def _error(mensaje: str) -> str:
    return json.dumps({"error": mensaje}, ensure_ascii=False)

def consultar_producto(nombre: str) -> str:
    """Busca un producto por nombre y devuelve su precio y disponibilidad."""
    buscado = nombre.strip().lower()
    if not buscado:
        return _error("Falta el nombre del producto.")
    for producto in CATALOGO.values():
        if buscado in producto.nombre.lower():
            return _resultado(producto.model_dump())
    return _error(f"No existe un producto parecido a '{nombre}'. Favor de solicitar otro producto.")


def registrar_pedido(config: Configuracion, cliente: str, items: list[dict]) -> str:
    """Valida y registra un pedido, o devuelve el primer error encontrado."""
    try:
        pedido = Pedido.model_validate({"cliente": cliente, "items": items})
    except ValidationError as exc:
        error = exc.errors(include_url=False)[0]
        campo = ".".join(str(parte) for parte in error["loc"])
        return _error(f"Campo '{campo}': {error['msg']}")

    total = 0.0
    for indice, item in enumerate(pedido.items):
        producto = CATALOGO.get(item.producto_id)
        if producto is None:
            return _error(f"El producto '{item.producto_id}' no existe.")
        if not producto.disponible:
            return _error(f"El producto '{item.producto_id}' no está disponible.")
        if item.cantidad > config.cantidad_maxima_por_item:
            return _error(
                f"El campo 'items.{indice}.cantidad' supera "
                f"el máximo de {config.cantidad_maxima_por_item}."
            )
        total += producto.precio * item.cantidad

    if total < config.pedido_minimo:
        return _error(
            f"El total del pedido ({total}) es inferior al mínimo de "
            f"{config.pedido_minimo}."
        )

    numero = len(PEDIDOS) + 1
    PEDIDOS.append(
        {
            "numero": numero,
            "cliente": pedido.cliente,
            "items": [item.model_dump() for item in pedido.items],
            "total": total,
        }
    )
    return _resultado({"ok": True, "pedido": numero, "total": total})
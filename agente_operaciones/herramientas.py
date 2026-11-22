import json
from agente_operaciones.catalogo import CATALOGO

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
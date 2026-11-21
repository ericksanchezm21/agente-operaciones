from .modelos import Producto


CATALOGO: dict[str, Producto] = {
    "cuaderno-a4": Producto(
        id="cuaderno-a4",
        nombre="Cuaderno A4",
        precio=4.5,
    ),
    "boligrafos-caja": Producto(
        id="boligrafos-caja",
        nombre="Caja de bolígrafos",
        precio=6.0,
    ),
    "resma-papel": Producto(
        id="resma-papel",
        nombre="Resma de papel",
        precio=8.0,
    ),
    "organizador-escritorio": Producto(
        id="organizador-escritorio",
        nombre="Organizador de escritorio",
        precio=12.0,
        disponible=False,
    ),
}

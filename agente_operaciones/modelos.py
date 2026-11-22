from pydantic import BaseModel, Field


class Producto(BaseModel):
    id: str
    nombre: str
    precio: float = Field(gt=0)
    disponible: bool = True


class ItemPedido(BaseModel):
    producto_id: str = Field(min_length=1)
    cantidad: int = Field(ge=1)


class Pedido(BaseModel):
    cliente: str = Field(min_length=1, max_length=80)
    items: list[ItemPedido] = Field(min_length=1)

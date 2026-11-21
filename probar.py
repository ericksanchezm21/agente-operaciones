from pydantic import ValidationError
from agente_operaciones.modelos import Pedido

def probar(datos):
    try:
        p = Pedido.model_validate(datos)
        print("OK", p)
    except ValidationError as e:
        for err in e.errors():
            print(".".join(map(str, err["loc"])) + ": " + err["msg"])

            
probar({"cliente": "Ana", "items": [{"producto_id": "cuaderno-a4", "cantidad": 2}]})
probar({"cliente": "", "items": [{"producto_id": "cuaderno-a4", "cantidad": 2}]})
probar({"cliente": "Ana", "items": []})
probar({"cliente": "Ana", "items": [{"producto_id": "cuaderno-a4", "cantidad": "tres"}]})
probar({"cliente": "Ana", "items": [{"producto_id": "cuaderno-a4", "cantidad": "3"}]})
probar({"cliente": "Ana", "items": [{"producto_id": "cuaderno-a4"}]})
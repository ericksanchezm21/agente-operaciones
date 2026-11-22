from pydantic import ValidationError

from agente_operaciones.agente import Agente
from agente_operaciones.config import cargar_configuracion


def main() -> None:
    try:
        config = cargar_configuracion()
        agente = Agente(config)
    except (ValidationError, AttributeError, TypeError, ValueError):
        print(
            "No se pudo iniciar el agente porque falta o es inválido un dato de "
            "configuración. Verifica la configuración e inténtalo de nuevo."
        )
        return

    print("Suministros Norte: ¡Hola! ¿En qué puedo ayudarte? Escribe 'salir' para terminar.")
    while True:
        try:
            mensaje = input("Tú: ")
        except EOFError:
            print("\nHasta luego.")
            return
        if mensaje.strip().lower() == "salir":
            print("Hasta luego.")
            return
        print(f"Agente: {agente.responder(mensaje)}")


if __name__ == "__main__":
    main()

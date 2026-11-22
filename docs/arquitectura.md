# Arquitectura del agente

```mermaid
flowchart LR
    cliente[Cliente] -->|mensaje| main[main.py]
    main -->|carga configuración e inicia conversación| agente[Agente]

    agente -->|mensajes e instrucciones HERRAMIENTAS| groq[Modelo de Groq]
    groq -->|respuesta o llamada a herramienta| agente

    agente -->|nombre y argumentos JSON| ejecutar[ejecutar]
    ejecutar -->|consultar_producto| consultar[consultar_producto]
    consultar --> catalogo[(CATALOGO)]
    catalogo -->|producto o error JSON| ejecutar

    ejecutar -->|registrar_pedido| registrar[registrar_pedido]
    registrar --> pydantic[Validación Pydantic<br/>Pedido e ItemPedido]
    pydantic -->|válido| reglas[Reglas de negocio<br/>producto existente y disponible<br/>cantidad por ítem dentro del límite<br/>total mínimo<br/>productos distintos dentro del límite<br/>total máximo]
    pydantic -->|inválido| error[Error JSON<br/>sin modificar PEDIDOS]
    reglas -->|incumple alguna regla| error
    reglas -->|cumple todas| pedidos[(PEDIDOS en memoria)]
    pedidos -->|pedido y total en JSON| ejecutar

    ejecutar -->|resultado de herramienta| agente
    agente -->|muestra [herramienta] y solicita respuesta final| groq
    groq -->|respuesta final| agente
    agente -->|respuesta en consola| main
    main -->|respuesta| cliente
    main -.->|repite hasta que escriba salir| cliente
```

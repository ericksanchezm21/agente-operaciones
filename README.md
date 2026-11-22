# Suministros Norte — Agente de Operaciones

## Descripción del proyecto

Suministros Norte es una tienda en línea ficticia de papelería y artículos de oficina. Este proyecto implementa un agente de operaciones desarrollado en Python, que utiliza inteligencia artificial mediante la API de Groq para atender consultas de clientes y gestionar pedidos.

### Funcionalidades principales

- **Consulta de productos:** Permite consultar los productos del catálogo, sus precios y disponibilidad.
- **Registro de pedidos:** Permite registrar pedidos después de recibir la confirmación explícita del cliente.
- **Validación de pedidos:** Comprueba que los productos existan, estén disponibles y que las cantidades solicitadas sean válidas.
- **Reglas del negocio:** Aplica límites configurables de cantidad por producto, monto mínimo, número máximo de productos distintos y monto máximo por pedido.
- **Gestión de errores:** Devuelve mensajes claros cuando una consulta o pedido incumple alguna validación.
- **Memoria de conversación:** Mantiene el historial durante la ejecución para dar continuidad a las interacciones.
- **Almacenamiento temporal:** Los pedidos se guardan en memoria durante la ejecución del programa, sin utilizar una base de datos.

## Ejecución del agente

Para iniciar el agente desde la terminal, ejecuta el siguiente comando en la raíz del proyecto:

```bash
uv run main.py
```

El agente iniciará una conversación interactiva por consola. Los clientes podrán consultar productos y solicitar pedidos, que serán registrados únicamente después de su confirmación.

Para finalizar la conversación, escribe `salir`.

**Nota:** Antes de ejecutar el agente, asegúrate de tener configurado el archivo `.env` con las variables necesarias, incluida la clave de acceso a Groq.

## Verificación del proyecto

Para ejecutar el script de verificación y comprobar el funcionamiento de las reglas del negocio, utiliza:

```bash
uv run verificar_semana1.py
```

Este script permite verificar el comportamiento del proyecto según las pruebas implementadas.

## Tecnologías utilizadas

- **Python:** Lenguaje principal del proyecto.
- **uv:** Gestión de dependencias y ejecución.
- **Groq API:** Procesamiento de lenguaje natural mediante modelos de inteligencia artificial.
- **Pydantic:** Validación de datos y configuración.

## Consideraciones

El proyecto tiene fines educativos y utiliza un catálogo de productos ficticio. Los pedidos se almacenan temporalmente en memoria y se pierden al finalizar la ejecución del programa. Las reglas del negocio pueden modificarse mediante las variables de configuración, sin necesidad de alterar la lógica del agente.
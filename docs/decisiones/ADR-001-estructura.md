# ADR-001: Por qué organicé el proyecto así

## Contexto
Necesito guardar los pedidos mientras el programa está abierto.
## Decisión
Los guardo en una lista de Python llamada PEDIDOS.
## Alternativas que descarté
Un archivo de texto: es más lento de leer y de probar.
## Consecuencias
Al cerrar el programa los pedidos se pierden. Es suficiente por ahora.
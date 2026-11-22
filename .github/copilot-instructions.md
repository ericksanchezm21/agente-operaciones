# Instrucciones permanentes

- Responde siempre en español y de forma breve.
- Ejecuta el proyecto y sus comandos con `uv run`; agrega dependencias con `uv add`.
- Mantén todo el código en `agente_operaciones/`; `main.py` solo debe iniciar el programa.
- Obtén toda la configuración de `agente_operaciones/config.py`; nunca incluyas claves ni reglas en el código.
- Nunca leas, muestres ni modifiques `.env`.
- Valida con los modelos de `modelos.py` todo dato entrante antes de usarlo.
- Las herramientas devuelven texto JSON; representa los fallos como `{"error": "mensaje claro"}`, no como excepciones.
- Antes de editar, explica qué vas a cambiar; no modifiques lo que ya funciona.
- No modifiques `verificar_semana1.py`.

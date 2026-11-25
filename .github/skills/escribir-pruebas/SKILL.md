---
name: escribir-pruebas
description: Úsala al crear, ampliar, corregir o revisar pruebas automatizadas del proyecto agente_operaciones, o cuando se modifique código que deba quedar cubierto por pruebas.
---

# Escribir pruebas

## Ubicación y nomenclatura

- Ubica las pruebas automatizadas en `tests/`.
- Nombra los archivos `test_<modulo>.py`, por ejemplo `test_agente.py` o `test_herramientas.py`.
- Nombra las funciones de prueba `test_<comportamiento>`, describiendo el resultado esperado.
- Mantén cada prueba enfocada en un comportamiento observable. Agrupa entradas relacionadas con `pytest.mark.parametrize` cuando corresponda.
- Cada prueba debe tener tres partes, en este orden: preparar, actuar y comprobar (Arrange, Act, Assert).

## Qué utilizar

- Reutiliza los fixtures de `tests/conftest.py`. El fixture `config` proporciona una configuración de prueba que no necesita leer `.env`; `pedidos_limpios` limpia `PEDIDOS` antes y después de cada prueba automáticamente.
- Usa `pytest.mark.parametrize` para probar varias entradas del mismo comportamiento sin duplicar la estructura de la prueba.
- Para probar el agente sin llamadas reales a Groq, reutiliza `ClienteFalso`, `texto` y `pide` desde `tests/falsos.py`.
- No crees fixtures ni clientes falsos duplicados si ya existe un componente reutilizable.

## Qué comprobar

- Comprueba el comportamiento observable del código: resultado devuelto, llamadas al modelo, herramientas invocadas, mensajes de herramienta y efectos secundarios como pedidos guardados.
- Incluye casos exitosos, entradas inválidas y valores límite relevantes para el comportamiento probado.
- En respuestas generadas por el modelo, evita depender de frases completas. Comprueba el resultado proporcionado por el cliente falso o indicadores semánticos estables; exige texto exacto solo cuando ese texto sea parte explícita del contrato.
- En casos inválidos, comprueba el error esperado y que no ocurran efectos secundarios no deseados.

## Antes de terminar

1. Ejecuta `uv run pytest` y revisa el resultado.
2. Para comprobar que una prueba detecta una regresión, modifica temporalmente una sola línea del código de producción relacionada con el comportamiento probado y ejecuta la prueba correspondiente. Confirma que falle por la regresión esperada.
3. Restaura inmediatamente la línea original, sin descartar otros cambios existentes del usuario.
4. Vuelve a ejecutar `uv run pytest` y confirma que todas las pruebas pasan.
5. Comprueba que no quede ninguna modificación temporal en el código de producción.
6. No modifiques el código de `agente_operaciones/` al escribir pruebas, salvo que se solicite explícitamente. Los cambios temporales para comprobar la efectividad de las pruebas deben restaurarse.

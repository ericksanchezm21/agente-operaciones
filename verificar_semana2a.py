"""Verifica la Práctica 2A (Probar). Úsalo desde la raíz de TU proyecto:

    uv run python verificar_semana2a.py

No llama a Groq ni necesita clave. Modifica copias temporales; tu proyecto no se toca.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path.cwd()
MINIMO_PRUEBAS = 26
MINIMO_BUGS = 11

REFERENCIA = 'import json\nfrom pydantic import ValidationError\nfrom agente_operaciones.catalogo import CATALOGO\nfrom agente_operaciones.config import Configuracion\nfrom agente_operaciones.modelos import Pedido\n\nPEDIDOS: list[dict] = []\n\n\ndef _resultado(datos: dict) -> str:\n    return json.dumps(datos, ensure_ascii=False)\n\n\ndef _error(mensaje: str) -> str:\n    return json.dumps({"error": mensaje}, ensure_ascii=False)\n\n\ndef consultar_producto(nombre: str) -> str:\n    """Busca un producto por nombre y devuelve su precio y disponibilidad."""\n    buscado = nombre.strip().lower()\n    if not buscado:\n        return _error("Falta el nombre del producto.")\n    for producto in CATALOGO.values():\n        if buscado in producto.nombre.lower():\n            return _resultado(producto.model_dump())\n    return _error(f"No existe un producto parecido a \'{nombre}\'.")\n\n\ndef registrar_pedido(config: Configuracion, cliente: str, items: list[dict]) -> str:\n    """Valida un pedido (forma y reglas del negocio) y lo registra si es correcto."""\n    try:\n        pedido = Pedido.model_validate({"cliente": cliente, "items": items})\n    except ValidationError as e:\n        detalle = "; ".join(\n            f"{\'.\'.join(map(str, err[\'loc\']))}: {err[\'msg\']}" for err in e.errors()\n        )\n        return _error(f"El pedido no es válido. {detalle}")\n    if len({item.producto_id for item in pedido.items}) > config.max_lineas_pedido:\n        return _error(\n            f"Un pedido admite como máximo {config.max_lineas_pedido} productos distintos."\n        )\n    total = 0.0\n    for item in pedido.items:\n        producto = CATALOGO.get(item.producto_id)\n        if producto is None:\n            return _error(f"El producto \'{item.producto_id}\' no existe.")\n        if not producto.disponible:\n            return _error(f"\'{producto.nombre}\' no está disponible hoy.")\n        if item.cantidad > config.cantidad_maxima_por_item:\n            return _error(\n                f"La cantidad máxima por producto es {config.cantidad_maxima_por_item}."\n            )\n        total += producto.precio * item.cantidad\n    if total < config.pedido_minimo:\n        return _error(f"El pedido mínimo es {config.pedido_minimo:.2f}.")\n\n    if total > config.monto_maximo_pedido:\n        return _error(\n            f"El monto máximo por pedido es {config.monto_maximo_pedido:.2f}."\n        )\n\n    PEDIDOS.append(\n        {\n            "cliente": pedido.cliente,\n            "items": [i.model_dump() for i in pedido.items],\n            "total": total,\n        }\n    )\n    return _resultado({"ok": True, "pedido": len(PEDIDOS), "total": round(total, 2)})\n'

BUGS = [('b01', 'El máximo por producto deja pasar una cantidad de más', 'item.cantidad > config.cantidad_maxima_por_item', 'item.cantidad >= config.cantidad_maxima_por_item'), ('b02', 'El pedido mínimo rechaza justo el mínimo', 'total < config.pedido_minimo', 'total <= config.pedido_minimo'), ('b03', 'El total ignora la cantidad', 'producto.precio * item.cantidad', 'producto.precio'), ('b04', 'Se aceptan productos no disponibles', 'if not producto.disponible:', 'if False:'), ('b05', 'La consulta distingue mayúsculas', 'buscado = nombre.strip().lower()', 'buscado = nombre.strip()'), ('b06', 'El número de pedido empieza en cero', '"pedido": len(PEDIDOS)', '"pedido": len(PEDIDOS) - 1'), ('b07', 'El total pierde los decimales', 'round(total, 2)', 'int(total)'), ('b08', 'El máximo de productos distintos rechaza justo el límite', '> config.max_lineas_pedido', '>= config.max_lineas_pedido'), ('b09', 'El monto máximo rechaza justo el límite', 'total > config.monto_maximo_pedido', 'total >= config.monto_maximo_pedido'), ('b10', 'Un producto inexistente se ignora en silencio', 'return _error(f"El producto \'{item.producto_id}\' no existe.")', 'continue'), ('b11', 'Dos renglones del mismo producto cuentan como dos productos distintos', 'len({item.producto_id for item in pedido.items})', 'len(pedido.items)'), ('b12', 'El pedido se guarda sin sus productos', '"items": [i.model_dump() for i in pedido.items]', '"items": []'), ('b13', 'El pedido se guarda con total en cero', '"total": total,', '"total": 0,')]

resultados = []


def revisar(nombre, condicion, ayuda=""):
    resultados.append((nombre, bool(condicion), ayuda))


def correr(comando, carpeta=None, tiempo=90):
    entorno = {k: v for k, v in os.environ.items() if k != "GROQ_API_KEY"}
    entorno["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        return subprocess.run(
            comando, cwd=carpeta or RAIZ, capture_output=True, text=True,
            timeout=tiempo, env=entorno,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(comando, 1, "", "Tiempo agotado")


def pytest(carpeta):
    return correr(["uv", "run", "pytest", "-q", "-x", "-p", "no:cacheprovider"], carpeta)


def leer(ruta):
    p = RAIZ / ruta
    return p.read_text(encoding="utf-8") if p.exists() else ""


# --- 1. Estructura -----------------------------------------------------------
for archivo in ["tests/conftest.py", "tests/falsos.py", ".github/copilot-instructions.md",
                ".github/skills/escribir-pruebas/SKILL.md"]:
    revisar(f"Existe {archivo}", (RAIZ / archivo).exists(), "Revisa la fase donde se crea.")
archivos_prueba = sorted((RAIZ / "tests").glob("test_*.py")) if (RAIZ / "tests").exists() else []
revisar("Hay al menos 3 archivos tests/test_*.py", len(archivos_prueba) >= 3,
        "Herramientas, agente y las pruebas del reto.")
codigo_tests = "\n".join(p.read_text(encoding="utf-8") for p in archivos_prueba)
revisar("Usas @pytest.mark.parametrize", "parametrize" in codigo_tests)
revisar("Usas un fixture con yield y autouse",
        "autouse=True" in leer("tests/conftest.py") and "yield" in leer("tests/conftest.py"))
revisar("Probaste al Agente con ClienteFalso",
        "ClienteFalso" in leer("tests/test_agente.py"), "Fase 4.")
skill = leer(".github/skills/escribir-pruebas/SKILL.md")
revisar("La skill tiene nombre y descripción",
        skill.startswith("---") and "name:" in skill and "description:" in skill)

# --- 2. El agente recibe su cliente ----------------------------------------
comprobacion = (
    "import inspect;from agente_operaciones.agente import Agente;"
    "print('cliente' in inspect.signature(Agente.__init__).parameters)"
)
salida = correr(["uv", "run", "python", "-c", comprobacion])
revisar("Agente(config, cliente=...) recibe el cliente", salida.stdout.strip().endswith("True"),
        "Fase 4: el Agente no debe crear Groq adentro cuando se le pasa un cliente.")

# --- 3. La suite --------------------------------------------------------------
tr = correr(["uv", "run", "pytest", "-q", "-p", "no:cacheprovider"])
revisar("uv run pytest termina en verde, sin clave ni red", tr.returncode == 0,
        (tr.stdout + tr.stderr)[-300:])
m = re.search(r"(\d+) passed", tr.stdout)
cuantas = int(m.group(1)) if m else 0
revisar(f"Hay al menos {MINIMO_PRUEBAS} pruebas (tienes {cuantas})", cuantas >= MINIMO_PRUEBAS)

# --- 4. Cazador de bugs ----------------------------------------------------------
def copia_con(fuente):
    carpeta = Path(tempfile.mkdtemp(prefix="cazador_"))
    destino = carpeta / "p"
    shutil.copytree(RAIZ, destino, ignore=shutil.ignore_patterns(
        ".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache", ".env"))
    (destino / "agente_operaciones" / "herramientas.py").write_text(fuente, encoding="utf-8")
    return carpeta, destino


carpeta, destino = copia_con(REFERENCIA)
if (RAIZ / ".venv").exists():
    os.symlink(RAIZ / ".venv", destino / ".venv")
base = pytest(destino)
revisar("Tus pruebas pasan con la versión correcta de herramientas.py",
        base.returncode == 0, (base.stdout + base.stderr)[-300:])
shutil.rmtree(carpeta, ignore_errors=True)

atrapados = []
if base.returncode == 0:
    for clave, descripcion, viejo, nuevo in BUGS:
        carpeta, destino = copia_con(REFERENCIA.replace(viejo, nuevo, 1))
        if (RAIZ / ".venv").exists():
            os.symlink(RAIZ / ".venv", destino / ".venv")
        r = pytest(destino)
        if r.returncode != 0 and "Tiempo agotado" not in r.stderr:
            atrapados.append(clave)
        shutil.rmtree(carpeta, ignore_errors=True)
    print("\nCazador de bugs: pistas de los que se escaparon")
    for clave, descripcion, _, _ in BUGS:
        if clave not in atrapados:
            print(f"  Se escapó: {descripcion}")
revisar(f"Cazador de bugs: atrapaste {len(atrapados)} de {len(BUGS)} (mínimo {MINIMO_BUGS})",
        len(atrapados) >= MINIMO_BUGS,
        "Escribe pruebas para las pistas de arriba y vuelve a ejecutar.")

# --- 5. Git ---------------------------------------------------------------------
rama = correr(["git", "branch", "--show-current"]).stdout.strip()
revisar("Estás en la rama semana2-pruebas", rama == "semana2-pruebas", f"Rama actual: {rama}")
commits = correr(["git", "rev-list", "--count", "HEAD"]).stdout.strip()
revisar("Al menos 6 commits en la historia", commits.isdigit() and int(commits) >= 6,
        f"Tienes {commits}.")
sucio = correr(["git", "status", "--porcelain"]).stdout.strip()
revisar("No hay cambios sin guardar", sucio == "", "Haz commit de lo pendiente.")
claves = correr(["git", "grep", "-lE", "gsk_[A-Za-z0-9]{20,}", "HEAD"]).stdout.strip()
revisar("Ninguna clave gsk_ en Git", claves == "")

# --- Resumen -----------------------------------------------------------------------
print()
fallos = 0
for nombre, ok, ayuda in resultados:
    print(("✅ " if ok else "❌ ") + nombre)
    if not ok:
        fallos += 1
        if ayuda:
            print("     ->", str(ayuda).strip().replace("\n", " ")[:300])
print(f"\n{len(resultados) - fallos}/{len(resultados)} comprobaciones en verde.")
sys.exit(1 if fallos else 0)

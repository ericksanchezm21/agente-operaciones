"""Verificación de la Práctica 1 (Formación 2). Ejecuta: uv run verificar_semana1.py"""
import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

resultados: list[tuple[bool, str]] = []


def comprobar(descripcion: str, condicion) -> None:
    try:
        ok = bool(condicion() if callable(condicion) else condicion)
    except Exception as e:  # noqa: BLE001
        ok = False
        descripcion += f" (error: {type(e).__name__}: {e})"
    resultados.append((ok, descripcion))
    print(("✓ " if ok else "✗ ") + descripcion)


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True, cwd=RAIZ)
    return r.stdout.strip()


print("\n== Git y secretos ==")
comprobar("Trabajas en una rama f2/...", lambda: git("branch", "--show-current").startswith("f2/"))
comprobar("Tienes al menos 8 commits", lambda: int(git("rev-list", "--count", "HEAD") or 0) >= 8)
comprobar(".env está ignorado y no se sigue en Git", lambda: git("check-ignore", ".env") == ".env" and git("ls-files", ".env") == "")
comprobar("Existe .env.example", lambda: (RAIZ / ".env.example").exists())
comprobar("Ninguna clave real de Groq en archivos de Git", lambda: git("grep", "-n", "gsk" + "_") == "")

print("\n== Instrucciones, documentación y decisiones ==")
instr = RAIZ / ".github" / "copilot-instructions.md"
comprobar("Existe .github/copilot-instructions.md con al menos 6 líneas", lambda: instr.exists() and len([l for l in instr.read_text(encoding="utf-8").splitlines() if l.strip()]) >= 6)
arq = RAIZ / "docs" / "arquitectura.md"
comprobar("docs/arquitectura.md incluye un diagrama mermaid", lambda: arq.exists() and "```mermaid" in arq.read_text(encoding="utf-8"))
comprobar("Existe docs/decisiones/ADR-001*.md", lambda: any((RAIZ / "docs" / "decisiones").glob("ADR-001*.md")))

print("\n== Configuración ==")
from agente_operaciones.config import Configuracion  # noqa: E402

clave = os.environ.pop("GROQ_API_KEY", None)


def sin_clave_falla() -> bool:
    try:
        Configuracion(_env_file=None)
    except Exception:  # noqa: BLE001
        return True
    return False


comprobar("Sin GROQ_API_KEY la configuración falla al arrancar", sin_clave_falla)
if clave:
    os.environ["GROQ_API_KEY"] = clave


def claves_env_example() -> int:
    lineas = (RAIZ / ".env.example").read_text(encoding="utf-8").splitlines()
    return len([l for l in lineas if "=" in l and not l.strip().startswith("#")])


comprobar(".env.example documenta al menos 6 variables (4 base + 2 reglas del negocio)", lambda: claves_env_example() >= 6)

print("\n== Modelos (Pydantic) ==")
from pydantic import ValidationError  # noqa: E402

from agente_operaciones.catalogo import CATALOGO  # noqa: E402
from agente_operaciones.modelos import ItemPedido, Pedido  # noqa: E402


def rechaza(**datos) -> bool:
    try:
        Pedido.model_validate(datos)
    except ValidationError:
        return True
    return False


comprobar("El catálogo tiene al menos 3 productos y uno no disponible", lambda: len(CATALOGO) >= 3 and any(not p.disponible for p in CATALOGO.values()))
disponible = next(p for p in CATALOGO.values() if p.disponible)
no_disp = next((p for p in CATALOGO.values() if not p.disponible), None)
item_ok = {"producto_id": disponible.id, "cantidad": 1}
comprobar("Pedido acepta un pedido correcto", lambda: Pedido.model_validate({"cliente": "Ana", "items": [item_ok]}).items[0].cantidad == 1)
comprobar("Pedido rechaza cantidad 0", lambda: rechaza(cliente="Ana", items=[{"producto_id": disponible.id, "cantidad": 0}]))
comprobar("Pedido rechaza cantidad negativa", lambda: rechaza(cliente="Ana", items=[{"producto_id": disponible.id, "cantidad": -3}]))
comprobar("Pedido rechaza lista de items vacía", lambda: rechaza(cliente="Ana", items=[]))
comprobar("Pedido rechaza cliente vacío", lambda: rechaza(cliente="", items=[item_ok]))
comprobar("Pedido rechaza cliente de más de 80 caracteres", lambda: rechaza(cliente="x" * 81, items=[item_ok]))
comprobar("ItemPedido existe con producto_id y cantidad", lambda: ItemPedido(producto_id="a", cantidad=1).cantidad == 1)

print("\n== Herramienta registrar_pedido ==")
from agente_operaciones import herramientas  # noqa: E402


def cfg(**extra) -> Configuracion:
    return Configuracion(groq_api_key="prueba", _env_file=None, **extra)


def llamar(config, cliente, items) -> dict:
    return json.loads(herramientas.registrar_pedido(config, cliente, items))


herramientas.PEDIDOS.clear()
base = cfg(cantidad_maxima_por_item=3, pedido_minimo=0)
ok = llamar(base, "Ana", [item_ok])
comprobar("Un pedido válido se registra y devuelve ok y total", lambda: ok.get("ok") is True and "total" in ok and len(herramientas.PEDIDOS) == 1)
antes = len(herramientas.PEDIDOS)
comprobar("Un producto inexistente devuelve error y no registra", lambda: "error" in llamar(base, "Ana", [{"producto_id": "no-existe", "cantidad": 1}]) and len(herramientas.PEDIDOS) == antes)
if no_disp:
    comprobar("Un producto no disponible devuelve error y no registra", lambda: "error" in llamar(base, "Ana", [{"producto_id": no_disp.id, "cantidad": 1}]) and len(herramientas.PEDIDOS) == antes)
comprobar("Una cantidad 0 devuelve error (no lanza excepción) y no registra", lambda: "error" in llamar(base, "Ana", [{"producto_id": disponible.id, "cantidad": 0}]) and len(herramientas.PEDIDOS) == antes)
comprobar("Una cantidad sobre el máximo configurado devuelve error", lambda: "error" in llamar(base, "Ana", [{"producto_id": disponible.id, "cantidad": 4}]) and len(herramientas.PEDIDOS) == antes)
comprobar("La cantidad máxima sale de la configuración (con 5 sí pasa)", lambda: llamar(cfg(cantidad_maxima_por_item=5), "Ana", [{"producto_id": disponible.id, "cantidad": 4}]).get("ok") is True)
minimo = cfg(pedido_minimo=disponible.precio + 1)
antes = len(herramientas.PEDIDOS)
comprobar("Un pedido bajo el mínimo configurado devuelve error", lambda: "error" in llamar(minimo, "Ana", [item_ok]) and len(herramientas.PEDIDOS) == antes)
comprobar("consultar_producto responde con precio", lambda: "precio" in json.loads(herramientas.consultar_producto(disponible.nombre)))
comprobar("consultar_producto con algo que no existe devuelve error", lambda: "error" in json.loads(herramientas.consultar_producto("zzzz-no-existe")))

print("\n== Las dos reglas de Suministros Norte (Fase 11) ==")
disponibles = [p for p in CATALOGO.values() if p.disponible]
ids3 = [p.id for p in disponibles[:3]]
caro = max(disponibles, key=lambda p: p.precio)
tope = caro.precio * 2


def pedido_de(config, ids) -> dict:
    return llamar(config, "Ana", [{"producto_id": i, "cantidad": 1} for i in ids])


def variables_env_example() -> set[str]:
    lineas = (RAIZ / ".env.example").read_text(encoding="utf-8").splitlines()
    return {l.split("=")[0].strip() for l in lineas if "=" in l and not l.strip().startswith("#")}


comprobar("max_lineas_pedido existe en la configuración y vale 3 por defecto", lambda: cfg().max_lineas_pedido == 3)
antes = len(herramientas.PEDIDOS)
comprobar("Más productos distintos que max_lineas_pedido devuelve error y no registra", lambda: "error" in pedido_de(cfg(max_lineas_pedido=2), ids3) and len(herramientas.PEDIDOS) == antes)
comprobar("Con max_lineas_pedido=3 el mismo pedido sí se registra (el límite sale de la configuración)", lambda: pedido_de(cfg(max_lineas_pedido=3), ids3).get("ok") is True)
antes = len(herramientas.PEDIDOS)
comprobar("monto_maximo_pedido existe en la configuración y vale 200 por defecto", lambda: cfg().monto_maximo_pedido == 200)
comprobar("Un total sobre monto_maximo_pedido devuelve error y no registra", lambda: "error" in llamar(cfg(monto_maximo_pedido=tope), "Ana", [{"producto_id": caro.id, "cantidad": 3}]) and len(herramientas.PEDIDOS) == antes)
comprobar("Un total igual a monto_maximo_pedido se acepta (el límite sale de la configuración)", lambda: llamar(cfg(monto_maximo_pedido=tope), "Ana", [{"producto_id": caro.id, "cantidad": 2}]).get("ok") is True)
comprobar(".env.example documenta MAX_LINEAS_PEDIDO y MONTO_MAXIMO_PEDIDO", lambda: {"MAX_LINEAS_PEDIDO", "MONTO_MAXIMO_PEDIDO"} <= variables_env_example())

prueba = RAIZ / "probar_reglas.py"
comprobar("Existe probar_reglas.py", prueba.exists)


def reglas_pasan() -> bool:
    r = subprocess.run([sys.executable, str(prueba)], capture_output=True, text=True, cwd=RAIZ)
    return r.returncode == 0


comprobar("probar_reglas.py termina sin errores", lambda: prueba.exists() and reglas_pasan())

total = len(resultados)
buenos = sum(1 for ok_, _ in resultados if ok_)
print(f"\nResultado: {buenos} de {total} comprobaciones ✓")
if buenos != total:
    print("Revisa las líneas con ✗. La prueba manda.")
sys.exit(0 if buenos == total else 1)

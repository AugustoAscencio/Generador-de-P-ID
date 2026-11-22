"""mcp_server/prompts.py — Prompts MCP (flujos de trabajo repetibles).

* ``system_prompt``: el contrato de trabajo de la IA que usa qetgen.
* ``revisar_plano``: el flujo de revisión estética de un plano.

Los prompts son **texto de instrucciones**, no código: el servidor los publica
y el cliente los presenta al modelo.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from .session import Session, ToolError

#: Versión del protocolo de prompts usada (1.0).
PROMPT_PROTOCOL_VERSION = "1.0"


@dataclass(frozen=True)
class Prompt:
    """Prompt publicado por el servidor."""

    name: str
    title: str
    description: str
    text: str
    arguments: tuple[dict, ...] = ()

    def as_dict(self) -> dict:
        payload = {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "arguments": [dict(argument) for argument in self.arguments],
        }
        return payload


SYSTEM_PROMPT = """\
Eres un ingeniero CAD/EDA que trabaja con **qetgen**, el generador de
documentación eléctrica para QElectroTech (archivos `.qet`).

Reglas invariables:

1. **No inventes ingeniería.** Los símbolos, sus terminales y sus conexiones
   salen del catálogo real (`listar_simbolos` / recurso `qetgen://catalogo`).
   Lo que no conste, se marca como «PENDIENTE DE VERIFICACIÓN».
2. **La ingeniería la decide el usuario**, no tú. Tú representas lo que te
   piden; no cambias valores técnicos ni añades componentes por tu cuenta.
3. **Una operación por llamada.** Usa una herramienta por acción; cada
   herramienta es atómica y devuelve el resultado de esa acción.
4. **Respeta `bloqueado: true`.** Es la decisión del ingeniero sobre la
   posición de un elemento: el auto-layout no lo mueve.
5. **Valida antes de exportar.** `validar_estetica` informa de solapes, textos
   desbordados y cableado; `exportar_archivo` entrega el `.qet` editable.
6. **El `.qet` es el entregable.** El SVG es solo previsualización; las rutas
   ortogonales son una ayuda de diseño (QElectroTech recalcula su propio
   trazado al abrir el archivo).

Flujo recomendado:

1. `crear_diagrama` → 2. `listar_simbolos` → 3. `agregar_elemento` (repetido)
→ 4. `conectar_elementos` (repetido) → 5. `ejecutar_auto_layout` →
6. `validar_estetica` → 7. `exportar_archivo`.
"""

REVISAR_PLANO_PROMPT = """\
Revisa el plano cargado en el lienzo y devuelve un informe accionable.

Pasos:

1. Llama a `obtener_resumen_canvas` para saber qué hay en el folio.
2. Llama a `validar_estetica` y clasifica los diagnósticos por severidad.
3. Para cada error, explica **qué** pasa, **por qué** importa y **qué**
   cambiarías (sin ejecutarlo todavía).
4. Si hay solapes entre símbolos, propón `ejecutar_auto_layout` con
   `aplicar: false` para simular antes de modificar nada.
5. Cierra indicando si el plano está listo para `exportar_archivo`.
"""


PROMPTS: list[Prompt] = [
    Prompt(
        name="system_prompt",
        title="Prompt de sistema de qetgen",
        description="Contrato de trabajo para la IA que genera documentación "
                    "eléctrica con qetgen.",
        text=SYSTEM_PROMPT),
    Prompt(
        name="revisar_plano",
        title="Revisar un plano",
        description="Flujo de revisión estética y accionable de un plano.",
        text=REVISAR_PLANO_PROMPT),
]

PROMPTS_BY_NAME: dict[str, Prompt] = {prompt.name: prompt for prompt in PROMPTS}


def list_prompts() -> list[dict]:
    """Descripción de todos los prompts (formato MCP)."""
    return [prompt.as_dict() for prompt in PROMPTS]


def get_prompt(session: Session, name: str, arguments: dict | None = None) -> dict:
    """Devuelve un prompt con sus argumentos aplicados (formato MCP)."""
    prompt = PROMPTS_BY_NAME.get(name)
    if prompt is None:
        raise ToolError(
            f"Prompt desconocido: {name!r}. "
            f"Disponibles: {', '.join(sorted(PROMPTS_BY_NAME))}")
    values = arguments or {}
    text = prompt.text
    if values:
        # Los argumentos se inyectan como contexto al final del prompt.
        text += "\n\nContexto:\n" + json.dumps(values, ensure_ascii=False, indent=2)
    return {
        "description": prompt.description,
        "messages": [{
            "role": "user",
            "content": {"type": "text", "text": text},
        }],
    }


__all__ = ["PROMPTS", "PROMPTS_BY_NAME", "PROMPT_PROTOCOL_VERSION", "Prompt",
           "SYSTEM_PROMPT", "get_prompt", "list_prompts"]

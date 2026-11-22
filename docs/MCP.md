# MCP.md — qetgen como servidor MCP

`qetgen` se puede usar desde cualquier cliente que hable **Model Context
Protocol** (MCP) por `stdio`: el cliente pide herramientas, recursos y
prompts; `qetgen` responde con el motor real (catálogo de símbolos de
QElectroTech, motor de layout, validadores y exportadores).

---

## 1. Puesta en marcha

```bash
pip install -e .            # instala el paquete y el comando `qetgen`
pip install -e ".[mcp]"     # además, el SDK oficial de MCP (opcional)
qetgen doctor               # comprueba que todo está en su sitio
qetgen serve                # arranca el servidor por stdio
```

El servidor funciona **con o sin** el SDK oficial:

| Situación | Transporte | Notas |
|---|---|---|
| `pip install qetgen[mcp]` | **SDK oficial** (`mcp>=1.0`) | Tipos oficiales, gestión de capacidades. |
| `pip install qetgen` | **Fallback propio** | JSON-RPC 2.0 sobre JSON Lines. Sin dependencias extra. |

En ambos casos la interfaz MCP es **idéntica**: mismas herramientas, mismos
recursos, mismos prompts. Se puede forzar el fallback con `--fallback`.

> `qetgen serve` **no imprime nada por stdout**: ese canal es el del
> protocolo. Los mensajes de estado van a `stderr`.

---

## 2. Configurar el cliente

Copia [`mcp_config_example.json`](../mcp_config_example.json) al archivo de
configuración de tu cliente MCP (la ruta exacta depende del cliente) y
ajusta el comando.

### Con el script instalado (`pip install -e .`)

```json
{
  "mcpServers": {
    "qetgen": {
      "command": "qetgen",
      "args": ["serve"]
    }
  }
}
```

### Sin instalar (desde el repositorio)

```json
{
  "mcpServers": {
    "qetgen": {
      "command": "python",
      "args": ["-X", "utf8", "-m", "qetgen.cli", "serve"],
      "cwd": "C:/ruta/al/repositorio",
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### Con rutas explícitas de configuración y biblioteca

```json
{
  "mcpServers": {
    "qetgen": {
      "command": "python",
      "args": [
        "-X", "utf8", "-m", "qetgen.cli", "serve",
        "--config", "C:/ruta/al/repo/config/default.yaml",
        "--library", "C:/Program Files/QElectroTech/elements"
      ]
    }
  }
}
```

---

## 3. Herramientas

Las ocho herramientas son **atómicas**: una llamada = una acción completa, con
entrada tipada (Pydantic estricto) y salida estructurada.

| Herramienta | Qué hace | Entrada principal |
|---|---|---|
| `crear_diagrama` | Crea un proyecto (o carga uno desde un JSON). | `titulo`, `formato_hoja`, `archivo?` |
| `listar_simbolos` | Lista los símbolos **reales** de la biblioteca de QET con terminales y geometría. | `tipo?`, `incluir_geometria?` |
| `agregar_elemento` | Coloca un símbolo en un folio. | `id`, `tipo`, `x`, `y`, `etiqueta?`, `orientacion?`, `bloqueado?` |
| `conectar_elementos` | Conecta dos terminales de dos elementos. | `desde`, `hasta`, `terminal_desde?`, `terminal_hasta?` |
| `ejecutar_auto_layout` | Reorganiza en columnas lógicas, respeta `bloqueado` y calcula rutas. | `folio?`, `snap?`, `aplicar?` |
| `validar_estetica` | Audita solapes, textos desbordados, legibilidad y cableado. | — |
| `obtener_resumen_canvas` | Resume el estado del lienzo. | `folio?` |
| `exportar_archivo` | Guarda el `.qet` editable o el JSON canónico. | `ruta`, `formato?` |

### Ejemplo de sesión

```jsonc
// 1) crear el proyecto
{"method": "tools/call", "params": {"name": "crear_diagrama",
 "arguments": {"titulo": "CUADRO DE MANDO", "formato_hoja": "A3_17x8"}}}

// 2) colocar dos símbolos (el tipo sale del catálogo real)
{"method": "tools/call", "params": {"name": "agregar_elemento",
 "arguments": {"id": "Q1", "tipo": "circuit_breaker_2p", "x": 200, "y": 200}}}

// 3) conectar
{"method": "tools/call", "params": {"name": "conectar_elementos",
 "arguments": {"desde": "Q1", "hasta": "K1"}}}

// 4) auditar y exportar
{"method": "tools/call", "params": {"name": "validar_estetica", "arguments": {}}}
{"method": "tools/call", "params": {"name": "exportar_archivo",
 "arguments": {"ruta": "output/cuadro_mando.qet", "formato": "qet"}}}
```

---

## 4. Recursos

| URI | Contenido |
|---|---|
| `qetgen://catalogo` | Catálogo de símbolos: descripción, prefijos, terminales, caja reservada y caja de tinta. |
| `qetgen://config` | Configuración central vigente (hoja, rejilla, tipografía, cableado, estilos). |
| `qetgen://formatos-hoja` | Presets de folio con su tamaño y zona segura. |
| `qetgen://proyecto` | El proyecto en memoria, en JSON canónico. |

---

## 5. Prompts

| Prompt | Para qué sirve |
|---|---|
| `system_prompt` | El contrato de trabajo de la IA: no inventar ingeniería, respetar `bloqueado`, validar antes de exportar. |
| `revisar_plano` | Flujo de revisión de un plano: resumir → validar → clasificar → proponer correcciones. |

---

## 6. Reglas de uso (importantes)

1. **La ingeniería la decide el usuario.** El servidor representa; no decide
   valores técnicos ni añade componentes por su cuenta. Lo que no conste en
   la documentación se marca como «PENDIENTE DE VERIFICACIÓN».
2. **`bloqueado: true` es intocable.** El auto-layout no mueve esos
   elementos: es la decisión del ingeniero sobre la posición.
3. **Simula antes de aplicar.** `ejecutar_auto_layout` con `aplicar: false`
   devuelve el informe sin tocar el proyecto.
4. **El `.qet` es el entregable.** El SVG es previsualización; las rutas
   ortogonales son una ayuda de diseño (QElectroTech recalcula su propio
   trazado al abrir el archivo).

---

## 7. Diagnóstico

```bash
qetgen doctor                 # entorno: Python, dependencias, QET, catálogo
qetgen doctor --json          # lo mismo, en JSON
qetgen doctor mi_proyecto.json  # añade la auditoría del proyecto
```

Si `doctor` informa `mcp NO instalado`, el servidor sigue funcionando con el
fallback propio: es una advertencia, no un error.

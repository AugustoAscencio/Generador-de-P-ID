# Cómo contribuir a qetgen

> Gracias por el interés. Este proyecto se construye con una regla que no
> se negocia: **nada se inventa**. El formato `.qet` está documentado con
> evidencia real, y cualquier cambio que afecte al motor, al formato o a la
> ingeniería del caso FV 588 debe respetarlo.

---

## 1. Entorno de desarrollo

### Requisitos

| Herramienta | Versión | Nota |
|---|---|---|
| Python | ≥ 3.10 | Probado en 3.10 → 3.13 (CI) |
| QElectroTech | 0.100.0 | Necesario para el catálogo de símbolos reales |
| Git | cualquiera | |

### Preparación

```bash
git clone https://github.com/AugustoAscencio/Generador-de-P-ID.git
cd Generador-de-P-ID

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -e ".[dev]"       # motor + ruff + pytest
qetgen doctor                 # todo debe salir en verde
```

### Verificación rápida

```bash
python -m unittest discover -s tests      # 227 tests (sin pytest necesario)
ruff check src tests tools
```

> En Windows, la consola usa `cp1252`: usa `python -X utf8` y
> `$env:PYTHONIOENCODING="utf-8"` si ves errores de codificación.

---

## 2. Reglas del proyecto (no negociables)

1. **Basado en evidencia.** Está **prohibido** inventar etiquetas o atributos
   XML del formato `.qet`. Ante cualquier duda, analiza archivos reales:
   ```bash
   python tools/inspect_qet.py "C:\Program Files\QElectroTech\examples\photovoltaique.qet"
   python tools/deep_qet.py    "C:\Program Files\QElectroTech\examples\photovoltaique.qet"
   ```
   El formato está documentado en [`docs/QET_FORMAT_NOTES.md`](docs/QET_FORMAT_NOTES.md),
   con **CONFIRMADO** vs **INFERIDO**. Si añades algo nuevo, márcalo
   correctamente y añade la prueba que lo demuestra.
2. **La ingeniería no la decide la herramienta.** El generador **representa**;
   nunca sustituye a la ingeniería. Lo no confirmado se marca
   **«PENDIENTE DE VERIFICACIÓN»**.
3. **Símbolos reales de biblioteca.** Un símbolo nuevo entra en
   `resources/symbol_catalog.json` solo si su `.elmt` existe en la biblioteca
   instalada de QElectroTech, y su geometría (terminales, posiciones) se ha
   **leído**, no supuesto.
4. **Sin cambios silenciosos en el entregable.** Si un cambio altera el
   `.qet` generado, documéntalo en el CHANGELOG y explica qué proyectos
   anteriores se ven afectados.
5. **El núcleo no contiene XML.** `core/` no usa `ElementTree`: el exportador
   relee el `.elmt` para embeberlo.

---

## 3. Estructura y dirección de dependencias

```
core/   →  layout/  →  exporters/ , validation/
             ↑
        cli/ , mcp_server/
```

`core` no depende de nada. `layout` depende de `core`. `cli` y `mcp_server`
usan todo. Si un módulo de `core` necesita importar de `layout`, es una señal
de que la abstracción está mal puesta.

Detalle en [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## 4. Flujo de trabajo de una contribución

```bash
# 1) Rama con un nombre descriptivo
git checkout -b feature/motor-etiquetas

# 2) Trabaja con la suite en verde en todo momento
python -m unittest discover -s tests

# 3) Commits pequeños y explícitos
git add -A
git commit -m "feat(layout): coloca las etiquetas en la primera posición libre"

# 4) Publica y abre un Pull Request
git push -u origin feature/motor-etiquetas
```

### Qué debe traer un Pull Request

- [ ] La **suite completa** en verde (`python -m unittest discover -s tests`).
- [ ] `ruff check src tests tools` sin errores.
- [ ] **Tests nuevos** para el comportamiento que introduces.
- [ ] Documentación actualizada: `docs/`, `CHANGELOG.md` y, si cambia el uso,
      `README.md` y `SKILL.md`.
- [ ] Si afecta al `.qet` generado: comparación estructural con la versión
      anterior (normalizando los UUID de instancia).
- [ ] Sin cambios en `entregables/` salvo que la ingeniería haya cambiado de
      verdad.

---

## 5. Estilo de código

- **PEP 8**, con 100 caracteres por línea (`ruff` con `E, F, W, I, UP, B`).
- **Docstrings en español**, con una línea que explique *qué* y el *por qué*
  cuando no sea evidente.
- **Type hints** en las funciones públicas.
- Los modelos son **Pydantic v2 estrictos** (`extra="forbid"`,
  `validate_assignment=True`): no relajes esa regla para "que pase algo".
- Comentarios que explican **decisiones y evidencia**, no lo obvio.

---

## 6. Cómo se verifica un cambio en el motor

El caso FV 588 es el banco de pruebas real. Tras un cambio en `layout/`,
`validation/` o `exporters/`:

```bash
# 1) Regenera y audita
qetgen fv588
qetgen layout examples/proyecto_fv_588.json --auto-layout --check

# 2) Comprueba que el .qet no ha cambiado estructuralmente
#    (los UUID de instancia son aleatorios por diseño: se normalizan)
```

Cifras de referencia del estado actual (v1.0.1):

| Comprobación | Resultado esperado |
|---|---|
| Tests | **227 OK** |
| Auto-layout de los 111 símbolos | 0 sin colocar, **0 solapes entre símbolos** |
| Rutas del proyecto | **60/60** trazadas |
| Auditoría sobre las 18 hojas | 8 errores reales (texto desbordado), avisos de legibilidad |

> Los 8 errores de texto desbordado son **defectos reales del proyecto FV 588**,
> no del motor: el motor los detecta y los reporta. No los "arregles"
> silenciosamente en el validador.

---

## 7. Publicar una versión

El versionado es [SemVer](https://semver.org/lang/es/) y el historial sigue
[Keep a Changelog](https://keepachangelog.com/es/1.1.0/).

```bash
# 1) Actualiza la versión en los DOS sitios (deben coincidir)
#    src/qetgen/__init__.py  →  __version__ = "1.1.0"
#    pyproject.toml          →  version = "1.1.0"
#    (hay un test que verifica la sincronía de la configuración)

# 2) Promueve "[No publicado]" a "[1.1.0] - <fecha>" en CHANGELOG.md

# 3) Suite completa + lint
python -m unittest discover -s tests
ruff check src tests tools

# 4) Commit, etiqueta y publicación
git add -A
git commit -m "feat(v1.1.0): <resumen>"
git tag -a v1.1.0 -m "v1.1.0 - <resumen>"
git push origin main
git push origin v1.1.0
```

Después, crea la *release* en GitHub con las notas del CHANGELOG.

---

## 8. Áreas donde más ayuda hace falta

| Área | Qué falta |
|---|---|
| **Verificación visual** | QElectroTech no tiene modo headless: la revisión visual de los 18 planos la hace una persona. |
| **Exportación a PDF** | Hoy se exporta desde QET (función nativa); automatizarlo requiere una vía con licencia. |
| **Más símbolos** | El catálogo tiene 14; la biblioteca de QET tiene 8597. |
| **Métrica tipográfica** | Hoy es una estimación calibrada; medir con la fuente real daría colisiones exactas. |
| **Tests de un `.qet` guardado por el usuario** | El round-trip existe para el caso FV 588; falta generalizarlo. |

---

## 9. Código de conducta

Sé profesional, técnico y respetuoso. En las discusiones técnicas, **apóyate
en la evidencia**: un `.qet` real, una medición reproducible o un test que
falla valen más que una opinión. Respetamos el trabajo de los demás y el
del autor original del caso FV 588.

---

## 10. Contacto

- **Issues y PRs:** <https://github.com/AugustoAscencio/Generador-de-P-ID/issues>
- **Documentación técnica del caso FV 588:** [`docs/SPEC_INVENTARIO.md`](docs/SPEC_INVENTARIO.md)
- **Reglas para agentes de IA en este workspace:** [`AGENTS.md`](AGENTS.md)

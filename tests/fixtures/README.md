# Fixtures — biblioteca de símbolos de QElectroTech

## Qué hay aquí

`qet_elements/` contiene una **copia byte-exacta de los 14 archivos `.elmt`**
que usa `resources/symbol_catalog.json`, extraídos de la biblioteca instalada
de **QElectroTech 0.100.0**:

```
C:\Program Files\QElectroTech\elements\
```

Los 14 archivos suman **44 KB**.

## Por qué están versionados

Los tests del motor (colisiones, routing, auto-layout, auditoría, exportador,
servidor MCP) necesitan la **geometría real** de los símbolos: sin ella no
hay nada que verificar. Si los tests dependieran de que QElectroTech esté
instalado en la máquina, la suite solo podría correr en el equipo del autor y
el CI no probaría nada.

Con estos fixtures:

- la suite es **hermética** y corre igual en Linux, macOS y Windows;
- el CI verifica la geometría real, no una imitación;
- cualquiera puede reproducir los resultados sin instalar QElectroTech.

## Cómo se garantiza que no deriven

`tests/test_fixtures.py` comprueba dos cosas:

1. **Todo símbolo del catálogo tiene su fixture** (y ningún fixture sobra).
2. **Cada fixture es byte-idéntico** al `.elmt` de la biblioteca instalada,
   comparando su SHA-256 — *cuando QElectroTech está disponible*. Si no lo
   está, ese test se marca como omitido (skip) y el resto sigue corriendo.

Es decir: los fixtures son **la evidencia**, no una simplificación. Si
QElectroTech se actualiza, el test falla y avisa de que hay que refrescarlos.

## Cómo refrescarlos

```bash
python tools/sync_fixtures.py
```

Copia los `.elmt` actuales de la biblioteca instalada a
`tests/fixtures/qet_elements/`, conservando la estructura de carpetas
relativa, y verifica los SHA-256.

## Nota

Estos fixtures son material de **prueba**. La generación real de los planos
usa siempre la biblioteca instalada de QElectroTech
(`config/default.yaml` → `sources.library_path`), nunca los fixtures.

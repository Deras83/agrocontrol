# AgroControl

Sistema de gestión agrícola para la clase de **Paradigmas de la Programación**.
Maneja lotes, cultivos, insumos, maquinaria, aplicaciones y cosechas, con diagnóstico experto.

## Paradigmas

| Paradigma | Archivos | Concepto que demuestra |
|-----------|----------|------------------------|
| Estructurada | `main.py` | Menú de consola con secuencia, selección e iteración |
| POO | `models/` (12 clases) | Herencia (`Insumo` → `Fertilizante`, `Plaguicida`, `Semilla`), encapsulamiento con `@property` y composición (`Finca`) |
| Declarativa (SQL) | `database/` | Tablas con CHECK y llaves foráneas; consultas que dicen *qué* se quiere |
| Lógica (Prolog) | `rules/sistema_experto.pl`, `rules/prolog_bridge.py` | Hechos y reglas para siembra, riego y plagas; Python las consulta con `swipl` |
| Funcional | `services/analytics.py`, `services/report_generator.py` | Funciones puras, `compose`, `partial`, `filter`/`map`/`reduce` |

## Cómo ejecutar

- Menú: en la raíz, `python main.py`
- Pruebas: abrir el archivo en `tests/` y pulsar ▷ (la funcional está en `services/prueba_funcional.py`)
- Puente Prolog: ▷ sobre `rules/prolog_bridge.py` (requiere `swipl` en el PATH)
- API y frontend: aún en actualización

## Nota

Los datos agronómicos de Prolog (pH, humedad, síntomas, tratamientos) son de ejemplo y no están verificados.
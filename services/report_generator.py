"""Reporte general de la finca (paradigma funcional: funciones puras que devuelven texto)."""
from functools import partial

from services import analytics

LINEA = "=" * 50


def ultimos(items, n=5):
    """Los n elementos más recientes, del último al primero."""
    return list(reversed(items[-n:]))


def seccion(titulo, lineas, vacio="Sin registros."):
    return [f"\n[{titulo}]"] + (lineas or [f"  {vacio}"])


def linea_lote(finca, lote):
    c = finca.cultivo_de(lote)
    cultivo = f"{c.nombre} ({c.etapa_fenologica})" if c else "sin cultivo"
    return (f"  - {lote.nombre}: {lote.hectareas} ha | suelo {lote.tipo_suelo} | pH {lote.ph} | "
            f"humedad {lote.humedad_actual}% | {cultivo}")


def linea_diagnostico(d):
    return f"  - #{d.id} {d.fecha} | {d.lote.nombre} | {d.tipo} | {d.conclusion} | severidad {d.severidad}"


def linea_cosecha(c):
    return f"  - {c.fecha} | {c.lote.nombre} | {c.toneladas} t"


def linea_aplicacion(a):
    return f"  - {a.fecha} | {a.lote.nombre} | {a.insumo.nombre} | dosis {a.dosis}"


def linea_registro(r):
    return f"  - {r.fecha} | {r.lote.nombre} | {r.actividad} | {r.horas_trabajadas} h"


def seccion_resumen(finca):
    r = analytics.resumen_finca(finca, 1.0)
    criticos = ", ".join(r["lotes_criticos"]) or "ninguno"
    return seccion("RESUMEN", [
        f"  Lotes: {r['lotes']} | Área total: {r['area_total']} ha",
        f"  Lotes críticos: {criticos}",
        f"  Costo total de insumos: {r['costo_total']}",
        f"  Toneladas cosechadas: {r['toneladas_cosechadas']}",
    ])


def reporte_completo(finca):
    horas = sum(map(lambda r: r.horas_trabajadas, finca.registros))
    partes = (
        [LINEA, f"  REPORTE GENERAL - {finca.nombre.upper()}", LINEA],
        seccion_resumen(finca),
        seccion(f"LOTES ({len(finca.lotes)})", list(map(partial(linea_lote, finca), finca.lotes))),
        seccion(f"ÚLTIMOS DIAGNÓSTICOS (de {len(finca.diagnosticos)})",
                list(map(linea_diagnostico, ultimos(finca.diagnosticos)))),
        seccion(f"ÚLTIMAS COSECHAS (de {len(finca.cosechas)})",
                list(map(linea_cosecha, ultimos(finca.cosechas)))),
        seccion(f"ÚLTIMAS APLICACIONES (de {len(finca.aplicaciones)})",
                list(map(linea_aplicacion, ultimos(finca.aplicaciones)))),
        seccion(f"BITÁCORA ({horas} h en total)",
                list(map(linea_registro, ultimos(finca.registros)))),
        ["\n" + LINEA],
    )
    return "\n".join(l for parte in partes for l in parte)
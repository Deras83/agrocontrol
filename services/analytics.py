"""Funciones puras (Programación Funcional).

Reglas de este módulo:
- Ninguna función modifica sus argumentos (devuelven tuplas o diccionarios nuevos).
- Ninguna lee ni escribe archivos, base de datos o variables globales.
- Los mismos argumentos siempre dan el mismo resultado.
"""
from functools import partial, reduce


# ------------------------------------------------------------ herramientas
def compose(*funciones):
    """compose(f, g, h)(x) equivale a f(g(h(x)))."""
    return lambda x: reduce(lambda acumulado, f: f(acumulado), reversed(funciones), x)


def promedio(valores):
    valores = tuple(valores)
    return sum(valores) / len(valores) if valores else 0.0


def promedio_ponderado(pares):
    """pares = ((valor, peso), ...). Cada valor cuenta según su peso."""
    pares = tuple(pares)
    peso_total = reduce(lambda acumulado, par: acumulado + par[1], pares, 0)
    if not peso_total:
        return 0.0
    return reduce(lambda acumulado, par: acumulado + par[0] * par[1], pares, 0) / peso_total


# ------------------------------------------------------------------ lotes
def lotes_con_humedad_menor(umbral, lotes):
    """filter: lotes cuya humedad es menor al umbral."""
    return tuple(filter(lambda lote: lote.humedad_actual < umbral, lotes))


# partial fija el umbral en 30%: lotes_criticos(lotes) ya solo pide los lotes
lotes_criticos = partial(lotes_con_humedad_menor, 30)

# Composición: primero se filtran los críticos y luego se extrae el dato
nombres_lotes_criticos = compose(tuple, partial(map, lambda lote: lote.nombre), lotes_criticos)
humedad_promedio_criticos = compose(
    promedio, partial(map, lambda lote: lote.humedad_actual), lotes_criticos)


def area_total(lotes):
    """reduce: suma de hectáreas."""
    return reduce(lambda acumulado, lote: acumulado + lote.hectareas, lotes, 0.0)


# ---------------------------------------------------------------- cultivos
def lotes_con_cultivo(finca):
    """Pares (lote, cultivo) de los lotes que tienen algo sembrado."""
    pares = map(lambda lote: (lote, finca.cultivo_de(lote)), finca.lotes)
    return tuple(filter(lambda par: par[1] is not None, pares))


def cultivos_listos_para_cosecha(pares):
    """filter: pares (lote, cultivo) cuyo cultivo está en etapa de cosecha."""
    return tuple(filter(lambda par: par[1].listo_para_cosecha(), pares))


# ------------------------------------------------------------ rendimiento
def proyecciones_por_lote(lotes, factor):
    """map: cada lote -> (nombre, toneladas esperadas = hectáreas * factor)."""
    return tuple(map(lambda lote: (lote.nombre, round(lote.hectareas * factor, 2)), lotes))


def proyeccion_global(lotes, factor):
    """reduce sobre el resultado de map: suma de todas las proyecciones."""
    return round(reduce(lambda acumulado, par: acumulado + par[1],
                        proyecciones_por_lote(lotes, factor), 0.0), 2)


def toneladas_totales(cosechas):
    return reduce(lambda acumulado, cosecha: acumulado + cosecha.toneladas, cosechas, 0.0)


def rendimiento_ponderado(cosechas):
    """Rendimiento t/ha donde cada cosecha pesa según las hectáreas de su lote."""
    pares = map(lambda c: (c.rendimiento_por_ha(), c.lote.hectareas), cosechas)
    return round(promedio_ponderado(pares), 2)


def rendimiento_simple(cosechas):
    """Promedio sin ponderar, para comparar con el ponderado."""
    return round(promedio(map(lambda c: c.rendimiento_por_ha(), cosechas)), 2)


# ----------------------------------------------------------- aplicaciones
def aplicaciones_realizadas(aplicaciones):
    return tuple(filter(lambda aplicacion: aplicacion.aplicada, aplicaciones))


def aplicaciones_de_lote(lote, aplicaciones):
    return tuple(filter(lambda aplicacion: aplicacion.lote is lote, aplicaciones))


def costo_total(aplicaciones):
    """reduce: costo acumulado de las aplicaciones ya realizadas."""
    return reduce(lambda acumulado, aplicacion: acumulado + aplicacion.costo_total(),
                  aplicaciones_realizadas(aplicaciones), 0.0)


def consumo_por_insumo(aplicaciones):
    """reduce: {nombre del insumo: (cantidad total, unidad)}. En cada paso se crea
    un diccionario nuevo; el acumulado anterior no se modifica."""
    def acumular(acumulado, aplicacion):
        nombre = aplicacion.insumo.nombre
        unidad = aplicacion.insumo.unidad_medida
        total = acumulado.get(nombre, (0.0, unidad))[0] + aplicacion.dosis
        return {**acumulado, nombre: (total, unidad)}
    return reduce(acumular, aplicaciones_realizadas(aplicaciones), {})


def costo_por_hectarea_lote(lote, aplicaciones):
    return round(costo_total(aplicaciones_de_lote(lote, aplicaciones)) / lote.hectareas, 2)


def costo_por_hectarea_global(lotes, aplicaciones):
    area = area_total(lotes)
    return round(costo_total(aplicaciones) / area, 2) if area else 0.0


# ----------------------------------------------------------------- resumen
def resumen_finca(finca, factor_rendimiento):
    """Todos los indicadores en un diccionario nuevo; no toca la finca."""
    return {
        "lotes": len(finca.lotes),
        "area_total": round(area_total(finca.lotes), 3),
        "lotes_criticos": nombres_lotes_criticos(finca.lotes),
        "costo_total": round(costo_total(finca.aplicaciones), 2),
        "costo_por_hectarea": costo_por_hectarea_global(finca.lotes, finca.aplicaciones),
        "toneladas_cosechadas": round(toneladas_totales(finca.cosechas), 3),
        "rendimiento_ponderado": rendimiento_ponderado(finca.cosechas),
        "proyeccion_global": proyeccion_global(finca.lotes, factor_rendimiento),
    }
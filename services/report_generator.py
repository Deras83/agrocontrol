def reporte_completo(estado):
    """
    Genera un texto consolidado con el reporte general de los lotes y registros.
    """
    lineas = []
    lineas.append("========================================")
    lineas.append("       REPORTE GENERAL - AGROCONTROL    ")
    lineas.append("========================================")
    
    # 1. Reporte de Lotes
    lotes = getattr(estado, 'lotes', [])
    lineas.append(f"\n[LOTES REGISTRADOS: {len(lotes)}]")
    for lote in lotes:
        nombre = getattr(lote, 'nombre', getattr(lote, 'id', 'Desconocido'))
        lineas.append(f"  - Lote: {nombre}")

    # 2. Reporte de Diagnósticos
    diagnosticos = getattr(estado, 'diagnosticos', [])
    if diagnosticos:
        lineas.append(f"\n[DIAGNÓSTICOS HISTÓRICOS: {len(diagnosticos)}]")
        for d in diagnosticos:
            d_id = getattr(d, 'id', 'N/D')
            d_lote = getattr(d, 'lote_id', getattr(d, 'lote', 'N/D'))
            d_causa = getattr(d, 'causa', getattr(d, 'resultado', 'Registrado'))
            lineas.append(f"  - ID {d_id} | Lote ID: {d_lote} | Causa: {d_causa}")
    else:
        lineas.append("\n[DIAGNÓSTICOS: Sin registros recientes]")

    lineas.append("\n========================================")
    return "\n".join(lineas)
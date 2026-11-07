import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from services import analytics as an
from services import report_generator as rg
from models.finca import Finca
from models.lote import Lote
from models.cultivo import Cultivo
from models.fertilizante import Fertilizante
from models.plaguicida import Plaguicida
from models.aplicacion_campo import AplicacionCampo
from models.cosecha import Cosecha

# --- Una finca de ejemplo, armada en memoria ---
finca = Finca("La Esperanza", "Zona central")
norte = Lote(1, "Lote Norte", 2, "franco", 6.5, 25)
sur = Lote(2, "Lote Sur", 3, "arcilloso", 6.0, 60)
este = Lote(3, "Lote Este", 5, "franco", 6.2, 28)
for lote in (norte, sur, este):
    finca.agregar_lote(lote)

urea = Fertilizante("Urea", 300, 46, 0, 0, costo_unitario=0.8, dosis_por_ha=50)
cipermetrina = Plaguicida("Cipermetrina", 20, 7, costo_unitario=12, dosis_por_ha=0.5)
finca.agregar_insumo(urea)
finca.agregar_insumo(cipermetrina)

finca.sembrar(norte, Cultivo("Maíz", "criollo", "cosecha", 110))
finca.sembrar(sur, Cultivo("Frijol", "rojo", "vegetativa", 25))

app1 = AplicacionCampo(1, norte, urea, 100, date(2026, 10, 1))
app2 = AplicacionCampo(2, sur, cipermetrina, 1.5, date(2026, 10, 2))
app3 = AplicacionCampo(3, norte, urea, 50, date(2026, 10, 5))
app4 = AplicacionCampo(4, este, urea, 200, date(2026, 10, 6))      # queda pendiente
for aplicacion in (app1, app2, app3):
    aplicacion.aplicar()
for aplicacion in (app1, app2, app3, app4):
    finca.agregar_aplicacion(aplicacion)

finca.agregar_cosecha(Cosecha(1, sur, 6, date(2026, 10, 10)))
finca.agregar_cosecha(Cosecha(2, este, 14, date(2026, 10, 12)))

# --- filter ---
print("--- filter ---")
print("Lotes críticos:", an.nombres_lotes_criticos(finca.lotes))
print("Lotes con humedad menor a 50:", tuple(l.nombre for l in an.lotes_con_humedad_menor(50, finca.lotes)))
listos = an.cultivos_listos_para_cosecha(an.lotes_con_cultivo(finca))
print("Cultivos listos para cosecha:", tuple(lote.nombre for lote, _ in listos))

# --- map ---
print("--- map ---")
print("Proyección por lote (3.5 t/ha):", an.proyecciones_por_lote(finca.lotes, 3.5))

# --- reduce ---
print("--- reduce ---")
print("Área total:", an.area_total(finca.lotes))
print("Proyección global:", an.proyeccion_global(finca.lotes, 3.5))
print("Costo total de aplicaciones realizadas:", an.costo_total(finca.aplicaciones))
print("Consumo por insumo:", an.consumo_por_insumo(finca.aplicaciones))
print("Costo por hectárea (global):", an.costo_por_hectarea_global(finca.lotes, finca.aplicaciones))
print("Rendimiento ponderado:", an.rendimiento_ponderado(finca.cosechas),
      "| simple:", an.rendimiento_simple(finca.cosechas))

# --- composición y partial ---
print("--- composición ---")
print("compose(str, len)('abc'):", repr(an.compose(str, len)("abc")))
print("Humedad promedio de los críticos:", an.humedad_promedio_criticos(finca.lotes))

# --- reporte completo ---
print()
print(rg.reporte_completo(finca))

# --- pureza: mismos datos de entrada, mismos resultados, nada modificado ---
print()
print("--- pureza ---")
estado = lambda: (tuple(map(str, finca.lotes)), tuple(map(str, finca.insumos)),
                  tuple(map(str, finca.aplicaciones)), tuple(map(str, finca.cosechas)))
antes = estado()
resultado_1 = (an.resumen_finca(finca, 3.5), rg.reporte_completo(finca))
resultado_2 = (an.resumen_finca(finca, 3.5), rg.reporte_completo(finca))
print("Mismo resultado al repetir:", resultado_1 == resultado_2)
print("Datos originales sin cambios:", antes == estado())
print("Resumen:", an.resumen_finca(finca, 3.5))

# --- bordes: finca vacía ---
vacia = Finca("Vacía")
print("--- finca vacía ---")
print(an.resumen_finca(vacia, 3.5))
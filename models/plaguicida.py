"""Clase Plaguicida: hereda de Insumo."""
from models.insumo import Insumo


class Plaguicida(Insumo):
    def __init__(self, nombre, cantidad_disponible, periodo_carencia_dias,
                 unidad_medida="l", costo_unitario=0.0, dosis_por_ha=0.0):
        super().__init__(nombre, "plaguicida", cantidad_disponible,
                         unidad_medida, costo_unitario, dosis_por_ha)
        if periodo_carencia_dias < 0:
            raise ValueError("El periodo de carencia no puede ser negativo.")
        self._periodo_carencia_dias = periodo_carencia_dias

    @property
    def periodo_carencia_dias(self):
        return self._periodo_carencia_dias

    def descripcion(self):
        return (f"{self.nombre} (plaguicida, carencia "
                f"{self.periodo_carencia_dias} días antes de cosechar)")
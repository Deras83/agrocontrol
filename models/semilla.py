"""Clase Semilla: hereda de Insumo."""
from models.insumo import Insumo


class Semilla(Insumo):
    def __init__(self, nombre, cantidad_disponible, tasa_germinacion,
                 unidad_medida="kg", costo_unitario=0.0, dosis_por_ha=0.0):
        super().__init__(nombre, "semilla", cantidad_disponible,
                         unidad_medida, costo_unitario, dosis_por_ha)
        if not 0 < tasa_germinacion <= 100:
            raise ValueError("La tasa de germinación debe estar entre 1 y 100.")
        self._tasa_germinacion = tasa_germinacion

    @property
    def tasa_germinacion(self):
        return self._tasa_germinacion

    def dosis_recomendada(self, hectareas):
        """Sobrescribe el método base: compensa las semillas que no germinan."""
        return super().dosis_recomendada(hectareas) / (self.tasa_germinacion / 100)

    def descripcion(self):
        return f"{self.nombre} (semilla, germinación {self.tasa_germinacion}%)"
    
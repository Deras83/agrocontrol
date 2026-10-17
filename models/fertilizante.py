"""Clase Fertilizante: hereda de Insumo."""
from models.insumo import Insumo


class Fertilizante(Insumo):
    def __init__(self, nombre, cantidad_disponible, n, p, k,
                 unidad_medida="kg", costo_unitario=0.0, dosis_por_ha=0.0):
        super().__init__(nombre, "fertilizante", cantidad_disponible,
                         unidad_medida, costo_unitario, dosis_por_ha)
        for porcentaje in (n, p, k):
            if not 0 <= porcentaje <= 100:
                raise ValueError("N, P y K deben estar entre 0 y 100.")
        if n + p + k > 100:
            raise ValueError("La suma de N, P y K no puede superar 100%.")
        self._n, self._p, self._k = n, p, k

    @property
    def formula(self):
        return f"{self._n}-{self._p}-{self._k}"

    def descripcion(self):
        return f"{self.nombre} (fertilizante NPK {self.formula})"
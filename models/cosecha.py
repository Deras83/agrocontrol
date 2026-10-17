"""Clase Cosecha: asocia un Lote con lo recolectado (POO)."""
from datetime import date

from models.lote import Lote
from models.cultivo import Cultivo


class Cosecha:
    def __init__(self, id, lote, toneladas, fecha=None, cultivo=None):
        if not isinstance(lote, Lote):
            raise TypeError("lote debe ser un objeto Lote.")
        if cultivo is not None and not isinstance(cultivo, Cultivo):
            raise TypeError("cultivo debe ser un objeto Cultivo.")
        self._id = id
        self._lote = lote
        self._cultivo = cultivo
        self.toneladas = toneladas
        self.fecha = fecha or date.today()

    # --- Getters y setters con validación ---
    @property
    def id(self):
        return self._id

    @property
    def lote(self):
        return self._lote

    @property
    def cultivo(self):
        return self._cultivo

    @property
    def toneladas(self):
        return self._toneladas

    @toneladas.setter
    def toneladas(self, valor):
        if valor <= 0:
            raise ValueError("Las toneladas recolectadas deben ser mayores a 0.")
        self._toneladas = valor

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, valor):
        if not isinstance(valor, date):
            raise ValueError("La fecha debe ser un objeto date.")
        self._fecha = valor

    # --- Comportamiento ---
    def rendimiento_por_ha(self):
        """Toneladas recolectadas por hectárea del lote."""
        return round(self._toneladas / self._lote.hectareas, 2)

    def cumple_carencia(self, aplicaciones):
        """True si ninguna aplicación hecha en este lote tiene una fecha segura
        de cosecha posterior a la fecha de esta cosecha."""
        for aplicacion in aplicaciones:
            if (aplicacion.lote is self._lote and aplicacion.aplicada
                    and aplicacion.fecha_segura_cosecha() > self._fecha):
                return False
        return True

    def __str__(self):
        cultivo = f" de {self._cultivo.nombre}" if self._cultivo else ""
        return (f"Cosecha {self.id}{cultivo} en {self._lote.nombre} | "
                f"{self._toneladas} t | {self._fecha} | "
                f"{self.rendimiento_por_ha()} t/ha")
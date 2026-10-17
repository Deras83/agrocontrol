"""Clase AplicacionCampo: asocia un Lote con un Insumo (POO)."""
from datetime import date, timedelta

from models.lote import Lote
from models.insumo import Insumo
from models.plaguicida import Plaguicida


class AplicacionCampo:
    def __init__(self, id, lote, insumo, dosis, fecha=None, aplicada=False):
        if not isinstance(lote, Lote):
            raise TypeError("lote debe ser un objeto Lote.")
        if not isinstance(insumo, Insumo):
            raise TypeError("insumo debe ser un objeto Insumo.")
        self._id = id
        self._lote = lote
        self._insumo = insumo
        self.dosis = dosis
        self.fecha = fecha or date.today()
        self._aplicada = aplicada

    # --- Getters y setters con validación ---
    @property
    def id(self):
        return self._id

    @property
    def lote(self):
        return self._lote

    @property
    def insumo(self):
        return self._insumo

    @property
    def aplicada(self):
        return self._aplicada

    @property
    def dosis(self):
        return self._dosis

    @dosis.setter
    def dosis(self, valor):
        if valor <= 0:
            raise ValueError("La dosis debe ser mayor a 0.")
        self._dosis = valor

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, valor):
        if not isinstance(valor, date):
            raise ValueError("La fecha debe ser un objeto date.")
        self._fecha = valor

    # --- Comportamiento ---
    def aplicar(self):
        """Descuenta la dosis del inventario. Solo se puede aplicar una vez."""
        if self._aplicada:
            raise ValueError("Esta aplicación ya fue realizada.")
        self._insumo.usar(self._dosis)
        self._aplicada = True

    def costo_total(self):
        return self._dosis * self._insumo.costo_unitario

    def dosis_por_hectarea(self):
        return round(self._dosis / self._lote.hectareas, 2)

    def fecha_segura_cosecha(self):
        """Los plaguicidas obligan a esperar su periodo de carencia."""
        if isinstance(self._insumo, Plaguicida):
            return self._fecha + timedelta(days=self._insumo.periodo_carencia_dias)
        return self._fecha

    def __str__(self):
        estado = "aplicada" if self._aplicada else "pendiente"
        return (f"Aplicación {self.id}: {self._insumo.nombre} en {self._lote.nombre} | "
                f"{self._dosis} {self._insumo.unidad_medida} | {self._fecha} | "
                f"costo {self.costo_total()} | {estado}")
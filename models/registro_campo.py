"""Clase RegistroCampo: bitácora de actividades (POO)."""
from datetime import date

from models.lote import Lote
from models.maquinaria import Maquinaria


class RegistroCampo:
    ACTIVIDADES = ("preparacion_suelo", "siembra", "riego", "fertilizacion",
                   "fumigacion", "mantenimiento", "cosecha", "otro")

    def __init__(self, id, lote, actividad, descripcion="", fecha=None,
                 horas_trabajadas=0.0, maquinaria=None):
        if not isinstance(lote, Lote):
            raise TypeError("lote debe ser un objeto Lote.")
        if maquinaria is not None and not isinstance(maquinaria, Maquinaria):
            raise TypeError("maquinaria debe ser un objeto Maquinaria.")
        self._id = id
        self._lote = lote
        self._maquinaria = maquinaria
        self.actividad = actividad
        self.descripcion = descripcion
        self.fecha = fecha or date.today()
        self.horas_trabajadas = horas_trabajadas
        if maquinaria is not None and horas_trabajadas <= 0:
            raise ValueError("Si usas maquinaria, las horas trabajadas deben ser mayores a 0.")
        self._completado = False

    # --- Getters y setters con validación ---
    @property
    def id(self):
        return self._id

    @property
    def lote(self):
        return self._lote

    @property
    def maquinaria(self):
        return self._maquinaria

    @property
    def completado(self):
        return self._completado

    @property
    def actividad(self):
        return self._actividad

    @actividad.setter
    def actividad(self, valor):
        valor = valor.lower().strip()
        if valor not in self.ACTIVIDADES:
            raise ValueError(f"Actividad inválida. Opciones: {self.ACTIVIDADES}")
        self._actividad = valor

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor):
        self._descripcion = (valor or "").strip()

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, valor):
        if not isinstance(valor, date):
            raise ValueError("La fecha debe ser un objeto date.")
        self._fecha = valor

    @property
    def horas_trabajadas(self):
        return self._horas_trabajadas

    @horas_trabajadas.setter
    def horas_trabajadas(self, valor):
        if valor < 0:
            raise ValueError("Las horas trabajadas no pueden ser negativas.")
        self._horas_trabajadas = valor

    # --- Comportamiento ---
    def usa_maquinaria(self):
        return self._maquinaria is not None

    def completar(self):
        """Marca la actividad como hecha y suma las horas a la maquinaria."""
        if self._completado:
            raise ValueError("Este registro ya fue completado.")
        if self.usa_maquinaria():
            self._maquinaria.registrar_uso(self._horas_trabajadas)
        self._completado = True

    def __str__(self):
        maquina = f" con {self._maquinaria.nombre}" if self.usa_maquinaria() else ""
        estado = "completado" if self._completado else "pendiente"
        detalle = f" - {self._descripcion}" if self._descripcion else ""
        return (f"Registro {self.id}: {self._actividad}{detalle} en {self._lote.nombre}"
                f"{maquina} | {self._horas_trabajadas} h | {self._fecha} | {estado}")
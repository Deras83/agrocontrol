"""Clase Diagnostico: resultado del sistema experto (POO)."""
from datetime import date

from models.lote import Lote


class Diagnostico:
    TIPOS = ("riego", "plaga_deficiencia", "siembra")
    SEVERIDADES = ("baja", "media", "alta")

    def __init__(self, id, lote, tipo, conclusion, recomendacion="",
                 severidad="baja", fecha=None):
        if not isinstance(lote, Lote):
            raise TypeError("lote debe ser un objeto Lote.")
        self._id = id
        self._lote = lote
        self.tipo = tipo
        self.conclusion = conclusion
        self.recomendacion = recomendacion
        self.severidad = severidad
        self.fecha = fecha or date.today()

    # --- Getters y setters con validación ---
    @property
    def id(self):
        return self._id

    @property
    def lote(self):
        return self._lote

    @property
    def tipo(self):
        return self._tipo

    @tipo.setter
    def tipo(self, valor):
        valor = valor.lower().strip()
        if valor not in self.TIPOS:
            raise ValueError(f"Tipo inválido. Opciones: {self.TIPOS}")
        self._tipo = valor

    @property
    def conclusion(self):
        return self._conclusion

    @conclusion.setter
    def conclusion(self, valor):
        if not valor or not valor.strip():
            raise ValueError("La conclusión no puede estar vacía.")
        self._conclusion = valor.strip()

    @property
    def recomendacion(self):
        return self._recomendacion

    @recomendacion.setter
    def recomendacion(self, valor):
        self._recomendacion = (valor or "").strip()

    @property
    def severidad(self):
        return self._severidad

    @severidad.setter
    def severidad(self, valor):
        valor = valor.lower().strip()
        if valor not in self.SEVERIDADES:
            raise ValueError(f"Severidad inválida. Opciones: {self.SEVERIDADES}")
        self._severidad = valor

    @property
    def fecha(self):
        return self._fecha

    @fecha.setter
    def fecha(self, valor):
        if not isinstance(valor, date):
            raise ValueError("La fecha debe ser un objeto date.")
        self._fecha = valor

    # --- Comportamiento ---
    def es_urgente(self):
        return self._severidad == "alta"

    def tiene_recomendacion(self):
        return bool(self._recomendacion)

    @classmethod
    def desde_respuesta(cls, id, lote, tipo, respuesta):
        """Construye un Diagnostico a partir de un diccionario con las claves
        'conclusion', 'recomendacion' y 'severidad' (las dos últimas opcionales)."""
        return cls(id, lote, tipo,
                   respuesta.get("conclusion", ""),
                   respuesta.get("recomendacion", ""),
                   respuesta.get("severidad", "baja"))

    def __str__(self):
        urgente = " [URGENTE]" if self.es_urgente() else ""
        texto = (f"Diagnóstico {self.id} ({self._tipo}) en {self._lote.nombre}{urgente}: "
                 f"{self._conclusion}")
        if self.tiene_recomendacion():
            texto += f" -> {self._recomendacion}"
        return texto
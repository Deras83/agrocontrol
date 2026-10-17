"""Clase Lote (Programación Orientada a Objetos)."""


class Lote:
    TIPOS_SUELO = ("arcilloso", "franco", "arenoso", "limoso")

    def __init__(self, id, nombre, hectareas, tipo_suelo, ph, humedad_actual=0.0):
        self._id = id
        # Se usan los setters para que la validación corra desde el inicio
        self.nombre = nombre
        self.hectareas = hectareas
        self.tipo_suelo = tipo_suelo
        self.ph = ph
        self.humedad_actual = humedad_actual

    # --- Getters y setters con validación ---
    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def hectareas(self):
        return self._hectareas

    @hectareas.setter
    def hectareas(self, valor):
        if valor <= 0:
            raise ValueError("Las hectáreas deben ser mayores a 0.")
        self._hectareas = valor

    @property
    def tipo_suelo(self):
        return self._tipo_suelo

    @tipo_suelo.setter
    def tipo_suelo(self, valor):
        valor = valor.lower().strip()
        if valor not in self.TIPOS_SUELO:
            raise ValueError(f"Tipo de suelo inválido. Opciones: {self.TIPOS_SUELO}")
        self._tipo_suelo = valor

    @property
    def ph(self):
        return self._ph

    @ph.setter
    def ph(self, valor):
        if not 0 <= valor <= 14:
            raise ValueError("El pH debe estar entre 0 y 14.")
        self._ph = valor

    @property
    def humedad_actual(self):
        return self._humedad_actual

    @humedad_actual.setter
    def humedad_actual(self, valor):
        if not 0 <= valor <= 100:
            raise ValueError("La humedad debe estar entre 0 y 100.")
        self._humedad_actual = valor

    # --- Comportamiento ---
    def actualizar_sensor(self, humedad):
        """Simula la lectura de un sensor de humedad."""
        self.humedad_actual = humedad

    def obtener_estado(self):
        if self.humedad_actual < 30:
            return "crítico"
        if self.humedad_actual < 50:
            return "atención"
        return "óptimo"

    def __str__(self):
        return (f"Lote {self.id}: {self.nombre} | {self.hectareas} ha | "
                f"suelo {self.tipo_suelo} | pH {self.ph} | "
                f"humedad {self.humedad_actual}% ({self.obtener_estado()})")
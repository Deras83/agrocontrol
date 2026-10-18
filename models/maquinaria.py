"""Clase Maquinaria (Programación Orientada a Objetos)."""


class Maquinaria:
    def __init__(self, id, nombre, vida_util_horas=5000, intervalo_mantenimiento=250,
                 horas_uso=0.0, horas_ultimo_mantenimiento=0.0):
        self._id = id
        self.nombre = nombre
        self.vida_util_horas = vida_util_horas
        self.intervalo_mantenimiento = intervalo_mantenimiento
        self.horas_uso = horas_uso
        self._horas_ultimo_mantenimiento = horas_ultimo_mantenimiento

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
            raise ValueError("El nombre de la maquinaria no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def vida_util_horas(self):
        return self._vida_util_horas

    @vida_util_horas.setter
    def vida_util_horas(self, valor):
        if valor <= 0:
            raise ValueError("La vida útil debe ser mayor a 0.")
        self._vida_util_horas = valor

    @property
    def intervalo_mantenimiento(self):
        return self._intervalo_mantenimiento

    @intervalo_mantenimiento.setter
    def intervalo_mantenimiento(self, valor):
        if valor <= 0:
            raise ValueError("El intervalo de mantenimiento debe ser mayor a 0.")
        self._intervalo_mantenimiento = valor

    @property
    def horas_uso(self):
        return self._horas_uso

    @horas_uso.setter
    def horas_uso(self, valor):
        if valor < 0:
            raise ValueError("Las horas de uso no pueden ser negativas.")
        self._horas_uso = valor

    @property
    def horas_ultimo_mantenimiento(self):
        return self._horas_ultimo_mantenimiento

    # --- Comportamiento ---
    @property
    def estado_mantenimiento(self):
        """Se calcula a partir de las horas desde el último mantenimiento."""
        horas_desde = self.horas_uso - self._horas_ultimo_mantenimiento
        if horas_desde >= self.intervalo_mantenimiento:
            return "vencido"
        if horas_desde >= 0.8 * self.intervalo_mantenimiento:
            return "próximo"
        return "al día"

    def registrar_uso(self, horas):
        if horas <= 0:
            raise ValueError("Las horas de uso deben ser mayores a 0.")
        self.horas_uso += horas

    def registrar_mantenimiento(self):
        """Reinicia el conteo para el siguiente mantenimiento."""
        self._horas_ultimo_mantenimiento = self.horas_uso

    def calcular_desgaste(self):
        """Porcentaje de vida útil consumida (máximo 100)."""
        return min(100.0, round(self.horas_uso / self.vida_util_horas * 100, 1))

    def __str__(self):
        return (f"Maquinaria {self.id}: {self.nombre} | {self.horas_uso} h | "
                f"desgaste {self.calcular_desgaste()}% | "
                f"mantenimiento {self.estado_mantenimiento}")
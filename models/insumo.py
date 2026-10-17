"""Clase base Insumo (Programación Orientada a Objetos)."""


class Insumo:
    def __init__(self, nombre, tipo, cantidad_disponible, unidad_medida,
                 costo_unitario=0.0, dosis_por_ha=0.0):
        self._tipo = tipo
        self.nombre = nombre
        self.cantidad_disponible = cantidad_disponible
        self.unidad_medida = unidad_medida
        self.costo_unitario = costo_unitario
        self.dosis_por_ha = dosis_por_ha

    # --- Getters y setters con validación ---
    @property
    def tipo(self):
        return self._tipo

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre del insumo no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def cantidad_disponible(self):
        return self._cantidad_disponible

    @cantidad_disponible.setter
    def cantidad_disponible(self, valor):
        if valor < 0:
            raise ValueError("La cantidad disponible no puede ser negativa.")
        self._cantidad_disponible = valor

    @property
    def unidad_medida(self):
        return self._unidad_medida

    @unidad_medida.setter
    def unidad_medida(self, valor):
        if not valor or not valor.strip():
            raise ValueError("La unidad de medida no puede estar vacía.")
        self._unidad_medida = valor.strip()

    @property
    def costo_unitario(self):
        return self._costo_unitario

    @costo_unitario.setter
    def costo_unitario(self, valor):
        if valor < 0:
            raise ValueError("El costo unitario no puede ser negativo.")
        self._costo_unitario = valor

    @property
    def dosis_por_ha(self):
        return self._dosis_por_ha

    @dosis_por_ha.setter
    def dosis_por_ha(self, valor):
        if valor < 0:
            raise ValueError("La dosis por hectárea no puede ser negativa.")
        self._dosis_por_ha = valor

    # --- Comportamiento ---
    def usar(self, cantidad):
        """Descuenta cantidad del inventario."""
        if cantidad <= 0:
            raise ValueError("La cantidad a usar debe ser mayor a 0.")
        if cantidad > self.cantidad_disponible:
            raise ValueError("No hay suficiente inventario.")
        self.cantidad_disponible -= cantidad

    def reabastecer(self, cantidad):
        """Suma cantidad al inventario."""
        if cantidad <= 0:
            raise ValueError("La cantidad a reabastecer debe ser mayor a 0.")
        self.cantidad_disponible += cantidad

    def dosis_recomendada(self, hectareas):
        """Cantidad total necesaria para un área. Las subclases pueden cambiarla."""
        return self.dosis_por_ha * hectareas

    def descripcion(self):
        return f"{self.nombre} ({self.tipo})"

    def __str__(self):
        return (f"{self.descripcion()} | {self.cantidad_disponible} {self.unidad_medida} | "
                f"costo {self.costo_unitario}/{self.unidad_medida}")
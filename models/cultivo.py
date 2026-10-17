"""Clase Cultivo (Programación Orientada a Objetos)."""


class Cultivo:
    ETAPAS = ("germinacion", "vegetativa", "floracion", "fructificacion", "cosecha")

    def __init__(self, nombre, variedad, etapa_fenologica="germinacion", dias_desde_siembra=0):
        self.nombre = nombre
        self.variedad = variedad
        self.etapa_fenologica = etapa_fenologica
        self.dias_desde_siembra = dias_desde_siembra

    # --- Getters y setters con validación ---
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre del cultivo no puede estar vacío.")
        self._nombre = valor.strip().lower()

    @property
    def variedad(self):
        return self._variedad

    @variedad.setter
    def variedad(self, valor):
        self._variedad = (valor or "").strip()

    @property
    def etapa_fenologica(self):
        return self._etapa_fenologica

    @etapa_fenologica.setter
    def etapa_fenologica(self, valor):
        valor = valor.lower().strip()
        if valor not in self.ETAPAS:
            raise ValueError(f"Etapa inválida. Opciones: {self.ETAPAS}")
        self._etapa_fenologica = valor

    @property
    def dias_desde_siembra(self):
        return self._dias_desde_siembra

    @dias_desde_siembra.setter
    def dias_desde_siembra(self, valor):
        if valor < 0:
            raise ValueError("Los días desde la siembra no pueden ser negativos.")
        self._dias_desde_siembra = valor

    # --- Comportamiento ---
    def avanzar_dias(self, dias):
        """Suma días desde la siembra."""
        self.dias_desde_siembra += dias

    def avanzar_etapa(self):
        """Pasa a la siguiente etapa fenológica, si existe."""
        i = self.ETAPAS.index(self.etapa_fenologica)
        if i == len(self.ETAPAS) - 1:
            raise ValueError("El cultivo ya está en la última etapa.")
        self.etapa_fenologica = self.ETAPAS[i + 1]

    def listo_para_cosecha(self):
        return self.etapa_fenologica == "cosecha"

    def __str__(self):
        return (f"{self.nombre.capitalize()} ({self.variedad or 'sin variedad'}) | "
                f"etapa {self.etapa_fenologica} | {self.dias_desde_siembra} días")
"""Clase Finca: contenedor que administra los demás objetos (POO, composición)."""
from models.lote import Lote
from models.cultivo import Cultivo
from models.insumo import Insumo
from models.maquinaria import Maquinaria
from models.aplicacion_campo import AplicacionCampo
from models.cosecha import Cosecha
from models.registro_campo import RegistroCampo
from models.diagnostico import Diagnostico


class Finca:
    def __init__(self, nombre, ubicacion=""):
        self.nombre = nombre
        self.ubicacion = ubicacion
        self._lotes = []
        self._insumos = []
        self._maquinarias = []
        self._cultivos = {}          # id del lote -> Cultivo
        self._aplicaciones = []
        self._cosechas = []
        self._registros = []
        self._diagnosticos = []

    # --- Getters y setters con validación ---
    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre de la finca no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def ubicacion(self):
        return self._ubicacion

    @ubicacion.setter
    def ubicacion(self, valor):
        self._ubicacion = (valor or "").strip()

    # Las colecciones se devuelven como tuplas: quien las consulta no puede
    # modificar la lista interna (útil después para el módulo funcional).
    @property
    def lotes(self):
        return tuple(self._lotes)

    @property
    def insumos(self):
        return tuple(self._insumos)

    @property
    def maquinarias(self):
        return tuple(self._maquinarias)

    @property
    def aplicaciones(self):
        return tuple(self._aplicaciones)

    @property
    def cosechas(self):
        return tuple(self._cosechas)

    @property
    def registros(self):
        return tuple(self._registros)

    @property
    def diagnosticos(self):
        return tuple(self._diagnosticos)

    # --- Agregar objetos (con validación de tipo y duplicados) ---
    def _agregar(self, coleccion, objeto, clase, clave):
        if not isinstance(objeto, clase):
            raise TypeError(f"Se esperaba un objeto {clase.__name__}.")
        if any(clave(existente) == clave(objeto) for existente in coleccion):
            raise ValueError(f"Ya existe un {clase.__name__} con ese identificador.")
        coleccion.append(objeto)

    def _agregar_de_lote(self, coleccion, objeto, clase):
        """Para objetos que dependen de un lote: el lote debe ser de esta finca."""
        if isinstance(objeto, clase) and objeto.lote not in self._lotes:
            raise ValueError("El lote no pertenece a esta finca.")
        self._agregar(coleccion, objeto, clase, lambda x: x.id)

    def agregar_lote(self, lote):
        self._agregar(self._lotes, lote, Lote, lambda x: x.id)

    def agregar_insumo(self, insumo):
        self._agregar(self._insumos, insumo, Insumo, lambda x: x.nombre.lower())

    def agregar_maquinaria(self, maquinaria):
        self._agregar(self._maquinarias, maquinaria, Maquinaria, lambda x: x.id)

    def agregar_aplicacion(self, aplicacion):
        self._agregar_de_lote(self._aplicaciones, aplicacion, AplicacionCampo)

    def agregar_cosecha(self, cosecha):
        self._agregar_de_lote(self._cosechas, cosecha, Cosecha)

    def agregar_registro(self, registro):
        self._agregar_de_lote(self._registros, registro, RegistroCampo)

    def agregar_diagnostico(self, diagnostico):
        self._agregar_de_lote(self._diagnosticos, diagnostico, Diagnostico)

    # --- Cultivos por lote ---
    def sembrar(self, lote, cultivo):
        if lote not in self._lotes:
            raise ValueError("El lote no pertenece a esta finca.")
        if not isinstance(cultivo, Cultivo):
            raise TypeError("Se esperaba un objeto Cultivo.")
        if lote.id in self._cultivos:
            raise ValueError("El lote ya tiene un cultivo.")
        self._cultivos[lote.id] = cultivo

    def cultivo_de(self, lote):
        return self._cultivos.get(lote.id)

    # --- Búsquedas ---
    def buscar_lote(self, id):
        return next((lote for lote in self._lotes if lote.id == id), None)

    def buscar_insumo(self, nombre):
        return next((i for i in self._insumos
                     if i.nombre.lower() == nombre.strip().lower()), None)

    # --- Consultas ---
    def area_total(self):
        return sum(lote.hectareas for lote in self._lotes)

    def lotes_criticos(self):
        return tuple(l for l in self._lotes if l.obtener_estado() == "crítico")

    def insumos_bajos(self, minimo):
        return tuple(i for i in self._insumos if i.cantidad_disponible < minimo)

    def maquinaria_con_mantenimiento_pendiente(self):
        return tuple(m for m in self._maquinarias
                     if m.estado_mantenimiento in ("próximo", "vencido"))

    def costo_aplicaciones(self):
        return sum(a.costo_total() for a in self._aplicaciones if a.aplicada)

    def toneladas_cosechadas(self):
        return sum(c.toneladas for c in self._cosechas)

    def resumen(self):
        criticos = ", ".join(l.nombre for l in self.lotes_criticos()) or "ninguno"
        lugar = f" ({self._ubicacion})" if self._ubicacion else ""
        return "\n".join([
            f"Finca {self._nombre}{lugar}",
            f"Lotes: {len(self._lotes)} | Área total: {self.area_total()} ha",
            f"Lotes críticos: {criticos}",
            f"Insumos: {len(self._insumos)} | Maquinaria: {len(self._maquinarias)}",
            f"Aplicaciones realizadas: {sum(1 for a in self._aplicaciones if a.aplicada)}",
            f"Toneladas cosechadas: {self.toneladas_cosechadas()}",
        ])

    def __str__(self):
        return self.resumen()
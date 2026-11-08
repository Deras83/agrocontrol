<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Estado del diálogo (modal)
const dialogVisible = ref(false)

// Formulario reactivo adaptado a las columnas de tu tabla "lotes"
const form = ref({
  nombre: '',
  area_ha: 0,
  tipo_suelo: '',
  ph: 7.0
})

// Lista reactiva de lotes
const lotesList = ref([])

// Función para obtener los lotes desde Flask
const cargarLotes = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/lotes')
    if (!response.ok) throw new Error('Error al conectar con el servidor')
    const data = await response.json()
    lotesList.value = data
  } catch (error) {
    console.error(error)
    ElMessage.error('No se pudo cargar la lista de lotes desde el backend.')
  }
}

// Cargar los datos automáticamente al abrir la vista
onMounted(() => {
  cargarLotes()
})

// Función para guardar un nuevo lote enviándolo a Python
const guardarLote = async () => {
  if (!form.value.nombre || !form.value.tipo_suelo) {
    ElMessage.error('Por favor completa los campos obligatorios.')
    return
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/api/lotes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(form.value)
    })

    const data = await response.json()
    if (!response.ok) throw new Error(data.error || 'Error al guardar en la base de datos')

    ElMessage.success('¡Lote registrado con éxito en SQLite!')
    dialogVisible.value = false
    
    // Limpiar formulario y recargar la tabla
    form.value = { nombre: '', area_ha: 0, tipo_suelo: '', ph: 7.0 }
    cargarLotes()
  } catch (error) {
    console.error(error)
    ElMessage.error(error instanceof Error ? error.message : 'Error al registrar el lote.')
  }
}

// Función para eliminar un lote (pide confirmación y muestra el motivo si no se puede)
const eliminarLote = async (lote: any) => {
  try {
    await ElMessageBox.confirm(
      `¿Eliminar "${lote.nombre}"? También se borra su cultivo.`,
      'Confirmar eliminación',
      { confirmButtonText: 'Eliminar', cancelButtonText: 'Cancelar', type: 'warning' }
    )
  } catch {
    return // el usuario canceló
  }
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/lotes/${lote.id}`, { method: 'DELETE' })
    const data = await response.json()
    if (!response.ok) {
      throw new Error(
        String(data.error).includes('FOREIGN KEY')
          ? 'No se puede eliminar: el lote tiene aplicaciones, bitácora, cosechas o diagnósticos registrados.'
          : data.error || 'Error al eliminar el lote'
      )
    }
    ElMessage.success('Lote eliminado correctamente')
    cargarLotes()
  } catch (error) {
    console.error(error)
    ElMessage.error(error instanceof Error ? error.message : 'No se pudo eliminar el lote.')
  }
}

// Función para actualizar la humedad del suelo de un lote
const cambiarHumedad = async (lote: any) => {
  let valor = 0
  try {
    const { value } = await ElMessageBox.prompt(
      `Humedad actual de "${lote.nombre}" (0 a 100 %)`,
      'Actualizar humedad',
      {
        inputValue: String(lote.humedad_actual),
        inputPattern: /^(100(\.0+)?|\d{1,2}(\.\d+)?)$/,
        inputErrorMessage: 'Escribe un número entre 0 y 100'
      }
    )
    valor = Number(value)
  } catch {
    return // el usuario canceló
  }
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/lotes/${lote.id}/humedad`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ humedad: valor })
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.error || 'Error al actualizar la humedad')
    ElMessage.success('Humedad actualizada')
    cargarLotes()
  } catch (error) {
    console.error(error)
    ElMessage.error(error instanceof Error ? error.message : 'No se pudo actualizar la humedad.')
  }
}

// --- Detalle de un lote: ficha, cultivo e historial (usa los endpoints existentes) ---
const detalleVisible = ref(false)
const detalle = ref<any>(null)

const pedir = async (ruta: string) => {
  const response = await fetch(`http://127.0.0.1:5000/api/${ruta}`)
  const data = await response.json()
  if (!response.ok) throw new Error(data.error || 'Error del servidor')
  return data
}

const verDetalle = async (lote: any) => {
  try {
    const [cultivos, diagnosticos, aplicaciones, bitacora, cosechas] = await Promise.all(
      ['cultivos', 'diagnosticos', 'aplicaciones', 'bitacora', 'cosechas'].map((ruta) => pedir(ruta))
    )
    const delLote = (lista: any[]) => lista.filter((x) => x.lote === lote.nombre)
    detalle.value = {
      lote,
      cultivo: cultivos.find((c: any) => c.lote_id === lote.id),
      diagnosticos: delLote(diagnosticos),
      aplicaciones: delLote(aplicaciones),
      bitacora: delLote(bitacora),
      cosechas: delLote(cosechas)
    }
    detalleVisible.value = true
  } catch (error) {
    console.error(error)
    ElMessage.error(error instanceof Error ? error.message : 'No se pudo cargar el detalle.')
  }
}

const estadoHumedad = (h: number) => (h < 30 ? ['danger', 'Crítica'] : h < 50 ? ['warning', 'Atención'] : ['success', 'Óptima'])
const colorSeveridad: Record<string, string> = { baja: 'success', media: 'warning', alta: 'danger' }
const pestanas = [
  { clave: 'diagnosticos', titulo: 'Diagnósticos', sev: true, cols: [['fecha', 'Fecha'], ['tipo', 'Tipo'], ['conclusion', 'Conclusión']] },
  { clave: 'aplicaciones', titulo: 'Aplicaciones', cols: [['fecha', 'Fecha'], ['insumo', 'Insumo'], ['dosis', 'Dosis']] },
  { clave: 'bitacora', titulo: 'Bitácora', cols: [['fecha', 'Fecha'], ['actividad', 'Actividad'], ['horas_trabajadas', 'Horas']] },
  { clave: 'cosechas', titulo: 'Cosechas', cols: [['fecha', 'Fecha'], ['toneladas', 'Toneladas']] }
]
</script>

<template>
  <div class="fincas-container">
    <div class="header-section">
      <div>
        <h2> Gestión de Lotes y Terrenos</h2>
        <p>Administra las parcelas sincronizadas con tu base de datos SQLite.</p>
      </div>
      <el-button type="primary" @click="dialogVisible = true">
        + Registrar Nuevo Lote
      </el-button>
    </div>

    <!-- Tabla conectada a los campos reales de SQLite -->
    <el-card shadow="never" style="margin-top: 20px;">
      <el-table :data="lotesList" style="width: 100%" stripe empty-text="No hay lotes registrados todavía. ¡Agrega uno!">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="nombre" label="Nombre del Lote" width="200" />
        <el-table-column prop="area_ha" label="Área (Hectáreas)" width="150" />
        <el-table-column prop="tipo_suelo" label="Tipo de Suelo" width="180" />
        <el-table-column prop="ph" label="pH del Suelo" width="120" />
        <el-table-column label="Humedad" width="140">
          <template #default="{ row }">
            <el-tag :type="estadoHumedad(row.humedad_actual)[0]">{{ row.humedad_actual }}%</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Acciones" align="right">
          <template #default="{ row }">
            <el-button size="small" type="success" plain @click="cambiarHumedad(row)">Humedad</el-button>
            <el-button size="small" type="primary" plain @click="verDetalle(row)">Ver Detalles</el-button>
            <el-button size="small" type="danger" plain @click="eliminarLote(row)">Eliminar</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- Ventana Modal (Dialog) para registrar un nuevo lote -->
    <el-dialog v-model="dialogVisible" title="Registrar Nuevo Lote" width="500px">
      <el-form :model="form" label-width="130px">
        <el-form-item label="Nombre Lote">
          <el-input v-model="form.nombre" placeholder="Ej. Lote Norte" />
        </el-form-item>
        <el-form-item label="Área (Hectáreas)">
          <el-input-number v-model="form.area_ha" :min="0.1" :precision="2" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="Tipo de Suelo">
          <el-select v-model="form.tipo_suelo" placeholder="Selecciona el tipo de suelo" style="width: 100%;">
            <el-option v-for="s in ['arcilloso', 'franco', 'arenoso', 'limoso']" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item label="Nivel de pH">
          <el-input-number v-model="form.ph" :min="0" :max="14" :precision="1" :step="0.1" style="width: 100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancelar</el-button>
          <el-button type="primary" @click="guardarLote">Guardar en SQLite</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Detalle del lote -->
    <el-dialog v-model="detalleVisible" :title="`Detalle: ${detalle?.lote.nombre}`" width="800px">
      <template v-if="detalle">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="Área">{{ detalle.lote.area_ha }} ha</el-descriptions-item>
          <el-descriptions-item label="Suelo">{{ detalle.lote.tipo_suelo }}</el-descriptions-item>
          <el-descriptions-item label="pH">{{ detalle.lote.ph }}</el-descriptions-item>
          <el-descriptions-item label="Humedad">
            <el-tag :type="estadoHumedad(detalle.lote.humedad_actual)[0]">
              {{ detalle.lote.humedad_actual }}% · {{ estadoHumedad(detalle.lote.humedad_actual)[1] }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Cultivo" :span="2">
            <template v-if="detalle.cultivo">
              {{ detalle.cultivo.tipo_cultivo }} {{ detalle.cultivo.variedad }} · etapa {{ detalle.cultivo.etapa }}
              · sembrado {{ detalle.cultivo.fecha_siembra || 'sin fecha' }}
            </template>
            <template v-else>Sin cultivo</template>
          </el-descriptions-item>
        </el-descriptions>

        <el-tabs style="margin-top: 16px">
          <el-tab-pane v-for="p in pestanas" :key="p.clave" :label="`${p.titulo} (${detalle[p.clave].length})`">
            <el-table :data="detalle[p.clave].slice(0, 5)" empty-text="Sin registros">
              <el-table-column v-for="[prop, label] in p.cols" :key="prop" :prop="prop" :label="label" />
              <el-table-column v-if="p.sev" label="Severidad" width="110">
                <template #default="{ row }">
                  <el-tag :type="colorSeveridad[row.severidad] || 'info'">{{ row.severidad }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
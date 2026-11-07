<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

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

    if (!response.ok) throw new Error('Error al guardar en la base de datos')

    ElMessage.success('¡Lote registrado con éxito en SQLite!')
    dialogVisible.value = false
    
    // Limpiar formulario y recargar la tabla
    form.value = { nombre: '', area_ha: 0, tipo_suelo: '', ph: 7.0 }
    cargarLotes()
  } catch (error) {
    console.error(error)
    ElMessage.error('Error al registrar el lote.')
  }
}

// Función para eliminar un lote por ID
const eliminarLote = async (id: number) => {
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/lotes/${id}`, {
      method: 'DELETE'
    })

    if (!response.ok) throw new Error('Error al eliminar el lote')

    ElMessage.success('Lote eliminado correctamente')
    cargarLotes()
  } catch (error) {
    console.error(error)
    ElMessage.error('No se pudo eliminar el lote.')
  }
}
</script>

<template>
  <div class="fincas-container">
    <div class="header-section">
      <div>
        <h2>🏡 Gestión de Lotes y Terrenos</h2>
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
        <el-table-column label="Acciones" align="right">
          <template #default>
            <el-button size="small" type="primary" plain>Ver Detalles</el-button>
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
          <el-input v-model="form.tipo_suelo" placeholder="Ej. Franco-arcilloso" />
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
  </div>
</template>

<style scoped>
.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
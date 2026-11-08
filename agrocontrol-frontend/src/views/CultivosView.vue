<template>
  <div style="padding: 20px;">
    <h2>Gestión de Cultivos</h2>
    
    <!-- Botón para abrir el modal de registro -->
    <el-button type="primary" @click="dialogVisible = true" style="margin-bottom: 20px;">
      Registrar Nuevo Cultivo
    </el-button>

    <!-- Tabla de Cultivos -->
    <el-table :data="cultivosList" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="nombre_lote" label="Lote Asignado" />
      <el-table-column prop="tipo_cultivo" label="Tipo de Cultivo" />
      <el-table-column prop="variedad" label="Variedad" />
      <el-table-column prop="fecha_siembra" label="Fecha de Siembra" />
      <el-table-column prop="etapa" label="Etapa" />
      <el-table-column label="Acciones" width="150">
        <template #default="{ row }">
          <el-button size="small" type="success" plain @click="abrirEtapa(row)">Cambiar etapa</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Modal de Registro -->
    <el-dialog v-model="dialogVisible" title="Registrar Cultivo" width="500px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="Lote">
          <el-select v-model="form.lote_id" placeholder="Selecciona un lote" style="width: 100%">
            <el-option
              v-for="lote in lotesList"
              :key="lote.id"
              :label="lote.nombre"
              :value="lote.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="Tipo de Cultivo">
          <el-input v-model="form.tipo_cultivo" placeholder="Ej. Maíz, Frijol..." />
        </el-form-item>

        <el-form-item label="Variedad">
          <el-input v-model="form.variedad" placeholder="Ej. H-93, Criollo..." />
        </el-form-item>

        <el-form-item label="Fecha Siembra">
          <el-date-picker
            v-model="form.fecha_siembra"
            type="date"
            placeholder="Selecciona fecha"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="Etapa">
          <el-select v-model="form.etapa" placeholder="Selecciona etapa" style="width: 100%">
            <el-option label="Germinación" value="germinacion" />
            <el-option label="Vegetativa" value="vegetativa" />
            <el-option label="Floración" value="floracion" />
            <el-option label="Fructificación" value="fructificacion" />
            <el-option label="Cosecha" value="cosecha" />
          </el-select>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">Cancelar</el-button>
          <el-button type="primary" @click="guardarCultivo">Guardar</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Modal para cambiar la etapa de un cultivo -->
    <el-dialog v-model="etapaVisible" :title="`Etapa: ${cultivoSel?.tipo_cultivo} (${cultivoSel?.nombre_lote})`" width="420px">
      <el-select v-model="etapaNueva" style="width: 100%">
        <el-option v-for="[valor, texto] in etapas" :key="valor" :label="texto" :value="valor" />
      </el-select>
      <template #footer>
        <el-button @click="etapaVisible = false">Cancelar</el-button>
        <el-button type="primary" @click="guardarEtapa">Guardar</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// Interfaces para tipado estricto con TypeScript
interface Lote {
  id: number
  nombre: string
}

interface Cultivo {
  id?: number
  nombre_lote?: string
  lote_id: number | ''
  tipo_cultivo: string
  variedad: string
  fecha_siembra: string
  etapa: string
}

const dialogVisible = ref(false)
const cultivosList = ref<Cultivo[]>([])
const lotesList = ref<Lote[]>([]) // Soluciona el error de tipo 'never'

const formVacio = (): Cultivo => ({
  lote_id: '',
  tipo_cultivo: '',
  variedad: '',
  fecha_siembra: '',
  etapa: 'germinacion'
})
const form = ref<Cultivo>(formVacio())

// Cargar lotes para el selector
const cargarLotes = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/lotes')
    if (response.ok) {
      lotesList.value = await response.json()
    }
  } catch (error) {
    console.error('Error al cargar lotes:', error)
  }
}

// Cargar cultivos desde el backend
const cargarCultivos = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/cultivos')
    if (response.ok) {
      cultivosList.value = await response.json()
    }
  } catch (error) {
    console.error('Error al cargar cultivos:', error)
  }
}

// Guardar nuevo cultivo
const guardarCultivo = async () => {
  if (!form.value.lote_id || !form.value.tipo_cultivo || !form.value.fecha_siembra) {
    ElMessage.error('Por favor completa los campos obligatorios.')
    return
  }

  try {
    const response = await fetch('http://127.0.0.1:5000/api/cultivos', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value)
    })

    const data = await response.json()
    if (!response.ok) throw new Error(data.error || 'Error al registrar')

    ElMessage.success('¡Cultivo registrado con éxito!')
    dialogVisible.value = false
    form.value = formVacio()
    cargarCultivos()
  } catch (error) {
    console.error(error)
    ElMessage.error(error instanceof Error ? error.message : 'No se pudo registrar el cultivo.')
  }
}

// Cambiar la etapa de un cultivo ya registrado
const etapas = [['germinacion', 'Germinación'], ['vegetativa', 'Vegetativa'], ['floracion', 'Floración'],
  ['fructificacion', 'Fructificación'], ['cosecha', 'Cosecha']]
const etapaVisible = ref(false)
const cultivoSel = ref<Cultivo | null>(null)
const etapaNueva = ref('germinacion')

const abrirEtapa = (cultivo: Cultivo) => {
  cultivoSel.value = cultivo
  etapaNueva.value = cultivo.etapa
  etapaVisible.value = true
}

const guardarEtapa = async () => {
  if (!cultivoSel.value) return
  try {
    const response = await fetch(`http://127.0.0.1:5000/api/cultivos/${cultivoSel.value.id}/etapa`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ etapa: etapaNueva.value })
    })
    const data = await response.json()
    if (!response.ok) throw new Error(data.error || 'Error al cambiar la etapa')
    ElMessage.success('Etapa actualizada')
    etapaVisible.value = false
    cargarCultivos()
  } catch (error) {
    console.error(error)
    ElMessage.error(error instanceof Error ? error.message : 'No se pudo cambiar la etapa.')
  }
}

onMounted(() => {
  cargarLotes()
  cargarCultivos()
})
</script>
<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const API = 'http://127.0.0.1:5000/api'
const lista = ref([])
const lotes = ref([])
const dialogo = ref(false)
const vacio = () => ({ lote_id: '', toneladas: 1, fecha: '' })
const form = ref(vacio())

const pedir = async (ruta, opciones = {}) => {
  const r = await fetch(`${API}/${ruta}`, opciones)
  const data = await r.json()
  if (!r.ok) throw new Error(data.error || 'Error del servidor')
  return data
}

const cargar = async () => {
  try {
    lista.value = await pedir('cosechas')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const abrir = async () => {
  try {
    lotes.value = await pedir('lotes')
    dialogo.value = true
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const guardar = async () => {
  try {
    await pedir('cosechas', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    ElMessage.success('Cosecha registrada')
    dialogo.value = false
    form.value = vacio()
    cargar()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

onMounted(cargar)
</script>

<template>
  <div>
    <h2> Cosechas</h2>
    <el-button type="primary" style="margin-bottom: 20px" @click="abrir">Registrar cosecha</el-button>
    <el-table :data="lista" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="lote" label="Lote" />
      <el-table-column prop="toneladas" label="Toneladas" />
      <el-table-column prop="fecha" label="Fecha" />
    </el-table>

    <el-dialog v-model="dialogo" title="Registrar cosecha" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="Lote">
          <el-select v-model="form.lote_id" placeholder="Selecciona un lote" style="width: 100%">
            <el-option v-for="l in lotes" :key="l.id" :label="l.nombre" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Toneladas">
          <el-input-number v-model="form.toneladas" :min="0.01" :step="0.5" />
        </el-form-item>
        <el-form-item label="Fecha">
          <el-date-picker v-model="form.fecha" type="date" value-format="YYYY-MM-DD"
                          placeholder="Hoy por defecto" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogo = false">Cancelar</el-button>
        <el-button type="primary" @click="guardar">Guardar</el-button>
      </template>
    </el-dialog>
  </div>
</template>
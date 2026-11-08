<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const API = 'http://127.0.0.1:5000/api'
const lista = ref([])
const lotes = ref([])
const insumos = ref([])
const dialogo = ref(false)
const form = ref({ lote_id: '', insumo_id: '', dosis: 1 })

const pedir = async (ruta, opciones = {}) => {
  const r = await fetch(`${API}/${ruta}`, opciones)
  const data = await r.json()
  if (!r.ok) throw new Error(data.error || 'Error del servidor')
  return data
}

const cargar = async () => {
  try {
    lista.value = await pedir('aplicaciones')
    insumos.value = await pedir('insumos')
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
    await pedir('aplicaciones', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form.value),
    })
    ElMessage.success('Aplicación registrada')
    dialogo.value = false
    form.value = { lote_id: '', insumo_id: '', dosis: 1 }
    cargar()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

onMounted(cargar)
</script>

<template>
  <div>
    <h2> Aplicaciones de Insumos</h2>
    <el-button type="primary" style="margin-bottom: 20px" @click="abrir">Registrar aplicación</el-button>
    <el-table :data="lista" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="lote" label="Lote" />
      <el-table-column prop="insumo" label="Insumo" />
      <el-table-column prop="dosis" label="Dosis" />
      <el-table-column prop="fecha" label="Fecha" />
      <el-table-column label="Aplicada">
        <template #default="{ row }">{{ row.aplicada ? 'Sí' : 'No' }}</template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogo" title="Registrar aplicación" width="500px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="Lote">
          <el-select v-model="form.lote_id" placeholder="Selecciona un lote" style="width: 100%">
            <el-option v-for="l in lotes" :key="l.id" :label="l.nombre" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="Insumo">
          <el-select v-model="form.insumo_id" placeholder="Selecciona un insumo" style="width: 100%">
            <el-option v-for="i in insumos" :key="i.id" :value="i.id"
                       :label="`${i.nombre} (stock: ${i.stock} ${i.unidad})`" />
          </el-select>
        </el-form-item>
        <el-form-item label="Dosis">
          <el-input-number v-model="form.dosis" :min="0.01" :step="0.5" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogo = false">Cancelar</el-button>
        <el-button type="primary" @click="guardar">Guardar</el-button>
      </template>
    </el-dialog>
  </div>
</template>
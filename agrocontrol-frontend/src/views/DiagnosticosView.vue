<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const lista = ref([])
const colores = { baja: 'success', media: 'warning', alta: 'danger' }

onMounted(async () => {
  try {
    const r = await fetch('http://127.0.0.1:5000/api/diagnosticos')
    const data = await r.json()
    if (!r.ok) throw new Error(data.error || 'Error del servidor')
    lista.value = data
  } catch (e) {
    ElMessage.error(e.message)
  }
})
</script>

<template>
  <div>
    <h2> Historial de Diagnósticos</h2>
    <el-table :data="lista" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="lote" label="Lote" />
      <el-table-column prop="tipo" label="Tipo" />
      <el-table-column prop="conclusion" label="Conclusión" min-width="200" />
      <el-table-column prop="recomendacion" label="Recomendación" min-width="200" />
      <el-table-column label="Severidad">
        <template #default="{ row }">
          <el-tag :type="colores[row.severidad] || 'info'">{{ row.severidad }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="fecha" label="Fecha" />
    </el-table>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const API = 'http://127.0.0.1:5000/api'
const resumen = ref({ lotes_criticos: [] })
const lotes = ref([])
const cultivos = ref([])
const datos = ref({ diagnosticos: [], cosechas: [], aplicaciones: [], bitacora: [] })
const texto = ref('')
const verTexto = ref(false)

const pedir = async (ruta) => {
  const r = await fetch(`${API}/${ruta}`)
  const data = await r.json()
  if (!r.ok) throw new Error(data.error || 'Error del servidor')
  return data
}

onMounted(async () => {
  try {
    resumen.value = await pedir('resumen')
    lotes.value = await pedir('lotes')
    cultivos.value = await pedir('cultivos')
    for (const k of Object.keys(datos.value)) datos.value[k] = (await pedir(k)).slice(0, 5)
    texto.value = (await pedir('reporte-general')).reporte
  } catch (e) {
    ElMessage.error(e.message)
  }
})

const tarjetas = computed(() => [
  { t: 'Lotes', v: resumen.value.lotes },
  { t: 'Área total (ha)', v: resumen.value.area_total },
  { t: 'Costo de insumos', v: resumen.value.costo_total },
  { t: 'Toneladas cosechadas', v: resumen.value.toneladas_cosechadas },
])

const cultivoDe = (id) => {
  const c = cultivos.value.find((x) => x.lote_id === id)
  return c ? `${c.tipo_cultivo} (${c.etapa})` : 'Sin cultivo'
}
const estadoHumedad = (h) => (h < 30 ? ['danger', 'Crítica'] : h < 50 ? ['warning', 'Atención'] : ['success', 'Óptima'])
const colorSeveridad = { baja: 'success', media: 'warning', alta: 'danger' }

const bloques = [
  { clave: 'diagnosticos', titulo: 'Últimos diagnósticos', cols: [['fecha', 'Fecha'], ['lote', 'Lote'], ['tipo', 'Tipo'], ['conclusion', 'Conclusión']], sev: true },
  { clave: 'cosechas', titulo: 'Últimas cosechas', cols: [['fecha', 'Fecha'], ['lote', 'Lote'], ['toneladas', 'Toneladas']] },
  { clave: 'aplicaciones', titulo: 'Últimas aplicaciones', cols: [['fecha', 'Fecha'], ['lote', 'Lote'], ['insumo', 'Insumo'], ['dosis', 'Dosis']] },
  { clave: 'bitacora', titulo: 'Última actividad de campo', cols: [['fecha', 'Fecha'], ['lote', 'Lote'], ['actividad', 'Actividad'], ['horas_trabajadas', 'Horas']] },
]
</script>

<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center">
      <h2> Reporte General</h2>
      <el-button @click="verTexto = true">Ver texto</el-button>
    </div>

    <el-row :gutter="16" style="margin-bottom: 16px">
      <el-col v-for="c in tarjetas" :key="c.t" :span="6">
        <el-card shadow="hover"><el-statistic :title="c.t" :value="c.v ?? 0" /></el-card>
      </el-col>
    </el-row>

    <el-alert v-if="resumen.lotes_criticos.length" type="error" show-icon :closable="false"
              title="Lotes críticos" :description="resumen.lotes_criticos.join(', ')"
              style="margin-bottom: 16px" />

    <el-card style="margin-bottom: 16px">
      <template #header>Lotes</template>
      <el-table :data="lotes">
        <el-table-column prop="nombre" label="Lote" />
        <el-table-column prop="area_ha" label="Área (ha)" />
        <el-table-column prop="tipo_suelo" label="Suelo" />
        <el-table-column prop="ph" label="pH" />
        <el-table-column label="Humedad">
          <template #default="{ row }">
            <el-tag :type="estadoHumedad(row.humedad_actual)[0]">
              {{ row.humedad_actual }}% · {{ estadoHumedad(row.humedad_actual)[1] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Cultivo">
          <template #default="{ row }">{{ cultivoDe(row.id) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card v-for="b in bloques" :key="b.clave" style="margin-bottom: 16px">
      <template #header>{{ b.titulo }}</template>
      <el-table :data="datos[b.clave]" empty-text="Sin registros">
        <el-table-column v-for="[prop, label] in b.cols" :key="prop" :prop="prop" :label="label" />
        <el-table-column v-if="b.sev" label="Severidad" width="110">
          <template #default="{ row }">
            <el-tag :type="colorSeveridad[row.severidad] || 'info'">{{ row.severidad }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="verTexto" title="Reporte en texto" width="800px">
      <pre style="white-space: pre-wrap; margin: 0">{{ texto }}</pre>
    </el-dialog>
  </div>
</template>
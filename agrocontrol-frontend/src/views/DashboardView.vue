<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GaugeChart, BarChart, PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, GaugeChart, BarChart, PieChart, TooltipComponent, LegendComponent, GridComponent])

const API = 'http://127.0.0.1:5000/api'
const resumen = ref({ lotes_criticos: [] })
const lotes = ref([])
const diagnosticos = ref([])
const cosechas = ref([])

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
    diagnosticos.value = (await pedir('diagnosticos')).slice(0, 4)
    cosechas.value = await pedir('cosechas')
  } catch (e) {
    ElMessage.error(e.message)
  }
})

const VERDE = '#22c55e', AMARILLO = '#facc15', NARANJA = '#f97316'
const BLANCO = { color: '#e5e7eb' }
const sevColor = { baja: VERDE, media: AMARILLO, alta: NARANJA }

const tarjetas = computed(() => [
  { t: 'Lotes', v: resumen.value.lotes ?? 0, c: VERDE },
  { t: 'Área total (ha)', v: resumen.value.area_total ?? 0, c: VERDE },
  { t: 'Costo de insumos', v: resumen.value.costo_total ?? 0, c: AMARILLO },
  { t: 'Toneladas cosechadas', v: resumen.value.toneladas_cosechadas ?? 0, c: NARANJA },
])

const humedadPromedio = computed(() => {
  const h = lotes.value.map((l) => l.humedad_actual)
  return h.length ? Math.round(h.reduce((a, b) => a + b, 0) / h.length) : 0
})

const medidor = computed(() => ({
  series: [{
    type: 'gauge', min: 0, max: 100, startAngle: 200, endAngle: -20,
    axisLine: { lineStyle: { width: 14, color: [[0.3, NARANJA], [0.5, AMARILLO], [1, VERDE]] } },
    pointer: { width: 5 }, axisTick: { show: false }, splitLine: { show: false },
    axisLabel: { ...BLANCO, distance: 20 },
    detail: { formatter: '{value}%', color: '#fff', fontSize: 28, offsetCenter: [0, '60%'] },
    data: [{ value: humedadPromedio.value }],
  }],
}))

const tonPorLote = computed(() => {
  const acc = {}
  cosechas.value.forEach((c) => { acc[c.lote] = (acc[c.lote] || 0) + c.toneladas })
  return acc
})

const barras = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: 40, right: 16, top: 20, bottom: 30 },
  xAxis: { type: 'category', data: Object.keys(tonPorLote.value), axisLabel: BLANCO },
  yAxis: { type: 'value', axisLabel: BLANCO, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } } },
  series: [{ type: 'bar', data: Object.values(tonPorLote.value), itemStyle: { color: VERDE, borderRadius: [8, 8, 0, 0] } }],
}))

const pastel = computed(() => {
  const n = { Crítica: 0, Atención: 0, Óptima: 0 }
  lotes.value.forEach((l) => { n[l.humedad_actual < 30 ? 'Crítica' : l.humedad_actual < 50 ? 'Atención' : 'Óptima']++ })
  const col = { Crítica: NARANJA, Atención: AMARILLO, Óptima: VERDE }
  return {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, textStyle: BLANCO },
    series: [{
      type: 'pie', radius: '65%', center: ['50%', '45%'], label: { color: '#fff' },
      data: Object.entries(n).filter(([, v]) => v > 0).map(([name, value]) => ({ name, value, itemStyle: { color: col[name] } })),
    }],
  }
})
</script>

<template>
  <div>
    <h2> Dashboard</h2>

    <el-row :gutter="16" class="fila">
      <el-col v-for="t in tarjetas" :key="t.t" :span="6">
        <el-card shadow="never">
          <div class="titulo">{{ t.t }}</div>
          <div class="valor" :style="{ color: t.c }">{{ t.v }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="fila">
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>Humedad promedio de los lotes</template>
          <v-chart :option="medidor" autoresize style="height: 260px" />
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card shadow="never" style="height: 100%">
          <template #header>Alertas recientes</template>
          <el-empty v-if="!diagnosticos.length" description="Sin diagnósticos" />
          <div v-for="d in diagnosticos" :key="d.id" class="alerta">
            <span class="punto" :style="{ background: sevColor[d.severidad] || '#9ca3af' }" />
            <div>
              <div>{{ d.conclusion }}</div>
              <small>{{ d.lote }} · {{ d.tipo }} · {{ d.fecha }}</small>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="fila">
      <el-col :span="14">
        <el-card shadow="never">
          <template #header>Toneladas cosechadas por lote</template>
          <el-empty v-if="!cosechas.length" description="Sin cosechas registradas" :image-size="80" />
          <v-chart v-else :option="barras" autoresize style="height: 260px" />
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never">
          <template #header>Lotes por estado de humedad</template>
          <v-chart :option="pastel" autoresize style="height: 260px" />
        </el-card>
      </el-col>
    </el-row>

    <el-alert v-if="resumen.lotes_criticos.length" type="error" show-icon :closable="false"
              title="Lotes críticos (humedad baja)" :description="resumen.lotes_criticos.join(', ')" />
  </div>
</template>

<style scoped>
.fila { margin-bottom: 16px; }
.titulo { font-size: 0.9rem; color: #e5e7eb; }
.valor { font-size: 2rem; font-weight: 700; margin-top: 6px; }
.alerta {
  display: flex; gap: 12px; align-items: center; padding: 10px 12px; margin-bottom: 8px;
  border-radius: 12px; background: rgba(255, 255, 255, 0.1);
}
.alerta small { color: #cbd5d0; }
.punto { width: 12px; height: 12px; border-radius: 50%; flex: none; }
</style>
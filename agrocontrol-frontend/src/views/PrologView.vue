<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const API = 'http://127.0.0.1:5000/api'
const tipo = ref('siembra')
const form = ref({ lote_id: '', cultivo: '', temperatura: 25, sintomas: [] })
const lotes = ref([])
const sintomasLista = ref([])
const resultado = ref(null)

const pedir = async (ruta, opciones = {}) => {
  const r = await fetch(`${API}/${ruta}`, opciones)
  const data = await r.json()
  if (!r.ok) throw new Error(data.error || 'Error del servidor')
  return data
}

onMounted(async () => {
  try {
    lotes.value = await pedir('lotes')
    sintomasLista.value = await pedir('sintomas')
  } catch (e) {
    ElMessage.error(e.message)
  }
})

const consultar = async () => {
  const f = form.value
  const cuerpo = {
    siembra: { lote_id: f.lote_id, cultivo: f.cultivo },
    riego: { lote_id: f.lote_id, temperatura: f.temperatura },
    plagas: { lote_id: f.lote_id, sintomas: f.sintomas },
  }[tipo.value]
  try {
    resultado.value = await pedir(`diagnostico/${tipo.value}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cuerpo),
    })
  } catch (e) {
    resultado.value = null
    ElMessage.error(e.message)
  }
}

const tipoAlerta = computed(() =>
  ({ baja: 'success', media: 'warning', alta: 'error' })[resultado.value?.severidad] || 'info')
</script>

<template>
  <div>
    <h2> Sistema Experto Agrícola</h2>
    <p>Diagnósticos de siembra, riego y plagas con SWI-Prolog.</p>
    <el-card>
      <el-form label-width="150px">
        <el-form-item label="Consulta">
          <el-radio-group v-model="tipo" @change="resultado = null">
            <el-radio-button value="siembra">Siembra</el-radio-button>
            <el-radio-button value="riego">Riego</el-radio-button>
            <el-radio-button value="plagas">Plagas</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Lote">
          <el-select v-model="form.lote_id" placeholder="Selecciona un lote" style="width: 100%">
            <el-option v-for="l in lotes" :key="l.id" :label="l.nombre" :value="l.id" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="tipo === 'siembra'" label="Cultivo">
          <el-input v-model="form.cultivo" placeholder="Ej. maíz, frijol..." />
        </el-form-item>
        <el-form-item v-if="tipo === 'riego'" label="Temperatura (°C)">
          <el-input-number v-model="form.temperatura" :min="-10" :max="60" />
        </el-form-item>
        <el-form-item v-if="tipo === 'plagas'" label="Síntomas">
          <el-select v-model="form.sintomas" multiple filterable style="width: 100%"
                     placeholder="Elige los síntomas observados">
            <el-option v-for="s in sintomasLista" :key="s" :label="s.replaceAll('_', ' ')" :value="s" />
          </el-select>
        </el-form-item>
        <el-button type="success" @click="consultar">Consultar Experto</el-button>
      </el-form>
    </el-card>
    <el-alert v-if="resultado" :type="tipoAlerta" :title="resultado.conclusion"
              :description="resultado.recomendacion" show-icon :closable="false"
              style="margin-top: 20px" />
  </div>
</template>
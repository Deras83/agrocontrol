<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const API = 'http://127.0.0.1:5000/api'
const STOCK_BAJO = 10 // por debajo de esta cantidad se muestra el aviso "Bajo"
const UNIDADES = { fertilizante: 'kg', plaguicida: 'l', semilla: 'kg' }
const lista = ref([])
const dialogo = ref(false)
const vacio = () => ({
  nombre: '', tipo: 'fertilizante', stock: 0, unidad: 'kg', costo_unitario: 0, dosis_por_ha: 0,
  n: 0, p: 0, k: 0, periodo_carencia_dias: 0, tasa_germinacion: 90,
})
const form = ref(vacio())
const campos = computed(() => {
  const f = form.value
  if (f.tipo === 'fertilizante') return { n: f.n, p: f.p, k: f.k }
  if (f.tipo === 'plaguicida') return { periodo_carencia_dias: f.periodo_carencia_dias }
  return { tasa_germinacion: f.tasa_germinacion }
})

const pedir = async (ruta, opciones = {}) => {
  const r = await fetch(`${API}/${ruta}`, opciones)
  const data = await r.json()
  if (!r.ok) throw new Error(data.error || 'Error del servidor')
  return data
}
const enviar = (metodo, cuerpo) => ({
  method: metodo,
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(cuerpo),
})

const cargar = async () => {
  try {
    lista.value = await pedir('insumos')
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const detalle = (i) => {
  if (i.tipo === 'fertilizante') return `N-P-K: ${i.n}-${i.p}-${i.k}`
  if (i.tipo === 'plaguicida') return `Carencia: ${i.periodo_carencia_dias} días`
  return `Germinación: ${i.tasa_germinacion}%`
}

const abrir = () => {
  form.value = vacio()
  dialogo.value = true
}

const guardar = async () => {
  const f = form.value
  const cuerpo = { nombre: f.nombre, tipo: f.tipo, stock: f.stock, unidad: f.unidad,
    costo_unitario: f.costo_unitario, dosis_por_ha: f.dosis_por_ha, ...campos.value }
  try {
    await pedir('insumos', enviar('POST', cuerpo))
    ElMessage.success('Insumo registrado')
    dialogo.value = false
    cargar()
  } catch (e) {
    ElMessage.error(e.message)
  }
}

const reabastecer = async (i) => {
  try {
    const { value } = await ElMessageBox.prompt(`Cantidad a agregar (${i.unidad})`, `Reabastecer ${i.nombre}`, {
      inputPattern: /^\d+(\.\d+)?$/, inputErrorMessage: 'Escribe un número mayor a 0',
    })
    await pedir(`insumos/${i.id}/reabastecer`, enviar('POST', { cantidad: Number(value) }))
    ElMessage.success('Inventario actualizado')
    cargar()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message)
  }
}

const eliminar = async (i) => {
  try {
    await ElMessageBox.confirm(`¿Eliminar "${i.nombre}"?`, 'Confirmar', { type: 'warning' })
    await pedir(`insumos/${i.id}`, { method: 'DELETE' })
    ElMessage.success('Insumo eliminado')
    cargar()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error(e.message)
  }
}

onMounted(cargar)
</script>

<template>
  <div>
    <h2>Insumos</h2>
    <el-button type="primary" style="margin-bottom: 20px" @click="abrir">Registrar insumo</el-button>
    <el-table :data="lista" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="nombre" label="Nombre" />
      <el-table-column prop="tipo" label="Tipo" width="120" />
      <el-table-column label="Stock" width="150">
        <template #default="{ row }">
          {{ row.stock }} {{ row.unidad }}
          <el-tag v-if="row.stock < STOCK_BAJO" type="warning" size="small">Bajo</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="costo_unitario" label="Costo unit." width="110" />
      <el-table-column prop="dosis_por_ha" label="Dosis/ha" width="100" />
      <el-table-column label="Detalle" min-width="160">
        <template #default="{ row }">{{ detalle(row) }}</template>
      </el-table-column>
      <el-table-column label="Acciones" width="190">
        <template #default="{ row }">
          <el-button size="small" type="success" @click="reabastecer(row)">Reabastecer</el-button>
          <el-button size="small" type="danger" @click="eliminar(row)">Eliminar</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogo" title="Registrar insumo" width="520px">
      <el-form :model="form" label-width="130px">
        <el-form-item label="Nombre"><el-input v-model="form.nombre" /></el-form-item>
        <el-form-item label="Tipo">
          <el-select v-model="form.tipo" style="width: 100%" @change="form.unidad = UNIDADES[form.tipo]">
            <el-option label="Fertilizante" value="fertilizante" />
            <el-option label="Plaguicida" value="plaguicida" />
            <el-option label="Semilla" value="semilla" />
          </el-select>
        </el-form-item>
        <el-form-item label="Stock inicial"><el-input-number v-model="form.stock" :min="0" :step="5" /></el-form-item>
        <el-form-item label="Unidad"><el-input v-model="form.unidad" /></el-form-item>
        <el-form-item label="Costo unitario"><el-input-number v-model="form.costo_unitario" :min="0" /></el-form-item>
        <el-form-item label="Dosis por ha"><el-input-number v-model="form.dosis_por_ha" :min="0" /></el-form-item>
        <template v-if="form.tipo === 'fertilizante'">
          <el-form-item label="N (%)"><el-input-number v-model="form.n" :min="0" :max="100" /></el-form-item>
          <el-form-item label="P (%)"><el-input-number v-model="form.p" :min="0" :max="100" /></el-form-item>
          <el-form-item label="K (%)"><el-input-number v-model="form.k" :min="0" :max="100" /></el-form-item>
        </template>
        <el-form-item v-if="form.tipo === 'plaguicida'" label="Carencia (días)">
          <el-input-number v-model="form.periodo_carencia_dias" :min="0" />
        </el-form-item>
        <el-form-item v-if="form.tipo === 'semilla'" label="Germinación (%)">
          <el-input-number v-model="form.tasa_germinacion" :min="1" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogo = false">Cancelar</el-button>
        <el-button type="primary" @click="guardar">Guardar</el-button>
      </template>
    </el-dialog>
  </div>
</template>
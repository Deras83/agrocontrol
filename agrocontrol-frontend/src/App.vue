<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { DataBoard, Document, MapLocation, Orange, MagicStick, Notebook, Van, Cpu, FirstAidKit, Sunny, Box } from '@element-plus/icons-vue'

const route = useRoute()
const colapsado = ref(false) // escritorio: menú de solo iconos
const menuAbierto = ref(false) // teléfono: menú deslizable
const movil = ref(window.innerWidth <= 768)

const medir = () => { movil.value = window.innerWidth <= 768 }
onMounted(() => window.addEventListener('resize', medir))
onUnmounted(() => window.removeEventListener('resize', medir))
watch(() => route.path, () => { menuAbierto.value = false })

const alternarMenu = () => {
  if (movil.value) menuAbierto.value = !menuAbierto.value
  else colapsado.value = !colapsado.value
}
</script>

<template>
  <el-container class="layout-container">
    <!-- Menú lateral: se pliega a solo iconos -->
    <div v-if="movil && menuAbierto" class="overlay" @click="menuAbierto = false" />
    <el-aside :width="movil || !colapsado ? '240px' : '72px'" class="aside" :class="{ 'aside-movil': movil, abierto: menuAbierto }">
      <div class="logo-container">
        <h2><el-icon style="color: #22c55e; vertical-align: middle"><Sunny /></el-icon><span class="txt"> AgroControl</span></h2>
      </div>
      <el-menu :default-active="route.path" :class="{ plegado: colapsado && !movil }" router>
        <el-menu-item-group title="Panel">
          <el-menu-item index="/" title="Dashboard"><el-icon class="ico"><DataBoard /></el-icon><span class="txt">Dashboard</span></el-menu-item>
          <el-menu-item index="/reporte" title="Reporte"><el-icon class="ico"><Document /></el-icon><span class="txt">Reporte</span></el-menu-item>
        </el-menu-item-group>
        <el-menu-item-group title="Terreno">
          <el-menu-item index="/fincas" title="Lotes"><el-icon class="ico"><MapLocation /></el-icon><span class="txt">Lotes</span></el-menu-item>
          <el-menu-item index="/cultivos" title="Cultivos"><el-icon class="ico"><Orange /></el-icon><span class="txt">Cultivos</span></el-menu-item>
        </el-menu-item-group>
        <el-menu-item-group title="Operaciones">
          <el-menu-item index="/insumos" title="Insumos"><el-icon class="ico"><Box /></el-icon><span class="txt">Insumos</span></el-menu-item>
          <el-menu-item index="/aplicaciones" title="Aplicaciones"><el-icon class="ico"><MagicStick /></el-icon><span class="txt">Aplicaciones</span></el-menu-item>
          <el-menu-item index="/bitacora" title="Bitácora"><el-icon class="ico"><Notebook /></el-icon><span class="txt">Bitácora</span></el-menu-item>
          <el-menu-item index="/cosechas" title="Cosechas"><el-icon class="ico"><Van /></el-icon><span class="txt">Cosechas</span></el-menu-item>
        </el-menu-item-group>
        <el-menu-item-group title="Asesor">
          <el-menu-item index="/prolog" title="Sistema Experto"><el-icon class="ico"><Cpu /></el-icon><span class="txt">Sistema Experto</span></el-menu-item>
          <el-menu-item index="/diagnosticos" title="Diagnósticos"><el-icon class="ico"><FirstAidKit /></el-icon><span class="txt">Diagnósticos</span></el-menu-item>
        </el-menu-item-group>
      </el-menu>
    </el-aside>

    <!-- Contenido Principal -->
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <div class="header-izq">
            <button class="hamburguesa" title="Mostrar u ocultar menú" @click="alternarMenu">
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <h3>Panel de Gestión Agrícola</h3>
          </div>
          <span class="user-info">Administrador</span>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>
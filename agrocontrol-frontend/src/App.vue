<script setup lang="ts">
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<template>
  <el-container class="layout-container">
    <!-- Menú Lateral -->
    <el-aside width="240px" class="aside">
      <div class="logo-container">
        <h2>🌾 AgroControl</h2>
      </div>
      <el-menu
        :default-active="route.path"
        class="el-menu-vertical"
        background-color="#1f2d3d"
        text-color="#fff"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/">
          <span>📊 Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/fincas">
          <span>🏡 Fincas y Lotes</span>
        </el-menu-item>
        <el-menu-item index="/cultivos">
          <span>🌱 Cultivos</span>
        </el-menu-item>
        <el-menu-item index="/prolog">
          <span>🤖 Sistema Experto (Prolog)</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- Contenido Principal -->
    <el-container>
      <el-header class="header">
        <div class="header-content">
          <h3>Panel de Gestión Agrícola</h3>
          <span class="user-info">Administrador</span>
        </div>
      </el-header>

      <el-main class="main-content">
        <!-- Aquí se cargan dinámicamente las vistas del Router -->
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: #1f2d3d;
  color: #fff;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #3a4750;
}

.logo-container h2 {
  font-size: 1.2rem;
  color: #fff;
}

.el-menu-vertical {
  border-right: none;
}

.header {
  background-color: #ffffff;
  border-bottom: 1px solid #dcdfe6;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  font-weight: 500;
  color: #606266;
}

.main-content {
  background-color: #f4f7f6;
  padding: 20px;
}
</style>
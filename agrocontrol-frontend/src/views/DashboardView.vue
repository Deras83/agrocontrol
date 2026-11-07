<script setup lang="ts">
</script>

<template>
  <div>
    <h2>📊 Dashboard General</h2>
    <p>Resumen global de fincas, lotes activos y estado del sistema.</p>
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="8">
        <el-card shadow="hover">
          <h3>Fincas Activas</h3>
          <p style="font-size: 2rem; font-weight: bold; color: #409EFF;">12</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <h3>Lotes Registrados</h3>
          <p style="font-size: 2rem; font-weight: bold; color: #67C23A;">45</p>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <h3>Alertas Activas</h3>
          <p style="font-size: 2rem; font-weight: bold; color: #E6A23C;">3</p>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>
<script setup lang="ts">
</script>

<template>
  <div>
    <h2>🤖 Sistema Experto Agrícola</h2>
    <p>Diagnóstico de plagas y recomendaciones de cultivo alimentado por SWI-Prolog.</p>
    <el-card>
      <el-form label-width="150px">
        <el-form-item label="Observación">
          <el-input placeholder="Ej. Hojas amarillas en maíz..." />
        </el-form-item>
        <el-button type="success">Consultar Experto</el-button>
      </el-form>
    </el-card>
  </div>
</template>
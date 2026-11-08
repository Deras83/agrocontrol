import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import FincasView from '../views/FincasView.vue'
import PrologView from '../views/PrologView.vue'
import CultivosView from '../views/CultivosView.vue'
import AplicacionesView from '../views/AplicacionesView.vue'
import DiagnosticosView from '../views/DiagnosticosView.vue'
import BitacoraView from '../views/BitacoraView.vue'
import CosechasView from '../views/CosechasView.vue'
import ReporteView from '../views/ReporteView.vue'
import InsumosView from '../views/InsumosView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/fincas',
      name: 'fincas',
      component: FincasView
    },
    {
      path: '/prolog',
      name: 'prolog',
      component: PrologView
    },
    {
      path: '/cultivos',
      name: 'cultivos',
      component: CultivosView
    },
    {
      path: '/insumos',
      name: 'insumos',
      component: InsumosView
    },
    {
      path: '/aplicaciones',
      name: 'aplicaciones',
      component: AplicacionesView
    },
    {
      path: '/diagnosticos',
      name: 'diagnosticos',
      component: DiagnosticosView
    },
    {
      path: '/bitacora',
      name: 'bitacora',
      component: BitacoraView
    },
    {
      path: '/cosechas',
      name: 'cosechas',
      component: CosechasView
    },
    {
      path: '/reporte',
      name: 'reporte',
      component: ReporteView
    }
  ]
})

export default router
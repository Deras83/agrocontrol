import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '../views/DashboardView.vue'
import FincasView from '../views/FincasView.vue'
import PrologView from '../views/PrologView.vue'
import CultivosView from '../views/CultivosView.vue'

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
    }
  ]
})

export default router
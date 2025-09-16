import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import DashboardCards from './views/DashboardCards.vue';
import DashboardHeatmap from './views/DashboardHeatmap.vue';
import DashboardMinimalista from './views/DashboardMinimalista.vue';
import Services from '@/views/Services.vue'
import CreateService from '@/views/CreateService.vue'
import Products from '@/views/Products.vue'

const routes = [
  { path: '/', name: 'Dashboard', component: Dashboard },
  { path: '/cards', component: DashboardCards },
  { path: '/heatmap', component: DashboardHeatmap },
  { path: '/minimalista', component: DashboardMinimalista },
  { path: '/services', name: 'Services', component: Services },
  { path: '/create-service', name: 'CreateService', component: CreateService },
  { path: '/products', name: 'Products', component: Products },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
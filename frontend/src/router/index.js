import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Analysis from '../views/Analysis.vue'
import FrequencyCalculator from '../views/FrequencyCalculator.vue'
import Algorithms from '../views/Algorithms.vue'
import GuideSpecs from '../views/GuideSpecs.vue'
import History from '../views/History.vue'
import PHMTraining from '../views/PHMTraining.vue'
import PHMTesting from '../views/PHMTesting.vue'
import PHMDatabase from '../views/PHMDatabase.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: Analysis
    },
    {
      path: '/frequency',
      name: 'frequency',
      component: FrequencyCalculator
    },
    {
      path: '/algorithms',
      name: 'algorithms',
      component: Algorithms
    },
    {
      path: '/guide-specs',
      name: 'guide-specs',
      component: GuideSpecs
    },
    {
      path: '/history',
      name: 'history',
      component: History
    },
    {
      path: '/phm-training',
      name: 'phm-training',
      component: PHMTraining
    },
    {
      path: '/phm-testing',
      name: 'phm-testing',
      component: PHMTesting
    },
    {
      path: '/phm-database',
      name: 'phm-database',
      component: PHMDatabase
    }
  ]
})

export default router

import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../features/home/pages/HomeView.vue'
import LoginView from '../features/auth/pages/LoginView.vue'
import MyView from '../features/profile/pages/MyView.vue'
import RegisterView from '../features/auth/pages/RegisterView.vue'
import { useAuthStore } from '../features/auth/store/auth'
import { pinia } from '../app/pinia'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/my',
      name: 'my',
      component: MyView,
      meta: { requiresAuth: true },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
    },
  ],
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore(pinia)

  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchMe()
    } catch {
      authStore.logout()
    }
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }

  if (
    (to.name === 'login' || to.name === 'register') &&
    authStore.isAuthenticated
  ) {
    return { name: 'home' }
  }

  return true
})

export default router

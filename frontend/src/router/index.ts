import { createRouter, createWebHistory } from 'vue-router'
import useAuthStore from '@/stores/auth.ts'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/HomeView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/auth',
      component: () => import('@/layouts/AuthLayout.vue'),
      redirect: '/auth/registration',
      children: [
        {
          path: 'registration',
          name: 'Registration',
          component: () => import('@/views/RegistrationView.vue'),
          meta: { guestOnly: true },
        },
        {
          path: 'login',
          name: 'Login',
          component: () => import('@/views/LoginView.vue'),
          meta: { guestOnly: true },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: { name: 'Home' },
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (!authStore.user && !authStore.isAuthChecked) {
    await authStore.fetchUser()
  }

  const isAuthenticated = authStore.isAuthenticated

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router

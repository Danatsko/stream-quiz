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
      redirect: { name: 'Login' },
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
      path: '/main',
      component: () => import('@/layouts/MainLayout.vue'),
      redirect: { name: 'Take' },
      children: [
        {
          path: '/take',
          name: 'Take',
          component: () => import('@/views/TakeView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: '/quizzes',
          name: 'Quizzes',
          component: () => import('@/views/QuizzesView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: '/quizzes/:uuid',
          name: 'Quiz',
          component: () => import('@/views/QuizView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: '/rooms',
          name: 'Rooms',
          component: () => import('@/views/RoomsView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: '/history',
          name: 'History',
          component: () => import('@/views/HistoryView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: '/settings',
          name: 'Settings',
          component: () => import('@/views/SettingsView.vue'),
          meta: { requiresAuth: true },
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
    await authStore.getMe()
  }

  const isAuthenticated = authStore.isAuthenticated

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Home' })

    return
  }

  if (to.meta.guestOnly && isAuthenticated) {
    next({ name: 'Take' })

    return
  }

  next()
})

export default router

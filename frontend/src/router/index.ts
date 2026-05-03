import { createRouter, createWebHistory, RouterView } from 'vue-router'
import useAuthStore from '@/stores/auth.ts'
import { h } from 'vue'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({
  showSpinner: false,
  minimum: 0.1,
  speed: 300,
  easing: 'ease-in-out',
})

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
        {
          path: 'verify',
          name: 'Verify',
          component: () => import('@/views/VerifyView.vue'),
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
          component: { render: () => h(RouterView) },
          children: [
            {
              path: '',
              name: 'Take',
              component: () => import('@/views/TakeView.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: ':uuid',
              name: 'TakeSession',
              component: () => import('@/views/TakeSessionView.vue'),
              meta: { requiresAuth: true },
            },
          ],
        },
        {
          path: '/quizzes',
          component: { render: () => h(RouterView) },
          children: [
            {
              path: '',
              name: 'Quizzes',
              component: () => import('@/views/QuizzesView.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: ':uuid',
              name: 'Quiz',
              component: () => import('@/views/QuizView.vue'),
              meta: { requiresAuth: true, nativeScroll: true },
            },
            {
              path: ':uuid/edit',
              name: 'QuizEdit',
              component: () => import('@/views/QuizEditView.vue'),
              meta: { requiresAuth: true, nativeScroll: true },
            },
          ],
        },
        {
          path: '/rooms',
          component: { render: () => h(RouterView) },
          children: [
            {
              path: '',
              name: 'Rooms',
              component: () => import('@/views/RoomsView.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: ':uuid',
              name: 'Room',
              component: () => import('@/views/RoomView.vue'),
              meta: { requiresAuth: true, nativeScroll: true },
            },
            {
              path: ':uuid/edit',
              name: 'RoomEdit',
              component: () => import('@/views/RoomEditView.vue'),
              meta: { requiresAuth: true, nativeScroll: true },
            },
            {
              path: ':room_uuid/sessions/:uuid',
              name: 'Session',
              component: () => import('@/views/SessionView.vue'),
              meta: { requiresAuth: true, nativeScroll: true },
            },
            {
              path: ':room_uuid/sessions/:uuid/edit',
              name: 'SessionEdit',
              component: () => import('@/views/SessionEditView.vue'),
              meta: { requiresAuth: true, nativeScroll: true },
            },
          ],
        },
        {
          path: '/history',
          component: { render: () => h(RouterView) },
          children: [
            {
              path: '',
              name: 'History',
              component: () => import('@/views/HistoryView.vue'),
              meta: { requiresAuth: true },
            },
            {
              path: ':uuid',
              name: 'HistorySession',
              component: () => import('@/views/HistorySessionView.vue'),
              meta: { requiresAuth: true, nativeScroll: true },
            },
          ],
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
  NProgress.start()

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

router.afterEach(() => {
  NProgress.done()
})

router.onError(() => {
  NProgress.done()
})

export default router

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth'
import useNotificationsStore from '@/stores/notifications'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

const isVerifying = ref(true)

onMounted(async () => {
  const token = route.query.token as string
  if (!token) {
    notificationsStore.addNotification('Verification token is missing', 'error')
    await router.push({ name: 'Home' })

    return
  }

  try {
    await authStore.verify({ token })
    notificationsStore.addNotification('Account verified successfully', 'success')
    await router.push({ name: 'Take' })
  } catch (error) {
    await router.push({ name: 'Login' })
  } finally {
    isVerifying.value = false
  }
})
</script>

<template>
  <div class="layout">
    <div class="header">
      <h1 class="header-title">Account verification</h1>
      <p class="header-subtitle">Please wait while we verify your account</p>
    </div>
    <div class="main">
      <div v-if="isVerifying" class="loading-state">
        <Icon icon="mdi:loading" class="spin-icon empty-icon" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.layout {
  width: 100vw;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: black;
}
.header {
  text-align: center;
}
.header-title {
  font-size: 1.5rem;
  font-weight: 900;
  margin-bottom: 0;
}
.header-subtitle {
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 0;
  margin-bottom: 1rem;
}
.main {
  display: flex;
  justify-content: center;
  min-height: 100px;
}
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.empty-icon {
  font-size: 3rem;
  color: var(--color-primary);
}
.spin-icon {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

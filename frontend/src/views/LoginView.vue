<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import { ref, computed, onUnmounted } from 'vue'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth.ts'
import { useRouter } from 'vue-router'
import AppInput from '@/components/AppInput.vue'
import useNotificationsStore from '@/stores/notifications.ts'

interface LoginFormState {
  email: string
  password: string
}

const MIN_PASSWORD_LENGTH = 8

const authStore = useAuthStore()
const router = useRouter()
const notificationsStore = useNotificationsStore()
const isUnverified = ref(false)
const resendCooldown = ref(0)
let resendTimer: number | ReturnType<typeof setInterval> | null = null

const loginForm = ref<LoginFormState>({
  email: '',
  password: '',
})

onUnmounted(() => {
  if (resendTimer) {
    clearInterval(resendTimer)

    resendTimer = null
  }
})

const isEmailValid = computed((): boolean => {
  const { email } = loginForm.value
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  return !!email && emailRegex.test(email)
})

const isPasswordValid = computed((): boolean => {
  const { password } = loginForm.value

  return !!password && password.length >= MIN_PASSWORD_LENGTH
})

const isFormValid = computed((): boolean => {
  const f = loginForm.value
  const isNotEmpty = !!f.email && !!f.password

  return isNotEmpty && isPasswordValid.value && isEmailValid.value
})

const handleSubmit = async () => {
  if (!isFormValid.value) {
    return
  }

  isUnverified.value = false

  try {
    await authStore.login({
      email: loginForm.value.email,
      password: loginForm.value.password,
    })
    await router.push({ name: 'Take' })
  } catch (error: any) {
    if (
      error.response?.status === 403 &&
      error.response?.data?.detail === 'Account is not verified'
    ) {
      isUnverified.value = true
    }
  }
}

const handleResend = async () => {
  if (resendCooldown.value > 0) {
    return
  }

  try {
    await authStore.resendVerification({ email: loginForm.value.email })
    notificationsStore.addNotification('Verification email resent successfully', 'success')

    resendCooldown.value = 60

    if (resendTimer) {
      clearInterval(resendTimer)
    }

    resendTimer = setInterval(() => {
      resendCooldown.value--

      if (resendCooldown.value <= 0) {
        if (resendTimer) {
          clearInterval(resendTimer)
        }

        resendTimer = null
      }
    }, 1000)
  } catch (error) {}
}
</script>

<template>
  <div class="layout">
    <div class="header">
      <h1 class="header-title">Welcome back</h1>
      <p class="header-subtitle">Continue your journey with us</p>
    </div>

    <div class="main">
      <form class="form" @submit.prevent="handleSubmit">
        <AppInput
          :style="{ color: 'black' }"
          id="email"
          type="email"
          label="Email"
          placeholder="xxxxx@xxxxx.xxxxx"
          v-model="loginForm.email"
          :has-error="!!loginForm.email && !isEmailValid"
          error-message="Invalid email"
          required
        >
          <template v-slot:icon>
            <Icon icon="mdi:email-outline" />
          </template>
        </AppInput>

        <AppInput
          :style="{ color: 'black' }"
          id="password"
          type="password"
          label="Password"
          placeholder="••••••••"
          v-model="loginForm.password"
          :minlength="MIN_PASSWORD_LENGTH"
          :has-error="!!loginForm.password && !isPasswordValid"
          :error-message="`Minimum ${MIN_PASSWORD_LENGTH} characters`"
          required
        >
          <template v-slot:icon>
            <Icon icon="mdi:password-outline" />
          </template>
        </AppInput>

        <AppButton
          class="btn-signin"
          type="submit"
          :disabled="!isFormValid || authStore.isLoading"
          title="Sign in"
          aria-label="Sign in"
        >
          {{ authStore.isLoading ? 'Processing' : 'Sign in' }}
        </AppButton>

        <AppButton
          v-if="isUnverified"
          type="button"
          @click.prevent="handleResend"
          :disabled="resendCooldown > 0 || authStore.isLoading"
          title="Resend verification email"
          aria-label="Resend verification email"
        >
          {{
            resendCooldown > 0
              ? `Resend available in ${resendCooldown}s`
              : 'Resend verification email'
          }}
        </AppButton>
      </form>
    </div>

    <div class="footer">
      <p class="footer-subtitle">
        Don't have an account?
        <RouterLink class="signup-link" :to="{ name: 'Registration' }">Sign up</RouterLink>
      </p>
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
}
.form {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.5rem;
}
.btn-signin {
  align-self: center;
}

.footer {
  text-align: center;
  color: black;
  font-size: 0.9rem;
}
.footer-subtitle {
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 0;
}
.signup-link {
  font-weight: 700;
  text-decoration: none;
  background: var(--linear-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: pointer;
  transition: opacity 0.2s;
}
.signup-link:hover {
  opacity: 0.5;
  text-decoration: underline;
}
</style>

<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth.ts'
import { useRouter } from 'vue-router'
import AppInput from '@/components/AppInput.vue'

interface RegistrationFormState {
  username: string
  email: string
  password: string
  confirmPassword: string
}

const MIN_PASSWORD_LENGTH = 8
const MIN_USERNAME_LENGTH = 3
const MAX_USERNAME_LENGTH = 30

const authStore = useAuthStore()
const router = useRouter()

const registrationForm = ref<RegistrationFormState>({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const isUsernameValid = computed((): boolean => {
  const { username } = registrationForm.value

  return (
    !!username && username.length >= MIN_USERNAME_LENGTH && username.length <= MAX_USERNAME_LENGTH
  )
})

const isEmailValid = computed((): boolean => {
  const { email } = registrationForm.value
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  return !!email && emailRegex.test(email)
})

const isPasswordValid = computed((): boolean => {
  const { password } = registrationForm.value

  return !!password && password.length >= MIN_PASSWORD_LENGTH
})

const isPasswordMatched = computed((): boolean => {
  const { password, confirmPassword } = registrationForm.value

  return !!confirmPassword && !!password && password === confirmPassword
})

const isFormValid = computed((): boolean => {
  const f = registrationForm.value
  const isNotEmpty = !!f.username && !!f.email && !!f.password && !!f.confirmPassword

  return (
    isNotEmpty &&
    isUsernameValid.value &&
    isPasswordValid.value &&
    isEmailValid.value &&
    isPasswordMatched.value
  )
})

const handleSubmit = async () => {
  if (!isFormValid.value) {
    return
  }

  try {
    await authStore.registration({
      username: registrationForm.value.username,
      email: registrationForm.value.email,
      password: registrationForm.value.password,
    })
    await router.push({ name: 'Take' })
  } catch (error) {}
}
</script>

<template>
  <div class="layout">
    <div class="header">
      <h1 class="header-title">Create account</h1>
      <p class="header-subtitle">Start your journey with us</p>
    </div>

    <div class="main">
      <form class="form" @submit.prevent="handleSubmit">
        <AppInput
          :style="{ color: 'black' }"
          id="username"
          type="text"
          label="Username"
          placeholder="Username"
          v-model="registrationForm.username"
          :minlength="MIN_USERNAME_LENGTH"
          :maxLength="MAX_USERNAME_LENGTH"
          :has-error="!!registrationForm.username && !isUsernameValid"
          :error-message="`Minimum ${MIN_USERNAME_LENGTH} characters`"
          required
        >
          <template v-slot:icon>
            <Icon icon="mdi:user-outline" />
          </template>
        </AppInput>

        <AppInput
          :style="{ color: 'black' }"
          id="email"
          type="email"
          label="Email"
          placeholder="xxxxx@xxxxx.xxxxx"
          v-model="registrationForm.email"
          :minlength="MIN_USERNAME_LENGTH"
          :maxLength="MAX_USERNAME_LENGTH"
          :has-error="!!registrationForm.email && !isEmailValid"
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
          v-model="registrationForm.password"
          :minlength="MIN_PASSWORD_LENGTH"
          :has-error="!!registrationForm.password && !isPasswordValid"
          :error-message="`Minimum ${MIN_PASSWORD_LENGTH} characters`"
          required
        >
          <template v-slot:icon>
            <Icon icon="mdi:password-outline" />
          </template>
        </AppInput>

        <AppInput
          :style="{ color: 'black' }"
          id="confirm-password"
          type="password"
          label="Confirm password"
          placeholder="••••••••"
          v-model="registrationForm.confirmPassword"
          :has-error="!!registrationForm.confirmPassword && !isPasswordMatched"
          error-message="Passwords do not match"
          required
        >
          <template v-slot:icon>
            <Icon icon="mdi:password-outline" />
          </template>
        </AppInput>

        <AppButton class="btn-signup" type="submit" :disabled="!isFormValid || authStore.isLoading">
          {{ authStore.isLoading ? 'Processing' : 'Sign up' }}
        </AppButton>
      </form>
    </div>

    <div class="footer">
      <p class="footer-subtitle">
        Already have an account?
        <RouterLink class="signin-link" :to="{ name: 'Login' }">Sign in</RouterLink>
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

.btn-signup {
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
.signin-link {
  font-weight: 700;
  text-decoration: none;
  background: var(--linear-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  cursor: pointer;
  transition: opacity 0.2s;
}
.signin-link:hover {
  opacity: 0.5;
  text-decoration: underline;
}
</style>

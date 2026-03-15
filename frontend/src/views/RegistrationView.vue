<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import AppErrorMessage from '@/components/AppErrorMessage.vue'
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth.ts'
import { useRouter } from 'vue-router'

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
        <div class="form-group">
          <label for="username">Username</label>
          <div class="input-wrapper">
            <Icon icon="mdi:user-outline" class="input-icon" />
            <input
              class="input"
              :class="{ 'input-error': registrationForm.username && !isUsernameValid }"
              id="username"
              type="text"
              placeholder="Username"
              v-model="registrationForm.username"
              :minlength="MIN_USERNAME_LENGTH"
              :maxLength="MAX_USERNAME_LENGTH"
              required
            />
          </div>
          <AppErrorMessage v-if="registrationForm.username && !isUsernameValid">
            Minimum {{ MIN_USERNAME_LENGTH }} characters
          </AppErrorMessage>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <div class="input-wrapper">
            <Icon icon="mdi:email-outline" class="input-icon" />
            <input
              class="input"
              :class="{ 'input-error': registrationForm.email && !isEmailValid }"
              id="email"
              type="email"
              placeholder="example@example.com"
              v-model="registrationForm.email"
              required
            />
          </div>
          <AppErrorMessage v-if="registrationForm.email && !isEmailValid">
            Invalid email
          </AppErrorMessage>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <div class="input-wrapper">
            <Icon icon="mdi:password-outline" class="input-icon" />
            <input
              class="input"
              :class="{ 'input-error': registrationForm.password && !isPasswordValid }"
              id="password"
              type="password"
              placeholder="••••••••"
              v-model="registrationForm.password"
              :minlength="MIN_PASSWORD_LENGTH"
              required
            />
          </div>
          <AppErrorMessage v-if="registrationForm.password && !isPasswordValid">
            Minimum {{ MIN_PASSWORD_LENGTH }} characters
          </AppErrorMessage>
        </div>

        <div class="form-group">
          <label for="confirm-password">Confirm password</label>
          <div class="input-wrapper">
            <Icon icon="mdi:password-outline" class="input-icon" />
            <input
              class="input"
              :class="{ 'input-error': registrationForm.confirmPassword && !isPasswordMatched }"
              id="confirm-password"
              type="password"
              placeholder="••••••••"
              v-model="registrationForm.confirmPassword"
              required
            />
          </div>
          <AppErrorMessage v-if="registrationForm.confirmPassword && !isPasswordMatched">
            Passwords do not match
          </AppErrorMessage>
        </div>

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
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  margin: 0.3rem 0;
}
.input-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
}
.input-icon {
  position: absolute;
  left: 10px;
  font-size: 1.2rem;
  pointer-events: none;
  z-index: 1;
}
.input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  box-sizing: border-box;
  border: 1px solid #000000;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  transition:
    border-color 0.3s,
    box-shadow 0.3s;
}
.input:focus {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 10px 1px var(--color-secondary);
}
.input-error {
  border-color: red;
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

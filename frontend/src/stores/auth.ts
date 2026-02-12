import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { AxiosError } from 'axios'
import type { LoginPayload, RegistrationPayload } from '@/types/auth'
import type { User } from '@/types/user'
import { authAPI } from '@/api/auth'
import { usersAPI } from '@/api/users'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isLoading = ref<boolean>(false)
  const isAuthChecked = ref<boolean>(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed((): boolean => {
    return !!user.value
  })

  const resetError = (): void => {
    error.value = null
  }

  const registration = async (payload: RegistrationPayload): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await authAPI.registration(payload)
      isAuthChecked.value = false
      await fetchUser()
    } catch (registrationError) {
      if (registrationError instanceof AxiosError) {
        error.value = registrationError.response?.data?.detail || 'Error during registration'
      }

      throw registrationError
    } finally {
      isLoading.value = false
    }
  }

  const login = async (payload: LoginPayload): Promise<void> => {
    isLoading.value = true
    resetError()

    try {
      await authAPI.login(payload)
      isAuthChecked.value = false
      await fetchUser()
    } catch (loginError) {
      if (loginError instanceof AxiosError) {
        error.value = loginError.response?.data?.detail || 'Error during login'
      }

      throw loginError
    } finally {
      isLoading.value = false
    }
  }

  const logout = async (callAPI: boolean = true): Promise<void> => {
    isLoading.value = true

    try {
      if (callAPI) {
        await authAPI.logout()
      }
    } catch (logoutError) {
      throw logoutError
    } finally {
      user.value = null
      error.value = null
      isLoading.value = false
      isAuthChecked.value = true
    }
  }

  const fetchUser = async (): Promise<void> => {
    if (isAuthChecked.value && !user.value) {
      return
    }

    isLoading.value = true

    try {
      user.value = await usersAPI.getMe()
    } catch (fetchUserError) {
      user.value = null
    } finally {
      isLoading.value = false
      isAuthChecked.value = true
    }
  }

  return {
    user,
    isLoading,
    isAuthChecked,
    error,
    isAuthenticated,
    registration,
    login,
    logout,
    fetchUser,
  }
})

export default useAuthStore

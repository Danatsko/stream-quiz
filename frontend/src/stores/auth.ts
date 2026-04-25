import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LoginPayload, RegistrationPayload } from '@/types/auth'
import type { User } from '@/types/user'
import { authAPI } from '@/api/auth'
import { usersAPI } from '@/api/users'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isLoading = ref<boolean>(false)
  const isAuthChecked = ref<boolean>(false)

  const isAuthenticated = computed((): boolean => {
    return !!user.value
  })

  const registration = async (payload: RegistrationPayload): Promise<void> => {
    isLoading.value = true

    try {
      await authAPI.registration(payload)
      isAuthChecked.value = false
      await getMe()
    } catch (registrationError) {
      throw registrationError
    } finally {
      isLoading.value = false
    }
  }

  const login = async (payload: LoginPayload): Promise<void> => {
    isLoading.value = true

    try {
      await authAPI.login(payload)
      isAuthChecked.value = false
      await getMe()
    } catch (loginError) {
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
      isLoading.value = false
      isAuthChecked.value = true
    }
  }

  const getMe = async (): Promise<void> => {
    if (isAuthChecked.value && !user.value) {
      return
    }

    isLoading.value = true

    try {
      user.value = await usersAPI.getMe()
    } catch (getMeError) {
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
    isAuthenticated,
    registration,
    login,
    logout,
    getMe,
  }
})

export default useAuthStore

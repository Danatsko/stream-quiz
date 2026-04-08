<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppButton from '@/components/AppButton.vue'
import AppErrorMessage from '@/components/AppErrorMessage.vue'
import useTakeStore from '@/stores/take'

const UUID_LENGTH = 36
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

const sessionUuid = ref<string>('')
const isLoading = ref<boolean>(false)
const error = ref<string | null>(null)

const takeStore = useTakeStore()
const router = useRouter()

const isUuidValid = computed((): boolean => {
  return !!sessionUuid.value && UUID_REGEX.test(sessionUuid.value)
})

const handleJoin = async () => {
  if (!isUuidValid.value || isLoading.value) {
    return
  }

  isLoading.value = true
  error.value = null

  try {
    takeStore.connectToSession(sessionUuid.value)

    const unwatch = watch(
      () => [takeStore.isConnected, takeStore.error],
      ([connected, joinError]) => {
        if (connected) {
          unwatch()
          isLoading.value = false

          // TODO: Add routing to take session view
        } else if (joinError) {
          unwatch()
          isLoading.value = false
          error.value = joinError as string

          takeStore.disconnectFromSession()
        }
      },
    )
  } catch (joinError) {
    isLoading.value = false
    error.value = 'Error during join'
  }
}
</script>

<template>
  <div class="layout">
    <div class="header">
      <h1 class="header-title">Join</h1>
      <p class="header-subtitle">Enter the session uuid to participate</p>
    </div>

    <div class="main">
      <form class="form" @submit.prevent="handleJoin">
        <div class="form-group">
          <label for="session-uuid">Session UUID</label>
          <input
            class="input"
            :class="{ 'input-error': sessionUuid && !isUuidValid }"
            id="session-uuid"
            type="text"
            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            v-model="sessionUuid"
            :minlength="UUID_LENGTH"
            :maxLength="UUID_LENGTH"
            required
          />
          <AppErrorMessage v-if="sessionUuid && !isUuidValid">
            Invalid uuid format
          </AppErrorMessage>
        </div>

        <AppButton class="btn-join" type="submit" :disabled="!isUuidValid || isLoading">
          {{ isLoading ? 'Processing' : 'Join' }}
        </AppButton>
      </form>
    </div>
  </div>
</template>

<style scoped>
.layout {
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  box-sizing: border-box;
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
  margin-bottom: 1.5rem;
  color: var(--color-text-secondary);
  opacity: 0.8;
}

.main {
  display: flex;
  justify-content: center;
  width: 100%;
  max-width: 400px;
}
.form {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 1rem;
  width: 100%;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
label {
  font-size: 0.9rem;
  font-weight: 600;
}
.input {
  width: 100%;
  padding: 0.75rem 1rem;
  box-sizing: border-box;
  background-color: transparent;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--color-text);
  outline: none;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
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
.btn-join {
  align-self: center;
  width: 100%;
  margin-top: 0.5rem;
}
</style>

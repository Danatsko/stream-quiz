<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import AppButton from '@/components/AppButton.vue'
import useTakeStore from '@/stores/take'
import { Icon } from '@iconify/vue'
import AppInput from '@/components/AppInput.vue'

const UUID_LENGTH = 36
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

const sessionUuid = ref<string>('')
const isLoading = ref<boolean>(false)
const takeStore = useTakeStore()
const router = useRouter()

const isUuidValid = computed((): boolean => {
  return !!sessionUuid.value && UUID_REGEX.test(sessionUuid.value)
})

watch(sessionUuid, () => {
  if (takeStore.error) {
    takeStore.error = null
  }
})

const handleTake = async () => {
  if (!isUuidValid.value) {
    return
  }

  try {
    isLoading.value = true
    takeStore.error = null

    await router.push({
      name: 'TakeSession',
      params: {
        uuid: sessionUuid.value,
      },
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="layout">
    <div class="header">
      <h1 class="header-title">Take</h1>
      <p class="header-subtitle">Enter the session uuid to participate</p>
    </div>

    <div class="main">
      <form class="form" @submit.prevent="handleTake">
        <AppInput
          id="session-uuid"
          type="text"
          label=""
          placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
          v-model="sessionUuid"
          :minlength="UUID_LENGTH"
          :maxLength="UUID_LENGTH"
          :has-error="!!sessionUuid && !isUuidValid"
          error-message="Invalid uuid format"
          required
        >
          <template v-slot:icon>
            <Icon icon="mdi:identifier" />
          </template>
        </AppInput>

        <AppButton class="btn-take" type="submit" :disabled="!isUuidValid || isLoading">
          {{ isLoading ? 'Processing' : 'Take' }}
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
  margin: 0;
}
.header-subtitle {
  font-size: 0.95rem;
  margin: 0.5rem 0 1rem 0;
  color: var(--color-text-secondary);
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

label {
  font-size: 0.9rem;
  font-weight: 600;
}

.btn-take {
  align-self: center;
  width: 100%;
  margin-top: 0.5rem;
}
</style>

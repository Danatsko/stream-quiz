<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth'
import useRoomsStore from '@/stores/rooms'
import { useRoute, useRouter } from 'vue-router'
import AppModal from '@/components/AppModal.vue'
import AppListCard from '@/components/AppListCard.vue'
import AppDurationInput from '@/components/AppDurationInput.vue'
import AppInput from '@/components/AppInput.vue'
import AppTextarea from '@/components/AppTextarea.vue'

interface EditSession {
  title: string
  description: string
  time_seconds: number | null
  quiz_uuid: string
}

const MIN_TITLE_LENGTH = 3
const MAX_TITLE_LENGTH = 100
const MAX_DESCRIPTION_LENGTH = 500
const MIN_TIME_SECONDS = 1
const MAX_TIME_SECONDS = 604800
const QUIZ_UUID_LENGTH = 36
const QUIZ_UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const roomsStore = useRoomsStore()

const isDeleteSessionDialogOpen = ref(false)
const roomUuid = computed(() => route.params.room_uuid as string)
const sessionUuid = computed(() => route.params.uuid as string)
const session = computed(() => roomsStore.session)
const isLoading = computed(() => roomsStore.isLoading)
const isSaving = ref(false)

const currentUserUuid = computed((): string | null => {
  return authStore.user === null ? null : authStore.user.uuid
})

const editableSession = ref<EditSession | null>(null)

const initEditableSession = (): void => {
  if (!session.value) {
    return
  }

  editableSession.value = {
    title: session.value.title,
    description: session.value.description,
    time_seconds: session.value.time_seconds,
    quiz_uuid: session.value.quiz_uuid || '',
  }
}

watch(session, initEditableSession)

const goBack = async (): Promise<void> => {
  await router.push({
    name: 'Session',
    params: {
      room_uuid: roomUuid.value,
      uuid: sessionUuid.value,
    },
  })
}

onMounted(async () => {
  if (sessionUuid.value) {
    try {
      await roomsStore.getSession(roomUuid.value, sessionUuid.value)

      if (!session.value) {
        await router.push({ name: 'Room', params: { uuid: roomUuid.value } })
        return
      }

      if (session.value.status !== 'waiting') {
        await router.push({
          name: 'Session',
          params: {
            room_uuid: roomUuid.value,
            uuid: sessionUuid.value,
          },
        })
        return
      }
    } catch (onMountedError) {
      await router.push({ name: 'Room', params: { uuid: roomUuid.value } })
    }
  }
})

onBeforeUnmount(() => {
  roomsStore.clearSession()
})

const isTitleValid = computed((): boolean => {
  if (!editableSession.value) {
    return false
  }

  const { title } = editableSession.value

  return !!title && title.length >= MIN_TITLE_LENGTH && title.length <= MAX_TITLE_LENGTH
})

const isDescriptionValid = computed((): boolean => {
  if (!editableSession.value) {
    return false
  }

  const { description } = editableSession.value

  return !description || description.length <= MAX_DESCRIPTION_LENGTH
})

const isTimeSecondsValid = computed((): boolean => {
  if (!editableSession.value) {
    return false
  }

  const { time_seconds } = editableSession.value

  return !!time_seconds && time_seconds >= MIN_TIME_SECONDS && time_seconds <= MAX_TIME_SECONDS
})

const isQuizUuidValid = computed((): boolean => {
  if (!editableSession.value) {
    return false
  }

  const { quiz_uuid } = editableSession.value

  return !!quiz_uuid && quiz_uuid.length == QUIZ_UUID_LENGTH && QUIZ_UUID_REGEX.test(quiz_uuid)
})

const isFormValid = computed((): boolean => {
  if (!editableSession.value) {
    return false
  }

  return (
    isTitleValid.value &&
    isDescriptionValid.value &&
    isTimeSecondsValid.value &&
    isQuizUuidValid.value
  )
})

const hasChanges = computed((): boolean => {
  if (!editableSession.value || !session.value) {
    return false
  }

  const normalizeData = (data: any) => ({
    title: data.title,
    description: data.description,
    time_seconds: data.time_seconds,
    quiz_uuid: data.quiz_uuid || '',
  })

  const originalStr = JSON.stringify(normalizeData(session.value))
  const editedStr = JSON.stringify(normalizeData(editableSession.value))

  return originalStr !== editedStr
})

const saveChanges = async (): Promise<void> => {
  if (!editableSession.value || !session.value || !isFormValid.value || !hasChanges.value) {
    return
  }

  try {
    isSaving.value = true

    const payload = {
      title: editableSession.value.title,
      description: editableSession.value.description,
      time_seconds: editableSession.value.time_seconds as number,
      quiz_uuid: editableSession.value.quiz_uuid,
    }

    await roomsStore.updateSession(roomUuid.value, sessionUuid.value, payload)
    await goBack()
  } catch (error) {
  } finally {
    isSaving.value = false
  }
}

const openDeleteSessionDialog = (): void => {
  isDeleteSessionDialogOpen.value = true
}

const closeDeleteSessionDialog = (): void => {
  isDeleteSessionDialogOpen.value = false
}

const confirmDeleteSession = async (): Promise<void> => {
  try {
    await roomsStore.deleteSession(roomUuid.value, sessionUuid.value)
    closeDeleteSessionDialog()
    await router.push({ name: 'Room', params: { uuid: roomUuid.value } })
  } catch (error) {}
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content" :style="{ justifyContent: 'space-between' }">
        <AppButton @click="goBack" title="Cancel" aria-label="Cancel">
          <Icon icon="mdi:cancel-outline" />
        </AppButton>

        <div class="header-actions">
          <AppButton
            @click="saveChanges"
            :disabled="isSaving || !isFormValid || isLoading || !hasChanges"
            title="Save"
            aria-label="Save"
          >
            <span v-if="isSaving">Processing</span>
            <Icon v-else icon="mdi:content-save-outline" />
          </AppButton>
          <AppButton
            class="btn-delete"
            @click="openDeleteSessionDialog"
            title="Delete"
            aria-label="Delete"
          >
            <Icon icon="mdi:delete-outline" />
          </AppButton>
        </div>
      </div>
    </header>

    <main class="main" v-if="isLoading && !editableSession">
      <div class="empty-state">
        <Icon icon="mdi:loading" class="spin-icon empty-icon" />
        <p class="empty-text">Loading</p>
      </div>
    </main>

    <main class="main" v-else-if="editableSession">
      <div class="room-content-wrapper">
        <AppListCard>
          <template v-slot:icon>
            <Icon icon="mdi:timer-play-outline" />
          </template>

          <template v-slot:content>
            <div class="hero-top">
              <AppInput
                id="session-title"
                type="text"
                label="Title"
                placeholder="Title"
                v-model="editableSession.title"
                :minlength="MIN_TITLE_LENGTH"
                :maxLength="MAX_TITLE_LENGTH"
                :has-error="!!editableSession.title && !isTitleValid"
                :error-message="`Minimum ${MIN_TITLE_LENGTH} characters`"
              >
                <template v-slot:icon>
                  <Icon icon="mdi:format-align-left" />
                </template>
              </AppInput>
            </div>

            <AppTextarea
              id="session-description"
              label="Description"
              placeholder="Description"
              v-model="editableSession.description"
              :maxLength="MAX_DESCRIPTION_LENGTH"
            />

            <AppDurationInput
              id="session-time"
              label="Time"
              v-model="editableSession.time_seconds"
              :has-error="editableSession.time_seconds !== null && !isTimeSecondsValid"
              error-message="Invalid duration limits"
            >
              <template v-slot:icon>
                <Icon icon="mdi:timer-outline" />
              </template>
            </AppDurationInput>

            <AppInput
              id="quiz-uuid"
              type="text"
              label="Quiz uuid"
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              v-model="editableSession.quiz_uuid"
              :minlength="QUIZ_UUID_LENGTH"
              :maxLength="QUIZ_UUID_LENGTH"
              :has-error="!!editableSession.quiz_uuid && !isQuizUuidValid"
              error-message="Invalid uuid format"
            >
              <template v-slot:icon>
                <Icon icon="mdi:identifier" />
              </template>
            </AppInput>
          </template>
        </AppListCard>
      </div>
    </main>
  </div>

  <AppModal :is-open="isDeleteSessionDialogOpen" @close="closeDeleteSessionDialog">
    <template v-slot:header>
      <h1 class="modal-header-title">Delete session</h1>
    </template>

    <template v-slot:body>
      <p class="modal-text">Are you sure you want to delete this session?</p>
      <p class="modal-text">This action cannot be undone.</p>
    </template>

    <template v-slot:footer>
      <AppButton @click="closeDeleteSessionDialog" title="Cancel" aria-label="Cancel"
        >Cancel</AppButton
      >
      <AppButton
        class="btn-delete"
        @click="confirmDeleteSession"
        :disabled="roomsStore.isLoading"
        title="Delete"
        aria-label="Delete"
      >
        {{ roomsStore.isLoading ? 'Processing' : 'Delete' }}
      </AppButton>
    </template>
  </AppModal>
</template>

<style scoped>
.layout {
  width: 90vw;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  padding-bottom: 1rem;
}

.header {
  padding: 1.5rem 0.5rem;
  padding-right: 1rem;
  font-weight: bold;
  flex-shrink: 0;
}
.header-content {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
.header-actions {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
}

.main {
  display: flex;
  flex-direction: column;
}

.room-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 0.25rem 1rem 0.25rem 0.5rem;
}

.hero-top {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  max-width: 100%;
}
.modal-header-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 900;
}

.modal-text {
  font-size: 1rem;
  line-height: 1.5;
  margin: 0;
  text-align: center;
}
.btn-delete {
  color: red;
  border-color: red;
  background-color: color-mix(in srgb, red 10%, black);
}
.btn-delete:hover {
  background-color: color-mix(in srgb, red 20%, black);
  border-color: red;
  box-shadow:
    0 0 1px 1px red,
    0 0 10px 1px color-mix(in srgb, red 50%, transparent);
}
</style>

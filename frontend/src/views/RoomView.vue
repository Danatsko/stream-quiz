<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth'
import useRoomsStore from '@/stores/rooms'
import { useRoute, useRouter } from 'vue-router'
import AppModal from '@/components/AppModal.vue'
import AppAsyncList from '@/components/AppAsyncList.vue'
import AppListCard from '@/components/AppListCard.vue'
import AppBadge from '@/components/AppBadge.vue'
import { formatDateTime, formatDuration } from '@/utils/formatters'
import AppDurationInput from '@/components/AppDurationInput.vue'
import AppInput from '@/components/AppInput.vue'
import AppTextarea from '@/components/AppTextarea.vue'

interface CreateSessionFormState {
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

const sessionStatusLabels: Record<string, string> = {
  waiting: 'Waiting',
  active: 'Active',
  completed: 'Completed',
}

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const roomsStore = useRoomsStore()

const activeTab = ref('All')
const activeMenuUuid = ref<string | null>(null)
const sessionToDeleteUuid = ref<string | null>(null)
const isCreateSessionDialogOpen = ref(false)
const isDeleteSessionDialogOpen = ref(false)
const isDeleteRoomDialogOpen = ref(false)
const createSessionForm = ref<CreateSessionFormState>({
  title: '',
  description: '',
  time_seconds: null,
  quiz_uuid: '',
})

const roomUuid = computed(() => route.params.uuid as string)
const room = computed(() => roomsStore.room)
const isLoading = computed(() => roomsStore.isLoading)

const currentUserUuid = computed((): string | null => {
  return authStore.user === null ? null : authStore.user.uuid
})

const tabs = [
  { label: 'All', name: 'All' },
  { label: 'Waiting', name: 'Waiting' },
  { label: 'Active', name: 'Active' },
  { label: 'Completed', name: 'Completed' },
]

const filteredSessions = computed(() => {
  if (activeTab.value === 'Waiting') {
    return roomsStore.sessions.filter((session) => session.status === 'waiting')
  }
  if (activeTab.value === 'Active') {
    return roomsStore.sessions.filter((session) => session.status == 'active')
  }
  if (activeTab.value === 'Completed') {
    return roomsStore.sessions.filter((session) => session.status == 'completed')
  }

  return roomsStore.sessions
})

const copyToClipboard = (text: string): void => {
  navigator.clipboard.writeText(text)
}

const goToRoomEdit = async (uuid: string): Promise<void> => {
  await router.push({
    name: 'RoomEdit',
    params: {
      uuid: roomUuid.value,
    },
  })
}

const goToSession = async (uuid: string): Promise<void> => {
  await router.push({
    name: 'Session',
    params: {
      room_uuid: roomUuid.value,
      uuid: uuid,
    },
  })
}

const goToSessionEdit = async (uuid: string): Promise<void> => {
  activeMenuUuid.value = null

  await router.push({
    name: 'SessionEdit',
    params: {
      room_uuid: roomUuid.value,
      uuid: uuid,
    },
  })
}

const goBack = async (): Promise<void> => {
  await router.push({ name: 'Rooms' })
}

const openCreateSessionDialog = (): void => {
  isCreateSessionDialogOpen.value = true
  createSessionForm.value.title = ''
  createSessionForm.value.description = ''
  createSessionForm.value.time_seconds = null
  createSessionForm.value.quiz_uuid = ''
}

const closeCreateSessionDialog = (): void => {
  isCreateSessionDialogOpen.value = false
}

const toggleMenu = (uuid: string): void => {
  activeMenuUuid.value = activeMenuUuid.value === uuid ? null : uuid
}

const closeDropdowns = (): void => {
  if (activeMenuUuid.value) {
    activeMenuUuid.value = null
  }
}

onMounted(async () => {
  document.addEventListener('click', closeDropdowns)

  if (roomUuid.value) {
    try {
      await roomsStore.getRoom(roomUuid.value)

      if (!room.value) {
        await router.push({ name: 'Rooms' })

        return
      }

      if (room.value.creator_uuid !== currentUserUuid.value) {
        await router.push({ name: 'Rooms' })

        return
      }

      await roomsStore.getSessions(roomUuid.value)
    } catch (onMountedError) {
      await router.push({ name: 'Rooms' })

      return
    }
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeDropdowns)
  roomsStore.clearSessions()
  roomsStore.clearRoom()
})

const isTitleValid = computed((): boolean => {
  const { title } = createSessionForm.value

  return !!title && title.length >= MIN_TITLE_LENGTH && title.length <= MAX_TITLE_LENGTH
})

const isDescriptionValid = computed((): boolean => {
  const { description } = createSessionForm.value

  return !description || description.length <= MAX_DESCRIPTION_LENGTH
})

const isTimeSecondsValid = computed((): boolean => {
  const { time_seconds } = createSessionForm.value

  return (
    time_seconds !== null && time_seconds >= MIN_TIME_SECONDS && time_seconds <= MAX_TIME_SECONDS
  )
})

const isQuizUuidValid = computed((): boolean => {
  const { quiz_uuid } = createSessionForm.value

  return !!quiz_uuid && quiz_uuid.length == QUIZ_UUID_LENGTH && QUIZ_UUID_REGEX.test(quiz_uuid)
})

const isFormValid = computed((): boolean => {
  return (
    isTitleValid.value &&
    isDescriptionValid.value &&
    isTimeSecondsValid.value &&
    isQuizUuidValid.value
  )
})

const handleCreateSession = async (): Promise<void> => {
  if (!isFormValid.value) {
    return
  }

  try {
    const uuid = await roomsStore.createSession(roomUuid.value, {
      title: createSessionForm.value.title,
      description: createSessionForm.value.description,
      time_seconds: createSessionForm.value.time_seconds as number,
      quiz_uuid: createSessionForm.value.quiz_uuid,
    })

    closeCreateSessionDialog()
    await goToSession(uuid)
  } catch (error) {}
}

const openDeleteRoomDialog = (): void => {
  isDeleteRoomDialogOpen.value = true
}

const closeDeleteRoomDialog = (): void => {
  isDeleteRoomDialogOpen.value = false
}

const confirmDeleteRoom = async (): Promise<void> => {
  try {
    await roomsStore.deleteRoom(roomUuid.value)
    closeDeleteRoomDialog()
    await router.push({ name: 'Rooms' })
  } catch (error) {}
}

const openDeleteSessionDialog = (uuid: string): void => {
  activeMenuUuid.value = null
  sessionToDeleteUuid.value = uuid
  isDeleteSessionDialogOpen.value = true
}

const closeDeleteSessionDialog = (): void => {
  isDeleteSessionDialogOpen.value = false
  sessionToDeleteUuid.value = null
}

const confirmDeleteSession = async (): Promise<void> => {
  if (!sessionToDeleteUuid.value) {
    return
  }

  try {
    await roomsStore.deleteSession(roomUuid.value, sessionToDeleteUuid.value)
    closeDeleteSessionDialog()
  } catch (error) {}
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content" :style="{ justifyContent: 'space-between' }">
        <AppButton @click="goBack" title="Back to rooms" aria-label="Back to rooms">
          <Icon icon="mdi:chevron-left" />
        </AppButton>

        <div class="header-actions">
          <AppButton @click="goToRoomEdit" title="Edit" aria-label="Edit">
            <Icon icon="mdi:edit-outline" />
          </AppButton>
          <AppButton
            class="btn-delete"
            @click="openDeleteRoomDialog"
            title="Delete"
            aria-label="Delete"
          >
            <Icon icon="mdi:delete-outline" />
          </AppButton>
        </div>
      </div>
    </header>

    <main class="main" v-if="isLoading && !room">
      <div class="empty-state">
        <Icon icon="mdi:loading" class="spin-icon empty-icon" />
        <p class="empty-text">Loading</p>
      </div>
    </main>

    <main class="main" v-else-if="room">
      <div class="room-content-wrapper">
        <AppListCard>
          <template v-slot:icon>
            <Icon icon="mdi:cube-outline" />
          </template>

          <template v-slot:content>
            <div class="hero-top">
              <h1 class="hero-title">{{ room.title }}</h1>
            </div>

            <p class="hero-description">{{ room.description }}</p>

            <div class="hero-bottom">
              <span class="meta-item" v-if="room?.created_at">
                <Icon icon="mdi:calendar-plus" />
                {{ formatDateTime(room.created_at) }}
              </span>

              <span class="meta-item" v-if="room.updated_at">
                <Icon icon="mdi:calendar-edit" />
                {{ formatDateTime(room.updated_at) }}
              </span>

              <div class="meta-item" v-if="room.uuid">
                <Icon icon="mdi:identifier" />

                <div class="item-id" @click="copyToClipboard(room.uuid)" title="Copy UUID">
                  {{ room.uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>
            </div>
          </template>
        </AppListCard>

        <div class="main-nav">
          <AppButton
            @click="openCreateSessionDialog"
            title="Create session"
            aria-label="Create session"
            >Create session</AppButton
          >
        </div>
        <div class="main-nav">
          <div class="main-nav-tab">
            <AppButton
              v-for="tab in tabs"
              :key="tab.name"
              class="tab-btn"
              :class="{ active: activeTab === tab.name }"
              @click="activeTab = tab.name"
              :title="tab.label"
              :aria-label="tab.label"
            >
              {{ tab.label }}
            </AppButton>
          </div>
        </div>

        <div class="sessions-list-wrapper">
          <AppAsyncList
            :items="filteredSessions"
            :is-loading="roomsStore.isLoading"
            empty-icon="mdi:timer-play-outline"
            empty-title="There are no sessions"
            empty-text="No session found for the selected category"
            @load-more="() => roomsStore.getSessions(roomUuid)"
          >
            <AppListCard v-for="session in filteredSessions" :key="session.uuid">
              <template v-slot:icon>
                <Icon icon="mdi:timer-play-outline" />
              </template>

              <template v-slot:content>
                <div class="info-top">
                  <h3 class="item-title">{{ session.title }}</h3>

                  <AppBadge :class="`badge-${session.status}`">
                    {{ sessionStatusLabels[session.status] }}
                  </AppBadge>
                </div>

                <p class="item-description">{{ session.description }}</p>
                <div class="info-bottom">
                  <span class="meta-item">
                    <Icon icon="mdi:timer-outline" />
                    {{ formatDuration(session.time_seconds) }}
                  </span>

                  <div class="meta-item" v-if="session.quiz_uuid">
                    <Icon icon="mdi:book-open-variant-outline" />

                    <div
                      class="item-id"
                      @click="copyToClipboard(session.quiz_uuid)"
                      title="Copy UUID"
                    >
                      {{ session.quiz_uuid }}
                      <Icon icon="mdi:content-copy" class="copy-icon" />
                    </div>
                  </div>

                  <span class="meta-item" v-if="session.created_at">
                    <Icon icon="mdi:calendar-plus" />
                    {{ formatDateTime(session.created_at) }}
                  </span>

                  <span class="meta-item" v-if="session.updated_at">
                    <Icon icon="mdi:calendar-edit" />
                    {{ formatDateTime(session.updated_at) }}
                  </span>

                  <div class="meta-item" v-if="session.uuid">
                    <Icon icon="mdi:identifier" />

                    <div class="item-id" @click="copyToClipboard(session.uuid)" title="Copy UUID">
                      {{ session.uuid }}
                      <Icon icon="mdi:content-copy" class="copy-icon" />
                    </div>
                  </div>
                </div>
              </template>

              <template v-slot:actions>
                <AppButton @click="goToSession(session.uuid)" title="View" aria-label="View">
                  <Icon icon="mdi:eye-outline" />
                </AppButton>

                <div class="context-menu-wrapper" v-if="session.status === 'waiting'">
                  <AppButton
                    @click.stop="toggleMenu(session.uuid)"
                    title="Other actions"
                    aria-label="Other actions"
                  >
                    <Icon icon="mdi:dots-vertical" />
                  </AppButton>

                  <div class="dropdown-menu" v-if="activeMenuUuid === session.uuid" @click.stop>
                    <AppButton
                      @click="goToSessionEdit(session.uuid)"
                      title="Edit"
                      aria-label="Edit"
                    >
                      <Icon icon="mdi:edit-outline" />
                    </AppButton>

                    <div class="dropdown-divider"></div>

                    <AppButton
                      class="btn-delete"
                      @click="openDeleteSessionDialog(session.uuid)"
                      title="Delete"
                      aria-label="Delete"
                    >
                      <Icon icon="mdi:delete-outline" />
                    </AppButton>
                  </div>
                </div>
              </template>
            </AppListCard>
          </AppAsyncList>
        </div>
      </div>
    </main>
  </div>

  <AppModal :is-open="isCreateSessionDialogOpen" @close="closeCreateSessionDialog">
    <template v-slot:header>
      <h1 class="modal-header-title">Create session</h1>
    </template>

    <template v-slot:body>
      <AppInput
        id="session-title"
        type="text"
        label="Title"
        placeholder="Title"
        v-model="createSessionForm.title"
        :minlength="MIN_TITLE_LENGTH"
        :maxLength="MAX_TITLE_LENGTH"
        :has-error="!!createSessionForm.title && !isTitleValid"
        :error-message="`Minimum ${MIN_TITLE_LENGTH} characters`"
        required
      >
        <template v-slot:icon>
          <Icon icon="mdi:format-align-left" />
        </template>
      </AppInput>

      <AppTextarea
        id="session-description"
        label="Description"
        placeholder="Description"
        v-model="createSessionForm.description"
        :maxLength="MAX_DESCRIPTION_LENGTH"
      />

      <AppDurationInput
        id="session-time"
        label="Time"
        v-model="createSessionForm.time_seconds"
        :has-error="createSessionForm.time_seconds !== null && !isTimeSecondsValid"
        error-message="Invalid duration limits"
      >
        <template v-slot:icon>
          <Icon icon="mdi:timer-outline" />
        </template>
      </AppDurationInput>

      <AppInput
        id="quiz-uuid"
        type="text"
        label="Quiz UUID"
        placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
        v-model="createSessionForm.quiz_uuid"
        :minlength="QUIZ_UUID_LENGTH"
        :maxLength="QUIZ_UUID_LENGTH"
        :has-error="!!createSessionForm.quiz_uuid && !isQuizUuidValid"
        error-message="Invalid UUID format"
        required
      >
        <template v-slot:icon>
          <Icon icon="mdi:identifier" />
        </template>
      </AppInput>
    </template>

    <template v-slot:footer>
      <AppButton @click="closeCreateSessionDialog" title="Cancel" aria-label="Cancel"
        >Cancel</AppButton
      >
      <AppButton
        @click="handleCreateSession"
        :disabled="!isFormValid || roomsStore.isLoading"
        title="Create"
        aria-label="Create"
      >
        {{ roomsStore.isLoading ? 'Processing' : 'Create' }}
      </AppButton>
    </template>
  </AppModal>

  <AppModal :is-open="isDeleteRoomDialogOpen" @close="closeDeleteRoomDialog">
    <template v-slot:header>
      <h1 class="modal-header-title">Delete room</h1>
    </template>

    <template v-slot:body>
      <p class="modal-text">Are you sure you want to delete this room?</p>
      <p class="modal-text">This action cannot be undone</p>
    </template>

    <template v-slot:footer>
      <AppButton @click="closeDeleteRoomDialog" title="Cancel" aria-label="Cancel"
        >Cancel</AppButton
      >
      <AppButton
        class="btn-delete"
        @click="confirmDeleteRoom"
        :disabled="roomsStore.isLoading"
        title="Delete"
        aria-label="Delete"
      >
        {{ roomsStore.isLoading ? 'Processing' : 'Delete' }}
      </AppButton>
    </template>
  </AppModal>

  <AppModal :is-open="isDeleteSessionDialogOpen" @close="closeDeleteSessionDialog">
    <template v-slot:header>
      <h1 class="modal-header-title">Delete session</h1>
    </template>

    <template v-slot:body>
      <p class="modal-text">Are you sure you want to delete this session?</p>
      <p class="modal-text">This action cannot be undone</p>
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
.hero-title {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0;
  word-break: break-all;
  overflow-wrap: anywhere;
  min-width: 0;
  max-width: 100%;
}
.badge-waiting {
  background-color: color-mix(in srgb, var(--color-primary) 15%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-primary) 30%, transparent);
  color: var(--color-primary);
}
.badge-active {
  position: relative;
  z-index: 0;
  border-color: transparent;
  background: var(--linear-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.badge-active::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(
    50deg,
    color-mix(in srgb, var(--color-primary) 15%, transparent),
    color-mix(in srgb, var(--color-secondary) 15%, transparent)
  );
  z-index: -1;
  pointer-events: none;
}
.badge-active::after {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: inherit;
  padding: 1px;
  background: var(--linear-gradient-primary);
  opacity: 0.5;
  -webkit-mask:
    linear-gradient(#fff 0 0) content-box,
    linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  z-index: -1;
  pointer-events: none;
}
.badge-completed {
  background-color: color-mix(in srgb, var(--color-secondary) 15%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-secondary) 30%, transparent);
  color: var(--color-secondary);
}
.hero-description {
  margin: 0;
  font-size: 1rem;
  color: var(--color-text-secondary);
  line-height: 1.5;
  word-wrap: break-word;
  overflow-wrap: anywhere;
}
.hero-bottom {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin-top: 0.5rem;
  flex-wrap: wrap;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.item-id {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-family: monospace;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  background-color: var(--color-background-secondary);
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition:
    color 0.2s,
    background-color 0.2s;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}
.item-id:hover {
  color: var(--color-text);
}
.copy-icon {
  font-size: 0.9rem;
}

.main-nav {
  padding-right: 1rem;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-shrink: 0;
}
.main-nav-tab {
  display: flex;
  padding: 0.25rem;
  border-radius: 9px;
  border: 1px solid var(--color-border);
}
.tab-btn {
  border: none;
  background: transparent;
  padding: 0.5rem 1rem;
  color: var(--color-border);
}
.tab-btn:hover {
  border: none;
  box-shadow: none;
}
.tab-btn.active {
  cursor: default;
  pointer-events: none;
}
.tab-btn.active,
.tab-btn:hover {
  background: var(--linear-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sessions-list-wrapper {
  height: 500px;
  display: flex;
  flex-direction: column;
  border-radius: 12px;
  padding-left: 0.5rem;
}

.info-top {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  max-width: 100%;
}
.item-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  word-break: break-all;
  overflow-wrap: anywhere;
  hyphens: auto;
  min-width: 0;
  max-width: 100%;
}

.item-id {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-family: monospace;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  background-color: var(--color-background-secondary);
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: color 0.2s;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}
.item-id:hover {
  color: var(--color-text);
}
.copy-icon {
  font-size: 0.9rem;
}
.item-description {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
.info-bottom {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin-top: 0.5rem;
  flex-wrap: wrap;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.context-menu-wrapper {
  position: relative;
  display: inline-block;
}
.dropdown-menu {
  background: var(--color-background);
  border-radius: 9px;
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 0.5rem;
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: dropdownFadeIn 0.15s ease-out;
  gap: 0.15rem;
}
@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-5px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.dropdown-divider {
  height: 1px;
  width: 100%;
  margin: 0.1rem 0;
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

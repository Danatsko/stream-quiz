<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Icon } from '@iconify/vue'
import AppErrorMessage from '@/components/AppErrorMessage.vue'
import useAuthStore from '@/stores/auth'
import useRoomsStore from '@/stores/rooms'
import { useRouter } from 'vue-router'
import AppModal from '@/components/AppModal.vue'
import AppAsyncList from '@/components/AppAsyncList.vue'
import AppListCard from '@/components/AppListCard.vue'
import { formatDateTime } from '@/utils/formatters'

interface CreateRoomFormState {
  title: string
  description: string
}

const MIN_TITLE_LENGTH = 3
const MAX_TITLE_LENGTH = 100
const MAX_DESCRIPTION_LENGTH = 500

const authStore = useAuthStore()
const roomsStore = useRoomsStore()
const router = useRouter()

const activeMenuUuid = ref<string | null>(null)
const roomToDeleteUuid = ref<string | null>(null)
const isCreateRoomDialogOpen = ref(false)
const isDeleteRoomDialogOpen = ref(false)
const createRoomForm = ref<CreateRoomFormState>({
  title: '',
  description: '',
})

const currentUserUuid = computed((): string | null => {
  return authStore.user === null ? null : authStore.user.uuid
})

const copyToClipboard = (text: string): void => {
  navigator.clipboard.writeText(text)
}

const goToRoom = async (uuid: string): Promise<void> => {
  await router.push({
    name: 'Room',
    params: {
      uuid: uuid,
    },
  })
}

const goToEdit = async (uuid: string): Promise<void> => {
  activeMenuUuid.value = null

  await router.push({
    name: 'RoomEdit',
    params: {
      uuid: uuid,
    },
  })
}

const openCreateRoomDialog = (): void => {
  isCreateRoomDialogOpen.value = true
  createRoomForm.value.title = ''
  createRoomForm.value.description = ''
}

const closeCreateRoomDialog = (): void => {
  isCreateRoomDialogOpen.value = false
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
  await roomsStore.getRooms()
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeDropdowns)
  roomsStore.clearRooms()
})

const isTitleValid = computed((): boolean => {
  const { title } = createRoomForm.value

  return !!title && title.length >= MIN_TITLE_LENGTH && title.length <= MAX_TITLE_LENGTH
})

const isDescriptionValid = computed((): boolean => {
  const { description } = createRoomForm.value

  return !description || description.length <= MAX_DESCRIPTION_LENGTH
})

const isFormValid = computed((): boolean => {
  return isTitleValid.value && isDescriptionValid.value
})

const handleCreateRoom = async (): Promise<void> => {
  if (!isFormValid.value) {
    return
  }

  try {
    const uuid = await roomsStore.createRoom({
      title: createRoomForm.value.title,
      description: createRoomForm.value.description,
    })

    closeCreateRoomDialog()
    await goToRoom(uuid)
  } catch (error) {}
}

const openDeleteRoomDialog = (uuid: string): void => {
  activeMenuUuid.value = null
  roomToDeleteUuid.value = uuid
  isDeleteRoomDialogOpen.value = true
}

const closeDeleteRoomDialog = (): void => {
  isDeleteRoomDialogOpen.value = false
  roomToDeleteUuid.value = null
}

const confirmDeleteRoom = async (): Promise<void> => {
  if (!roomToDeleteUuid.value) {
    return
  }

  try {
    await roomsStore.deleteRoom(roomToDeleteUuid.value)
    closeDeleteRoomDialog()
  } catch (error) {}
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <AppButton @click="openCreateRoomDialog">Create room</AppButton>
      </div>
    </header>

    <main class="main">
      <AppAsyncList
        :items="roomsStore.rooms"
        :is-loading="roomsStore.isLoading"
        empty-icon="mdi:cube-outline"
        empty-title="There are no rooms"
        empty-text=" "
        @load-more="roomsStore.getRooms"
      >
        <AppListCard v-for="room in roomsStore.rooms" :key="room.uuid">
          <template v-slot:icon>
            <Icon icon="mdi:cube-outline" />
          </template>

          <template v-slot:content>
            <div class="info-top">
              <h3 class="room-title">{{ room.title }}</h3>
            </div>
            <p class="room-description">{{ room.description }}</p>
            <div class="info-bottom">
              <span class="meta-item" v-if="room.created_at">
                <Icon icon="mdi:calendar-plus" />
                {{ formatDateTime(room.created_at) }}
              </span>

              <span class="meta-item" v-if="room.updated_at">
                <Icon icon="mdi:calendar-edit" />
                {{ formatDateTime(room.updated_at) }}
              </span>

              <div class="room-id" @click="copyToClipboard(room.uuid)">
                {{ room.uuid }}
                <Icon icon="mdi:content-copy" class="copy-icon" />
              </div>
            </div>
          </template>

          <template v-slot:actions>
            <AppButton @click="goToRoom(room.uuid)">View</AppButton>

            <div class="context-menu-wrapper">
              <AppButton @click.stop="toggleMenu(room.uuid)">
                <Icon icon="mdi:dots-vertical" />
              </AppButton>

              <div class="dropdown-menu" v-if="activeMenuUuid === room.uuid" @click.stop>
                <AppButton @click="goToEdit(room.uuid)">
                  <span>Edit</span>
                </AppButton>

                <div class="dropdown-divider"></div>

                <AppButton class="btn-delete" @click="openDeleteRoomDialog(room.uuid)">
                  <span>Delete</span>
                </AppButton>
              </div>
            </div>
          </template>
        </AppListCard>
      </AppAsyncList>
    </main>
  </div>

  <AppModal :is-open="isCreateRoomDialogOpen" @close="closeCreateRoomDialog">
    <template v-slot:header>
      <h1 class="modal-header-title">Create room</h1>
    </template>

    <template v-slot:body>
      <div class="form-group">
        <label for="room-title">Title</label>
        <input
          class="modal-input"
          :class="{ 'input-error': createRoomForm.title && !isTitleValid }"
          id="room-title"
          type="text"
          placeholder="Title"
          v-model="createRoomForm.title"
          :minlength="MIN_TITLE_LENGTH"
          :maxLength="MAX_TITLE_LENGTH"
          required
        />
        <AppErrorMessage v-if="createRoomForm.title && !isTitleValid">
          Minimum {{ MIN_TITLE_LENGTH }} characters
        </AppErrorMessage>
      </div>

      <div class="form-group">
        <label for="room-description">Description</label>
        <textarea
          class="modal-input textarea"
          id="room-description"
          placeholder="Description"
          v-model="createRoomForm.description"
          :maxLength="MAX_DESCRIPTION_LENGTH"
          rows="5"
        ></textarea>
      </div>
    </template>

    <template v-slot:footer>
      <AppButton @click="closeCreateRoomDialog">Cancel</AppButton>
      <AppButton @click="handleCreateRoom" :disabled="!isFormValid || roomsStore.isLoading">
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
      <p class="modal-text">This action cannot be undone.</p>
    </template>

    <template v-slot:footer>
      <AppButton @click="closeDeleteRoomDialog">Cancel</AppButton>
      <AppButton class="btn-delete" @click="confirmDeleteRoom" :disabled="roomsStore.isLoading">
        {{ roomsStore.isLoading ? 'Processing' : 'Delete' }}
      </AppButton>
    </template>
  </AppModal>
</template>

<style scoped>
.layout {
  height: 100%;
  width: 90vw;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
  padding-bottom: 1rem;
}

.header {
  padding: 1.5rem 0;
  padding-right: 1rem;
  font-weight: bold;
  flex-shrink: 0;
}
.header-content {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.info-top {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  max-width: 100%;
}
.room-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  word-break: break-all;
  overflow-wrap: anywhere;
  hyphens: auto;
  min-width: 0;
  max-width: 100%;
}
.room-id {
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
.room-id:hover {
  color: var(--color-text);
}
.copy-icon {
  font-size: 0.9rem;
}
.room-description {
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
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 0.5rem;
  min-width: 100px;
  z-index: 50;
  display: flex;
  flex-direction: column;
  animation: dropdownFadeIn 0.15s ease-out;
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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.modal-input {
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
.modal-input:focus {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 10px 1px var(--color-secondary);
}
.modal-input.textarea {
  resize: unset;
  font-family: inherit;
}
.input-error {
  border-color: red;
}
.modal-input.textarea::-webkit-scrollbar {
  width: 8px;
  cursor: pointer;
}
.modal-input.textarea::-webkit-scrollbar-track {
  background: transparent;
  cursor: pointer;
}
.modal-input.textarea::-webkit-scrollbar-thumb {
  background-color: var(--color-border);
  border-radius: 10px;
  cursor: pointer;
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
    0 0 1px 3px color-mix(in srgb, red 50%, transparent);
}
</style>

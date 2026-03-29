<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { Icon } from '@iconify/vue'
import AppErrorMessage from '@/components/AppErrorMessage.vue'
import useAuthStore from '@/stores/auth'
import useRoomsStore from '@/stores/rooms'
import { useRoute, useRouter } from 'vue-router'
import AppModal from '@/components/AppModal.vue'
import AppListCard from '@/components/AppListCard.vue'

interface EditRoom {
  title: string
  description: string
}

const MIN_TITLE_LENGTH = 3
const MAX_TITLE_LENGTH = 100
const MAX_DESCRIPTION_LENGTH = 500

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const roomsStore = useRoomsStore()

const isDeleteRoomDialogOpen = ref(false)
const roomUuid = computed(() => route.params.uuid as string)
const room = computed(() => roomsStore.room)
const isLoading = computed(() => roomsStore.isLoading)
const isSaving = ref(false)

const currentUserUuid = computed((): string | null => {
  return authStore.user === null ? null : authStore.user.uuid
})

const editableRoom = ref<EditRoom | null>(null)

const initEditableRoom = (): void => {
  if (!room.value) {
    return
  }

  editableRoom.value = {
    title: room.value.title,
    description: room.value.description,
  }
}

watch(room, initEditableRoom)

const goBack = async (): Promise<void> => {
  await router.push({
    name: 'Room',
    params: {
      uuid: roomUuid.value,
    },
  })
}

onMounted(async () => {
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
    } catch (onMountedError) {
      await router.push({ name: 'Rooms' })
    }
  }
})

onBeforeUnmount(() => {
  roomsStore.clearRoom()
})

const isTitleValid = computed((): boolean => {
  if (!editableRoom.value) {
    return false
  }

  const { title } = editableRoom.value

  return !!title && title.length >= MIN_TITLE_LENGTH && title.length <= MAX_TITLE_LENGTH
})

const isDescriptionValid = computed((): boolean => {
  if (!editableRoom.value) {
    return false
  }

  const { description } = editableRoom.value

  return !description || description.length <= MAX_DESCRIPTION_LENGTH
})

const isFormValid = computed((): boolean => {
  if (!editableRoom.value) {
    return false
  }

  return isTitleValid.value && isDescriptionValid.value
})

const hasChanges = computed((): boolean => {
  if (!editableRoom.value || !room.value) {
    return false
  }

  const normalizeData = (data: any) => ({
    title: data.title,
    description: data.description,
  })

  const originalStr = JSON.stringify(normalizeData(room.value))
  const editedStr = JSON.stringify(normalizeData(editableRoom.value))

  return originalStr !== editedStr
})

const saveChanges = async (): Promise<void> => {
  if (!editableRoom.value || !room.value || !isFormValid.value || !hasChanges.value) {
    return
  }

  try {
    isSaving.value = true

    const payload = {
      title: editableRoom.value.title,
      description: editableRoom.value.description,
    }

    await roomsStore.updateRoom(roomUuid.value, payload)
    await goBack()
  } catch (error) {
  } finally {
    isSaving.value = false
  }
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
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content" :style="{ justifyContent: 'space-between' }">
        <AppButton @click="goBack">
          <span>Cancel</span>
        </AppButton>

        <div class="header-actions">
          <AppButton
            @click="saveChanges"
            :disabled="isSaving || !isFormValid || isLoading || !hasChanges"
          >
            {{ isSaving ? 'Processing' : 'Save' }}
          </AppButton>
          <AppButton class="btn-delete" @click="openDeleteRoomDialog">Delete</AppButton>
        </div>
      </div>
    </header>

    <main class="main" v-if="isLoading && !editableRoom">
      <div class="empty-state">
        <Icon icon="mdi:loading" class="spin-icon empty-icon" />
        <p class="empty-text">Loading</p>
      </div>
    </main>

    <main class="main" v-else-if="editableRoom">
      <div class="room-content-wrapper">
        <AppListCard>
          <template v-slot:icon>
            <Icon icon="mdi:cube-outline" />
          </template>

          <template v-slot:content>
            <div class="hero-top">
              <div class="form-group flex-1">
                <label for="room-title">Title</label>
                <input
                  id="room-title"
                  class="edit-input"
                  :class="{ 'input-error': editableRoom.title && !isTitleValid }"
                  type="text"
                  placeholder="Title"
                  v-model="editableRoom.title"
                  :minlength="MIN_TITLE_LENGTH"
                  :maxLength="MAX_TITLE_LENGTH"
                />
                <AppErrorMessage v-if="editableRoom.title && !isTitleValid">
                  Minimum {{ MIN_TITLE_LENGTH }} characters
                </AppErrorMessage>
              </div>
            </div>

            <div class="form-group">
              <label for="room-description">Description</label>
              <textarea
                id="room-description"
                class="edit-input textarea"
                placeholder="Description"
                v-model="editableRoom.description"
                :maxLength="MAX_DESCRIPTION_LENGTH"
                rows="5"
              ></textarea>
            </div>
          </template>
        </AppListCard>
      </div>
    </main>
  </div>

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

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.flex-1 {
  flex: 1;
}
.edit-input {
  width: 100%;
  padding: 0.75rem 1rem;
  box-sizing: border-box;
  background-color: transparent;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--color-text);
  outline: none;
  font-family: inherit;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}
.edit-input:focus {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 10px 1px var(--color-secondary);
}

.edit-input.textarea {
  resize: unset;
  font-family: inherit;
}
.edit-input.textarea::-webkit-scrollbar {
  width: 8px;
  cursor: pointer;
}
.edit-input.textarea::-webkit-scrollbar-track {
  background: transparent;
  cursor: pointer;
}
.edit-input.textarea::-webkit-scrollbar-thumb {
  background-color: var(--color-border);
  border-radius: 10px;
  cursor: pointer;
}

.input-error {
  border-color: red;
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

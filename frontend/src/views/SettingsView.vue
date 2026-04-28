<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth'
import AppButton from '@/components/AppButton.vue'
import AppListCard from '@/components/AppListCard.vue'
import AppInput from '@/components/AppInput.vue'
import AppModal from '@/components/AppModal.vue'

const MIN_USERNAME_LENGTH = 3
const MAX_USERNAME_LENGTH = 30

const authStore = useAuthStore()
const router = useRouter()

const user = computed(() => authStore.user)

const editableUsername = ref('')
const isUpdatingUsername = ref(false)
const isDeleteModalOpen = ref(false)
const isDeleting = ref(false)

const initEditableUsername = (): void => {
  if (user.value) {
    editableUsername.value = user.value.username
  }
}

watch(user, initEditableUsername, { immediate: true })

const isUsernameValid = computed((): boolean => {
  const username = editableUsername.value

  return (
    !!username && username.length >= MIN_USERNAME_LENGTH && username.length <= MAX_USERNAME_LENGTH
  )
})

const hasUsernameChanges = computed((): boolean => {
  return user.value?.username !== editableUsername.value
})

const handleUpdateUsername = async (): Promise<void> => {
  if (!hasUsernameChanges.value || !isUsernameValid.value) {
    return
  }

  try {
    isUpdatingUsername.value = true

    await authStore.updateMe({ username: editableUsername.value })
  } catch (error) {
  } finally {
    isUpdatingUsername.value = false
  }
}

const handleLogout = async (): Promise<void> => {
  try {
    await authStore.logout()
    await router.push({ name: 'Home' })
  } catch (error) {}
}

const openDeleteModal = (): void => {
  isDeleteModalOpen.value = true
}

const closeDeleteModal = (): void => {
  isDeleteModalOpen.value = false
}

const confirmDeleteAccount = async (): Promise<void> => {
  try {
    isDeleting.value = true

    await authStore.deleteMe()
    closeDeleteModal()
    await router.push({ name: 'Home' })
  } catch (error) {
  } finally {
    isDeleting.value = false
  }
}

const copyToClipboard = (text: string): void => {
  navigator.clipboard.writeText(text)
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <div class="header-actions">
          <AppButton
            class="btn-logout"
            @click="handleLogout"
            :disabled="authStore.isLoading"
            title="Logout"
            aria-label="Logout"
          >
            <span v-if="authStore.isLoading">Processing</span>
            <Icon v-else icon="mdi:logout" />
          </AppButton>
        </div>
      </div>
    </header>

    <main class="main" v-if="user">
      <div class="settings-content-wrapper">
        <AppListCard>
          <template v-slot:icon>
            <Icon icon="mdi:account-circle-outline" />
          </template>

          <template v-slot:content>
            <div class="info-top">
              <h3 class="item-title">Account information</h3>
            </div>

            <div class="info-bottom">
              <div class="username-update-wrapper">
                <AppInput
                  id="username"
                  type="text"
                  label="Username"
                  placeholder="Username"
                  v-model="editableUsername"
                  :minlength="MIN_USERNAME_LENGTH"
                  :maxLength="MAX_USERNAME_LENGTH"
                  :has-error="!!editableUsername && !isUsernameValid"
                  :error-message="`Minimum ${MIN_USERNAME_LENGTH} characters`"
                >
                  <template v-slot:icon>
                    <Icon icon="mdi:account-outline" />
                  </template>
                </AppInput>

                <AppButton
                  class="btn-save-username"
                  @click="handleUpdateUsername"
                  :disabled="!hasUsernameChanges || !isUsernameValid || isUpdatingUsername"
                  title="Save username"
                  aria-label="Save username"
                >
                  <span v-if="isUpdatingUsername">Saving</span>
                  <Icon v-else icon="mdi:content-save-outline" />
                </AppButton>
              </div>

              <span class="meta-item">
                <Icon icon="mdi:email-outline" />
                <span class="meta-value">{{ user.email }}</span>
              </span>

              <div class="meta-item" v-if="user.uuid">
                <Icon icon="mdi:identifier" />
                <div class="item-id" @click="copyToClipboard(user.uuid)" title="Copy uuid">
                  {{ user.uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>
            </div>
          </template>
        </AppListCard>

        <AppListCard class="danger-card">
          <template v-slot:icon>
            <Icon icon="mdi:alert-outline" class="danger-icon" />
          </template>

          <template v-slot:content>
            <div class="info-top">
              <h3 class="item-title">Danger zone</h3>
            </div>

            <div class="info-bottom">
              <span class="meta-value"> Deleting your account is permanent </span>
              <AppButton
                class="btn-delete"
                @click="openDeleteModal"
                title="Delete account"
                aria-label="Delete account"
              >
                Delete account
              </AppButton>
            </div>
          </template>
        </AppListCard>
      </div>
    </main>
  </div>

  <AppModal :is-open="isDeleteModalOpen" @close="closeDeleteModal">
    <template v-slot:header>
      <h1 class="modal-header-title">Delete account</h1>
    </template>

    <template v-slot:body>
      <p class="modal-text">Are you sure you want to delete your account?</p>
      <p class="modal-text">This action cannot be undone.</p>
    </template>

    <template v-slot:footer>
      <AppButton
        @click="closeDeleteModal"
        title="Cancel"
        aria-label="Cancel"
        :disabled="isDeleting"
      >
        Cancel
      </AppButton>
      <AppButton
        class="btn-delete"
        @click="confirmDeleteAccount"
        :disabled="isDeleting"
        title="Delete"
        aria-label="Delete"
      >
        {{ isDeleting ? 'Processing' : 'Delete' }}
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
.settings-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 0.25rem 1rem 0.25rem 0.5rem;
}

.info-top {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  max-width: 100%;
  margin-bottom: 0.5rem;
}
.item-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  word-break: break-all;
  overflow-wrap: anywhere;
}

.info-bottom {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.username-update-wrapper {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  gap: 1rem;
  width: 100%;
  max-width: 400px;
}

.btn-save-username {
  margin-top: 1.65rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.meta-value {
  color: var(--color-text-secondary);
  word-break: break-all;
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

.danger-card {
  transition: border-color 0.2s;
}

.danger-card:hover {
  border-color: red !important;
  box-shadow:
    0 0 1px 1px red,
    0 0 1px 3px color-mix(in srgb, red 50%, transparent) !important;
}

.danger-icon {
  color: red;
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

.btn-logout,
.btn-delete {
  color: red;
  border-color: red;
  background-color: color-mix(in srgb, red 10%, black);
}
.btn-logout:hover,
.btn-delete:hover {
  background-color: color-mix(in srgb, red 20%, black);
  border-color: red;
  box-shadow:
    0 0 1px 1px red,
    0 0 1px 3px color-mix(in srgb, red 50%, transparent);
}
</style>

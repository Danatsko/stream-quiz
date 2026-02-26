<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Icon } from '@iconify/vue'
import AppErrorMessage from '@/components/AppErrorMessage.vue'
import useAuthStore from '@/stores/auth'
import useQuizzesStore from '@/stores/quizzes'
import { useInfiniteScroll } from '@vueuse/core'

interface CreateQuizFormState {
  title: string
  description: string
}

const MIN_TITLE_LENGTH = 3
const MAX_TITLE_LENGTH = 100
const MIN_DESCRIPTION_LENGTH = 3
const MAX_DESCRIPTION_LENGTH = 500

const authStore = useAuthStore()
const quizzesStore = useQuizzesStore()

const activeTab = ref('All')
const activeMenuUuid = ref<string | null>(null)
const quizToDeleteUuid = ref<string | null>(null)
const quizzesListRef = ref<HTMLElement | null>(null)
const isCreateQuizDialogOpen = ref(false)
const isDeleteQuizDialogOpen = ref(false)
const createQuizForm = ref<CreateQuizFormState>({
  title: '',
  description: '',
})

useInfiniteScroll(
  quizzesListRef,
  async () => {
    if (!quizzesStore.isLoading) {
      await quizzesStore.getQuizzes()
    }
  },
  {
    distance: 50,
  },
)

const currentUserUuid = computed((): string | null => {
  return authStore.user === null ? null : authStore.user.uuid
})

const tabs = [
  { label: 'All', name: 'All' },
  { label: 'Owned', name: 'Owned' },
  { label: 'Not owned', name: 'Not owned' },
]

const filteredQuizzes = computed(() => {
  if (activeTab.value === 'Owned') {
    return quizzesStore.quizzes.filter((quiz) => quiz.creator_uuid === currentUserUuid.value)
  }
  if (activeTab.value === 'Not owned') {
    return quizzesStore.quizzes.filter((quiz) => quiz.creator_uuid !== currentUserUuid.value)
  }

  return quizzesStore.quizzes
})

const copyToClipboard = (text: string): void => {
  navigator.clipboard.writeText(text)
}

const openCreateQuizDialog = (): void => {
  isCreateQuizDialogOpen.value = true
  createQuizForm.value.title = ''
  createQuizForm.value.description = ''
}

const closeCreateQuizDialog = (): void => {
  isCreateQuizDialogOpen.value = false
}

const toggleMenu = (uuid: string): void => {
  activeMenuUuid.value = activeMenuUuid.value === uuid ? null : uuid
}

const editQuiz = (uuid: string): void => {
  activeMenuUuid.value = null
}

const closeDropdowns = (): void => {
  if (activeMenuUuid.value) {
    activeMenuUuid.value = null
  }
}

onMounted(async () => {
  document.addEventListener('click', closeDropdowns)
  await quizzesStore.getQuizzes()
})

onBeforeUnmount(() => {
  document.removeEventListener('click', closeDropdowns)
  quizzesStore.clearQuizzes()
})

const isTitleValid = computed((): boolean => {
  const { title } = createQuizForm.value

  return !!title && title.length >= MIN_TITLE_LENGTH
})

const isDescriptionValid = computed((): boolean => {
  const { description } = createQuizForm.value

  return !!description && description.length >= MIN_DESCRIPTION_LENGTH
})

const isFormValid = computed((): boolean => {
  const f = createQuizForm.value
  const isNotEmpty = !!f.title && !!f.description

  return isNotEmpty && isTitleValid.value && isDescriptionValid.value
})

const handleCreateQuiz = async (): Promise<void> => {
  if (!isFormValid.value) {
    return
  }

  try {
    await quizzesStore.createQuiz({
      title: createQuizForm.value.title,
      description: createQuizForm.value.description,
    })

    closeCreateQuizDialog()
  } catch (error) {}
}

const openDeleteQuizDialog = (uuid: string): void => {
  activeMenuUuid.value = null
  quizToDeleteUuid.value = uuid
  isDeleteQuizDialogOpen.value = true
}

const closeDeleteQuizDialog = (): void => {
  isDeleteQuizDialogOpen.value = false
  quizToDeleteUuid.value = null
}

const confirmDeleteQuiz = async (): Promise<void> => {
  if (!quizToDeleteUuid.value) {
    return
  }

  try {
    await quizzesStore.deleteQuiz(quizToDeleteUuid.value)
  } catch (error) {}

  closeDeleteQuizDialog()
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <AppButton class="btn-create-quiz" @click="openCreateQuizDialog">Create quiz</AppButton>
      </div>
    </header>

    <main class="main">
      <div class="main-nav">
        <div class="main-nav-tab">
          <button
            v-for="tab in tabs"
            :key="tab.name"
            class="main-nav-tab-btn"
            :class="{ active: activeTab === tab.name }"
            @click="activeTab = tab.name"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>

      <div class="main-quizzes-list" ref="quizzesListRef">
        <div v-if="quizzesStore.isLoading && quizzesStore.quizzes.length === 0" class="empty-state">
          <Icon icon="mdi:loading" class="spin-icon empty-icon" />
          <p class="empty-text">Loading</p>
        </div>

        <div
          v-else-if="!quizzesStore.isLoading && filteredQuizzes.length === 0"
          class="empty-state"
        >
          <Icon icon="mdi:book-open-variant-outline" class="empty-icon" />
          <h1 class="empty-title">There are no quizzes</h1>
          <p class="empty-text">No quiz found for the selected category</p>
        </div>

        <template v-else>
          <div class="quiz-card" v-for="quiz in filteredQuizzes" :key="quiz.uuid">
            <div class="card-icon-wrapper">
              <Icon icon="mdi:book-open-variant-outline" class="card-icon" />
            </div>

            <div class="card-info">
              <div class="info-top-row">
                <h3 class="quiz-title">{{ quiz.title }}</h3>

                <span :class="['badge', quiz.is_public ? 'public' : 'private']">
                  {{ quiz.is_public ? 'Public' : 'Private' }}
                </span>
              </div>

              <p class="quiz-description">{{ quiz.description }}</p>

              <div class="info-bottom-row">
                <span class="meta-item">
                  <Icon icon="mdi:help-circle-outline" />
                  {{ quiz.total_questions }} questions
                </span>
                <div class="quiz-id" @click="copyToClipboard(quiz.uuid)" title="Copy uuid">
                  {{ quiz.uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>
            </div>

            <div class="card-actions">
              <button class="btn-view">View</button>
              <div class="context-menu-wrapper" v-if="quiz.creator_uuid === currentUserUuid">
                <button class="btn-icon" @click.stop="toggleMenu(quiz.uuid)">
                  <Icon icon="mdi:dots-vertical" />
                </button>

                <div class="dropdown-menu" v-if="activeMenuUuid === quiz.uuid" @click.stop>
                  <button class="dropdown-item" @click="editQuiz(quiz.uuid)">
                    <span>Edit</span>
                  </button>
                  <div class="dropdown-divider"></div>
                  <button class="dropdown-item delete" @click="openDeleteQuizDialog(quiz.uuid)">
                    <span>Delete</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-if="quizzesStore.isLoading" class="loading-indicator">
            <Icon icon="mdi:loading" class="spin-icon" /> Loading
          </div>
        </template>
      </div>
    </main>
  </div>

  <Teleport to="body">
    <div v-if="isCreateQuizDialogOpen" class="modal-overlay">
      <div class="modal-window">
        <div class="modal-header">
          <h1 class="modal-header-title">Create quiz</h1>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label for="quiz-title">Title</label>
            <input
              class="modal-input"
              :class="{ 'input-error': createQuizForm.title && !isTitleValid }"
              id="quiz-title"
              type="text"
              placeholder="Title"
              v-model="createQuizForm.title"
              :minlength="MIN_TITLE_LENGTH"
              :maxLength="MAX_TITLE_LENGTH"
              required
            />
            <AppErrorMessage v-if="createQuizForm.title && !isTitleValid">
              Minimum {{ MIN_TITLE_LENGTH }} characters
            </AppErrorMessage>
          </div>

          <div class="form-group">
            <label for="quiz-description">Description</label>
            <textarea
              class="modal-input textarea"
              :class="{ 'input-error': createQuizForm.description && !isDescriptionValid }"
              id="quiz-description"
              placeholder="Description"
              v-model="createQuizForm.description"
              :minlength="MIN_DESCRIPTION_LENGTH"
              :maxLength="MAX_DESCRIPTION_LENGTH"
              rows="5"
              required
            ></textarea>
            <AppErrorMessage v-if="createQuizForm.description && !isDescriptionValid">
              Minimum {{ MIN_DESCRIPTION_LENGTH }} characters
            </AppErrorMessage>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="closeCreateQuizDialog">Cancel</button>
          <AppButton
            class="btn-submit"
            @click="handleCreateQuiz"
            :disabled="!isFormValid || quizzesStore.isLoading"
          >
            {{ quizzesStore.isLoading ? 'Processing' : 'Create' }}
          </AppButton>
        </div>
      </div>
    </div>
  </Teleport>

  <Teleport to="body">
    <div v-if="isDeleteQuizDialogOpen" class="modal-overlay">
      <div class="modal-window">
        <div class="modal-header">
          <h1 class="modal-header-title">Delete quiz</h1>
        </div>

        <div class="modal-body">
          <p class="modal-text">Are you sure you want to delete this quiz?</p>
          <p class="modal-text">This action cannot be undone.</p>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="closeDeleteQuizDialog">Cancel</button>
          <AppButton
            class="btn-submit btn-delete"
            @click="confirmDeleteQuiz"
            :disabled="quizzesStore.isLoading"
          >
            {{ quizzesStore.isLoading ? 'Processing' : 'Delete' }}
          </AppButton>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.layout {
  height: 100%;
  width: 90vw;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.header {
  padding: 1.5rem 0;
  font-weight: bold;
  flex-shrink: 0;
}
.header-content {
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
.btn-create-quiz {
  background: var(--linear-gradient-primary);
  color: var(--color-text);
  margin: 0.3rem 0;
  align-self: center;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.main-nav {
  padding-bottom: 1rem;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  flex-shrink: 0;
}
.main-nav-tab {
  display: flex;
  padding: 0.25rem;
  border-radius: 8px;
  border: 1px solid #2a2a2a;
}
.main-nav-tab-btn {
  background: transparent;
  border: none;
  color: #2a2a2a;
  padding: 0.5rem 1rem;
  font-size: 1rem;
  font-weight: 500;
  border-radius: 6px;
}
.main-nav-tab-btn:hover {
  cursor: pointer;
}
.main-nav-tab-btn.active {
  cursor: default;
  pointer-events: none;
}
.main-nav-tab-btn.active,
.main-nav-tab-btn:hover {
  background: var(--linear-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 500;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  text-align: center;
  gap: 0.5rem;
  color: white;
}
.empty-icon {
  font-size: 4rem;
  color: white;
  margin-bottom: 1rem;
}
.empty-title {
  color: white;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}
.empty-text {
  margin: 0 0 1rem 0;
  font-size: 0.95rem;
}
.spin-icon {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
.main-quizzes-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  min-height: 0;
  gap: 0.75rem;
  padding: 0.25rem 0.5rem 0.25rem 0.5rem;
}
.quiz-card {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 1.2rem;
  transition: border-color 0.2s;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
}
.quiz-card:hover {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 1px 3px var(--color-secondary);
}
.card-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
}
.card-icon {
  font-size: 1.5rem;
  color: white;
}
.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.4rem;
  min-width: 0;
}
.info-top-row {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  max-width: 100%;
}
.quiz-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  color: white;
  word-break: break-all;
  overflow-wrap: anywhere;
  hyphens: auto;
  min-width: 0;
  max-width: 100%;
}
.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  white-space: nowrap;
  flex-shrink: 0;
}
.badge.public {
  background-color: color-mix(in srgb, var(--color-primary) 15%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-primary) 30%, transparent);
  color: var(--color-primary);
}
.badge.private {
  background-color: #121212;
  border: 1px solid color-mix(in srgb, #9ca3af 30%, transparent);
  color: #9ca3af;
}
.quiz-id {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-family: monospace;
  font-size: 0.8rem;
  color: #9ca3af;
  background-color: #121212;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: color 0.2s;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}
.quiz-id:hover {
  color: white;
}
.copy-icon {
  font-size: 0.9rem;
}
.quiz-description {
  margin: 0;
  font-size: 0.9rem;
  color: #9ca3af;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
.info-bottom-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.8rem;
  color: #9ca3af;
  margin-top: 0.2rem;
  flex-wrap: wrap;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  margin-left: auto;
}
.btn-view {
  background-color: transparent;
  color: white;
  border: 1px solid #2a2a2a;
  padding: 0.5rem 1.2rem;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-view:hover {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 1px 3px var(--color-secondary);
}
.btn-view:active {
  transform: scale(0.95);
}
.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
  color: white;
  border: 1px solid #2a2a2a;
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
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
  background-color: var(--color-background);
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  min-width: 100px;
  box-shadow:
    0 10px 15px -3px rgba(0, 0, 0, 0.5),
    0 4px 6px -2px rgba(0, 0, 0, 0.3);
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
.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  box-sizing: border-box;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: transparent;
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  width: 100%;
  text-align: center;
}
.dropdown-item:hover {
  border-color: var(--color-primary);
  border-radius: 6px;
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 1px 3px var(--color-secondary);
}
.dropdown-item:active {
  transform: scale(0.95);
}
.dropdown-divider {
  height: 1px;
  background-color: #2a2a2a;
  width: 100%;
  margin: 0.1rem 0;
}
.dropdown-item.delete {
  color: red;
}
.dropdown-item.delete:hover {
  background-color: rgba(255, 0, 0, 0.1);
}
.btn-icon:hover {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 1px 3px var(--color-secondary);
}
.btn-icon:active {
  transform: scale(0.95);
}
.main-quizzes-list::-webkit-scrollbar {
  width: 8px;
  cursor: pointer;
}
.main-quizzes-list::-webkit-scrollbar-track {
  background: transparent;
  cursor: pointer;
}
.main-quizzes-list::-webkit-scrollbar-thumb {
  background-color: #2a2a2a;
  border-radius: 10px;
  cursor: pointer;
}
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  color: white;
  font-size: 0.9rem;
  width: 100%;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
.modal-window {
  background-color: #121212;
  border: 1px solid #2a2a2a;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.5),
    0 10px 10px -5px rgba(0, 0, 0, 0.2);
  animation: modalFadeIn 0.2s ease-out;
}
@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.modal-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1.5rem;
}
.modal-header-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 900;
}
.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
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
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  font-size: 1rem;
  color: white;
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
  background-color: #2a2a2a;
  border-radius: 10px;
  cursor: pointer;
}
.modal-footer {
  padding: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  align-items: center;
}
.btn-submit {
  background: var(--linear-gradient-primary);
  color: var(--color-text);
  margin: 0.3rem 0;
  align-self: center;
}
.modal-text {
  color: white;
  font-size: 1rem;
  line-height: 1.5;
  margin: 0;
  text-align: center;
}
.btn-cancel {
  background: transparent;
  color: white;
  border: 1px solid #2a2a2a;
  padding: 0.5rem 1.2rem;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-cancel:hover {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 1px 3px var(--color-secondary);
}
.btn-cancel:active {
  transform: scale(0.95);
}
.btn-delete {
  background: red;
  color: white;
}
.btn-delete:hover {
  box-shadow:
    0 0 1px 1px red,
    0 0 5px 1px rgba(255, 0, 0, 0.5);
}
</style>

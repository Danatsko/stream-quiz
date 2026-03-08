<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { Icon } from '@iconify/vue'
import AppErrorMessage from '@/components/AppErrorMessage.vue'
import useAuthStore from '@/stores/auth'
import useQuizzesStore from '@/stores/quizzes'
import { useRouter } from 'vue-router'
import AppModal from '@/components/AppModal.vue'
import AppAsyncList from '@/components/AppAsyncList.vue'
import AppAsyncCard from '@/components/AppAsyncCard.vue'
import AppBadge from '@/components/AppBadge.vue'

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
const router = useRouter()

const activeTab = ref('All')
const activeMenuUuid = ref<string | null>(null)
const quizToDeleteUuid = ref<string | null>(null)
const isCreateQuizDialogOpen = ref(false)
const isDeleteQuizDialogOpen = ref(false)
const createQuizForm = ref<CreateQuizFormState>({
  title: '',
  description: '',
})

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

const goToQuiz = async (uuid: string): Promise<void> => {
  await router.push({
    name: 'Quiz',
    params: {
      uuid: uuid,
    },
  })
}

const goToEdit = async (uuid: string): Promise<void> => {
  activeMenuUuid.value = null

  await router.push({
    name: 'EditQuiz',
    params: {
      uuid: uuid,
    },
  })
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
    const uuid = await quizzesStore.createQuiz({
      title: createQuizForm.value.title,
      description: createQuizForm.value.description,
    })

    closeCreateQuizDialog()
    await goToQuiz(uuid)
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
    closeDeleteQuizDialog()
  } catch (error) {}
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <AppButton @click="openCreateQuizDialog">Create quiz</AppButton>
      </div>
    </header>

    <main class="main">
      <div class="main-nav">
        <div class="main-nav-tab">
          <AppButton
            v-for="tab in tabs"
            :key="tab.name"
            class="tab-btn"
            :class="{ active: activeTab === tab.name }"
            @click="activeTab = tab.name"
          >
            {{ tab.label }}
          </AppButton>
        </div>
      </div>

      <AppAsyncList
        :items="filteredQuizzes"
        :is-loading="quizzesStore.isLoading"
        empty-icon="mdi:book-open-variant-outline"
        empty-title="There are no quizzes"
        empty-text="No quiz found for the selected category"
        @load-more="quizzesStore.getQuizzes"
      >
        <AppAsyncCard v-for="quiz in filteredQuizzes" :key="quiz.uuid">
          <template v-slot:icon>
            <Icon icon="mdi:book-open-variant-outline" />
          </template>

          <template v-slot:content>
            <div class="info-top-row">
              <h3 class="quiz-title">{{ quiz.title }}</h3>
              <AppBadge :class="{ 'badge-public': quiz.is_public }">
                {{ quiz.is_public ? 'Public' : 'Private' }}
              </AppBadge>
            </div>
            <p class="quiz-description">{{ quiz.description }}</p>
            <div class="info-bottom-row">
              <span class="meta-item">
                <Icon icon="mdi:help-circle-outline" />
                {{ quiz.total_questions }} questions
              </span>
              <div class="quiz-id" @click="copyToClipboard(quiz.uuid)">
                {{ quiz.uuid }}
                <Icon icon="mdi:content-copy" class="copy-icon" />
              </div>
            </div>
          </template>

          <template v-slot:actions>
            <AppButton @click="goToQuiz(quiz.uuid)">View</AppButton>

            <div class="context-menu-wrapper" v-if="quiz.creator_uuid === currentUserUuid">
              <AppButton @click.stop="toggleMenu(quiz.uuid)">
                <Icon icon="mdi:dots-vertical" />
              </AppButton>

              <div class="dropdown-menu" v-if="activeMenuUuid === quiz.uuid" @click.stop>
                <AppButton @click="goToEdit(quiz.uuid)">
                  <span>Edit</span>
                </AppButton>

                <div class="dropdown-divider"></div>

                <AppButton class="btn-delete" @click="openDeleteQuizDialog(quiz.uuid)">
                  <span>Delete</span>
                </AppButton>
              </div>
            </div>
          </template>
        </AppAsyncCard>
      </AppAsyncList>
    </main>
  </div>

  <AppModal :is-open="isCreateQuizDialogOpen" @close="closeCreateQuizDialog">
    <template v-slot:header>
      <h1 class="modal-header-title">Create quiz</h1>
    </template>

    <template v-slot:body>
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
    </template>

    <template v-slot:footer>
      <AppButton @click="closeCreateQuizDialog">Cancel</AppButton>
      <AppButton @click="handleCreateQuiz" :disabled="!isFormValid || quizzesStore.isLoading">
        {{ quizzesStore.isLoading ? 'Processing' : 'Create' }}
      </AppButton>
    </template>
  </AppModal>

  <AppModal :is-open="isDeleteQuizDialogOpen" @close="closeDeleteQuizDialog">
    <template v-slot:header>
      <h1 class="modal-header-title">Delete quiz</h1>
    </template>

    <template v-slot:body>
      <p class="modal-text">Are you sure you want to delete this quiz?</p>
      <p class="modal-text">This action cannot be undone.</p>
    </template>

    <template v-slot:footer>
      <AppButton @click="closeDeleteQuizDialog">Cancel</AppButton>
      <AppButton class="btn-delete" @click="confirmDeleteQuiz" :disabled="quizzesStore.isLoading">
        {{ quizzesStore.isLoading ? 'Processing' : 'Delete' }}
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
.main-nav {
  padding-bottom: 1rem;
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
  word-break: break-all;
  overflow-wrap: anywhere;
  hyphens: auto;
  min-width: 0;
  max-width: 100%;
}
.badge-public {
  background-color: color-mix(in srgb, var(--color-primary) 15%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-primary) 30%, transparent);
  color: var(--color-primary);
}
.quiz-id {
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
.quiz-id:hover {
  color: var(--color-text);
}
.copy-icon {
  font-size: 0.9rem;
}
.quiz-description {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
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
  color: var(--color-text-secondary);
  margin-top: 0.2rem;
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

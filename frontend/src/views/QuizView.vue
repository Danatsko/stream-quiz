<script setup lang="ts">
import { onMounted, onBeforeUnmount, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth'
import useQuizzesStore from '@/stores/quizzes'
import AppButton from '@/components/AppButton.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const quizzesStore = useQuizzesStore()

const isDeleteQuizDialogOpen = ref(false)

const quizUuid = computed(() => route.params.uuid as string)
const quiz = computed(() => quizzesStore.quiz)
const isLoading = computed(() => quizzesStore.isLoading)

const currentUserUuid = computed((): string | null => {
  return authStore.user === null ? null : authStore.user.uuid
})

const isCreator = computed((): boolean => {
  return quiz.value?.creator_uuid === currentUserUuid.value
})

onMounted(async () => {
  if (quizUuid.value) {
    await quizzesStore.getQuiz(quizUuid.value)
  }
})

onBeforeUnmount(() => {
  quizzesStore.clearQuiz()
})

const goBack = async (): Promise<void> => {
  await router.push({ name: 'Quizzes' })
}

const copyToClipboard = (text: string): void => {
  navigator.clipboard.writeText(text)
}

const openDeleteQuizDialog = (): void => {
  isDeleteQuizDialogOpen.value = true
}

const closeDeleteQuizDialog = (): void => {
  isDeleteQuizDialogOpen.value = false
}

const confirmDeleteQuiz = async (): Promise<void> => {
  if (!quiz.value?.uuid) {
    return
  }

  try {
    await quizzesStore.deleteQuiz(quiz.value.uuid)
    closeDeleteQuizDialog()
    await router.push({ name: 'Quizzes' })
  } catch (error) {}
}

const editQuiz = (): void => {}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <button class="btn-back" @click="goBack">
          <span>Back to quizzes</span>
        </button>

        <div class="header-actions" v-if="isCreator && quiz">
          <AppButton class="btn-action-outline" @click="editQuiz"> Edit </AppButton>
          <AppButton class="btn-action-outline delete" @click="openDeleteQuizDialog">
            Delete
          </AppButton>
        </div>
      </div>
    </header>

    <main class="main" v-if="isLoading && !quiz">
      <div class="empty-state">
        <Icon icon="mdi:loading" class="spin-icon empty-icon" />
        <p class="empty-text">Loading quiz details...</p>
      </div>
    </main>

    <main class="main" v-else-if="quiz">
      <div class="quiz-content-wrapper">
        <div class="quiz-hero-card">
          <div class="hero-top-row">
            <h1 class="hero-title">{{ quiz.title }}</h1>
            <span :class="['badge', quiz.is_public ? 'public' : 'private']">
              {{ quiz.is_public ? 'Public' : 'Private' }}
            </span>
          </div>

          <p class="hero-description">{{ quiz.description }}</p>

          <div class="hero-bottom-row">
            <span class="meta-item">
              <Icon icon="mdi:help-circle-outline" />
              {{ quiz.questions.length }} questions
            </span>
            <div class="quiz-id" @click="copyToClipboard(quiz.uuid)" title="Copy uuid">
              {{ quiz.uuid }}
              <Icon icon="mdi:content-copy" class="copy-icon" />
            </div>
          </div>
        </div>

        <div class="questions-list">
          <div v-if="quiz.questions.length === 0" class="empty-state-small">
            <Icon icon="mdi:help-circle-outline" class="empty-icon-small" />
            <p>This quiz has no questions</p>
          </div>

          <div class="question-card" v-for="question in quiz.questions" :key="question.uuid">
            <div class="question-header">
              <div class="question-title-wrapper">
                <h3 class="question-text">{{ question.text }}</h3>
              </div>
              <span class="badge type-badge">
                {{ question.is_multiple_answers ? 'Multiple choice' : 'Single choice' }}
              </span>
            </div>

            <div class="options-list">
              <div
                v-for="option in question.options"
                :key="option.uuid"
                :class="['option-item', { 'is-correct': option.is_correct }]"
              >
                <div class="option-icon-wrapper">
                  <Icon
                    v-if="option.is_correct"
                    icon="mdi:check-circle"
                    class="option-icon correct"
                  />
                  <Icon
                    v-else-if="question.is_multiple_answers"
                    icon="mdi:checkbox-blank-outline"
                    class="option-icon neutral"
                  />
                  <Icon v-else icon="mdi:circle-outline" class="option-icon neutral" />
                </div>
                <span class="option-text">{{ option.text }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>

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
  padding-left: 0.5rem;
  flex-shrink: 0;
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.btn-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: transparent;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  color: white;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.5rem 1.2rem;
  transition: color 0.2s;
}
.btn-back:hover {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 1px 3px var(--color-secondary);
}
.btn-back:active {
  transform: scale(0.95);
}
.header-actions {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
}
.btn-action-outline {
  background: transparent;
  color: white;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 0.5rem 1.5rem;
  font-size: 0.9rem;
  min-width: 100px;
}
.btn-action-outline:hover {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 1px 3px var(--color-secondary);
}
.btn-action-outline.delete {
  color: #ef4444;
  border-color: #2a2a2a;
}
.btn-action-outline.delete:hover {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
  box-shadow:
    0 0 1px 1px #ef4444,
    0 0 5px 1px rgba(239, 68, 68, 0.5);
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}
.quiz-content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  gap: 1.5rem;
  padding: 0.5rem;
  min-height: 0;
}
.quiz-content-wrapper::-webkit-scrollbar {
  width: 8px;
  cursor: pointer;
}
.quiz-content-wrapper::-webkit-scrollbar-track {
  background: transparent;
}
.quiz-content-wrapper::-webkit-scrollbar-thumb {
  background-color: #2a2a2a;
  border-radius: 10px;
}
.quiz-hero-card {
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
}
.hero-top-row {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  max-width: 100%;
}
.hero-title {
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0;
  color: white;
  word-break: break-all;
  overflow-wrap: anywhere;
  min-width: 0;
  max-width: 100%;
}
.hero-description {
  margin: 0;
  font-size: 1rem;
  color: #9ca3af;
  line-height: 1.5;
  word-wrap: break-word;
  overflow-wrap: anywhere;
}
.hero-bottom-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.85rem;
  color: #9ca3af;
  margin-top: 0.5rem;
  flex-wrap: wrap;
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
.type-badge {
  background-color: #121212;
  border: 1px solid color-mix(in srgb, #9ca3af 30%, transparent);
  color: #9ca3af;
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}
.quiz-id {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-family: monospace;
  font-size: 0.8rem;
  color: #9ca3af;
  background-color: #1a1a1a;
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
.quiz-id:hover {
  color: white;
  background-color: #2a2a2a;
}
.copy-icon {
  font-size: 0.9rem;
}
.questions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.question-card {
  background-color: transparent;
  border: 1px solid #2a2a2a;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  width: 100%;
  box-sizing: border-box;
}
.question-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  max-width: 100%;
}
.question-title-wrapper {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  flex: 1;
  min-width: 0;
}
.question-text {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: white;
  line-height: 1.4;
  word-break: break-all;
  overflow-wrap: anywhere;
}
.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.option-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  background-color: #121212;
  transition:
    border-color 0.2s,
    background-color 0.2s;
  width: 100%;
  box-sizing: border-box;
}
.option-item.is-correct {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.05);
}
.option-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  flex-shrink: 0;
}
.option-icon {
  font-size: 1.25rem;
}
.option-icon.correct {
  color: #10b981;
}
.option-icon.neutral {
  color: #4b5563;
}
.option-text {
  font-size: 0.95rem;
  color: #e5e7eb;
  line-height: 1.4;
  word-break: break-word;
  overflow-wrap: anywhere;
  flex: 1;
  min-width: 0;
  max-width: 100%;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #9ca3af;
  gap: 1rem;
}
.empty-state-small {
  text-align: center;
  padding: 3rem 1rem;
  color: white;
  border-radius: 12px;
}
.empty-icon {
  font-size: 3rem;
}
.empty-icon-small {
  font-size: 2rem;
  margin-bottom: 0.5rem;
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

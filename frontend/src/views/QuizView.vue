<script setup lang="ts">
import { onMounted, onBeforeUnmount, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth'
import useQuizzesStore from '@/stores/quizzes'
import AppButton from '@/components/AppButton.vue'
import AppModal from '@/components/AppModal.vue'
import AppBadge from '@/components/AppBadge.vue'
import AppListCard from '@/components/AppListCard.vue'
import { formatDateTime } from '@/utils/formatters'

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
    try {
      await quizzesStore.getQuiz(quizUuid.value)

      if (!quiz.value) {
        await router.push({ name: 'Quizzes' })

        return
      }

      if (quiz.value.creator_uuid !== currentUserUuid.value) {
        if (!quiz.value.is_public) {
          await router.push({ name: 'Quizzes' })

          return
        }
      }
    } catch (onMountedError) {
      await router.push({ name: 'Quizzes' })
    }
  }
})

onBeforeUnmount(() => {
  quizzesStore.clearQuiz()
})

const goBack = async (): Promise<void> => {
  await router.push({ name: 'Quizzes' })
}

const goToEdit = async (): Promise<void> => {
  await router.push({
    name: 'QuizEdit',
    params: {
      uuid: quizUuid.value,
    },
  })
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
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <AppButton @click="goBack" title="Back to quizzes" aria-label="Back to quizzes">
          <Icon icon="mdi:chevron-left" />
        </AppButton>

        <div class="header-actions" v-if="isCreator && quiz">
          <AppButton @click="goToEdit" title="Edit" aria-label="Edit">
            <Icon icon="mdi:edit-outline" />
          </AppButton>
          <AppButton
            class="btn-delete"
            @click="openDeleteQuizDialog"
            title="Delete"
            aria-label="Delete"
          >
            <Icon icon="mdi:delete-outline" />
          </AppButton>
        </div>
      </div>
    </header>

    <main class="main" v-if="isLoading && !quiz">
      <div class="empty-state">
        <Icon icon="mdi:loading" class="spin-icon empty-icon" />
        <p class="empty-text">Loading</p>
      </div>
    </main>

    <main class="main" v-else-if="quiz">
      <div class="quiz-content-wrapper">
        <AppListCard>
          <template v-slot:icon>
            <Icon icon="mdi:book-open-variant-outline" />
          </template>

          <template v-slot:content>
            <div class="hero-top">
              <h1 class="hero-title">{{ quiz.title }}</h1>
              <AppBadge :class="{ 'badge-public': quiz.is_public }">
                {{ quiz.is_public ? 'Public' : 'Private' }}
              </AppBadge>
            </div>

            <p class="hero-description">{{ quiz.description }}</p>

            <div class="hero-bottom">
              <span class="meta-item">
                <Icon icon="mdi:help-circle-outline" />
                {{ quiz.questions.length }} questions
              </span>

              <span class="meta-item" v-if="quiz.created_at">
                <Icon icon="mdi:calendar-plus" />
                {{ formatDateTime(quiz.created_at) }}
              </span>

              <span class="meta-item" v-if="quiz.updated_at">
                <Icon icon="mdi:calendar-edit" />
                {{ formatDateTime(quiz.updated_at) }}
              </span>

              <div class="meta-item" v-if="quiz.uuid">
                <Icon icon="mdi:identifier" />

                <div class="quiz-id" @click="copyToClipboard(quiz.uuid)" title="Copy UUID">
                  {{ quiz.uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>
            </div>
          </template>
        </AppListCard>

        <div class="questions-list">
          <div v-if="quiz.questions.length === 0" class="empty-state-small">
            <Icon icon="mdi:help-circle-outline" class="empty-icon-small" />
            <p>This quiz has no questions</p>
          </div>

          <AppListCard v-for="question in quiz.questions" :key="question.uuid">
            <template v-slot:icon>
              <Icon icon="mdi:help-circle-outline" />
            </template>

            <template v-slot:content>
              <div class="question-header">
                <div class="question-title-wrapper">
                  <h3 class="question-text">{{ question.text }}</h3>
                </div>
                <AppBadge>
                  {{ question.is_multiple_answers ? 'Multiple choice' : 'Single choice' }}
                </AppBadge>
              </div>

              <div class="options-list">
                <AppListCard
                  v-for="option in question.options"
                  :key="option.uuid"
                  :class="['option-item', { 'is-correct': option.is_correct }]"
                >
                  <template v-slot:icon>
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
                  </template>

                  <template v-slot:content>
                    <span class="option-text">{{ option.text }}</span>
                  </template>
                </AppListCard>
              </div>
            </template>
          </AppListCard>
        </div>
      </div>
    </main>
  </div>

  <AppModal :is-open="isDeleteQuizDialogOpen" @close="closeDeleteQuizDialog">
    <template v-slot:header>
      <h1 class="modal-header-title">Delete quiz</h1>
    </template>

    <template v-slot:body>
      <p class="modal-text">Are you sure you want to delete this quiz?</p>
      <p class="modal-text">This action cannot be undone</p>
    </template>

    <template v-slot:footer>
      <AppButton @click="closeDeleteQuizDialog" title="Cancel" aria-label="Cancel"
        >Cancel</AppButton
      >
      <AppButton
        class="btn-delete"
        @click="confirmDeleteQuiz"
        :disabled="quizzesStore.isLoading"
        title="Delete"
        aria-label="Delete"
      >
        {{ quizzesStore.isLoading ? 'Processing' : 'Delete' }}
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
  justify-content: space-between;
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
.quiz-content-wrapper {
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
.badge-public {
  position: relative;
  z-index: 0;
  border-color: transparent;
  background: var(--linear-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.badge-public::before {
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
.badge-public::after {
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
.quiz-id:hover {
  color: var(--color-text);
}
.copy-icon {
  font-size: 0.9rem;
}
.questions-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-left: 1rem;
  padding-right: 1rem;
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
  background-color: var(--color-background-secondary);
  transition:
    border-color 0.2s,
    background-color 0.2s;
}
.option-item:hover {
  border-color: #4b5563 !important;
  box-shadow:
    0 0 1px 1px #4b5563,
    0 0 10px 1px rgba(75, 85, 99, 0.5) !important;
}
.option-item.is-correct {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.05);
}
.option-item.is-correct:hover {
  border-color: #10b981 !important;
  box-shadow:
    0 0 1px 1px #10b981,
    0 0 10px 1px rgba(16, 185, 129, 0.5) !important;
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
  color: var(--color-text-secondary);
  gap: 1rem;
}
.empty-state-small {
  text-align: center;
  padding: 3rem 1rem;
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

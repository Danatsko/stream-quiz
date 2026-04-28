<script setup lang="ts">
import { onMounted, onBeforeUnmount, computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth'
import useQuizzesStore from '@/stores/quizzes'
import AppButton from '@/components/AppButton.vue'
import AppModal from '@/components/AppModal.vue'
import AppBadge from '@/components/AppBadge.vue'
import type { FullUpdateQuizPayload } from '@/types/quizzes'
import AppErrorMessage from '@/components/AppErrorMessage.vue'
import AppListCard from '@/components/AppListCard.vue'
import AppInput from '@/components/AppInput.vue'
import AppTextarea from '@/components/AppTextarea.vue'

interface EditOption {
  uiUuid: string
  uuid?: string
  text: string
  is_correct: boolean
}

interface EditQuestion {
  uiUuid: string
  uuid?: string
  text: string
  is_multiple_answers: boolean
  options: Array<EditOption>
}

interface EditQuiz {
  uuid: string
  title: string
  description: string
  is_public: boolean
  questions: Array<EditQuestion>
}

const MIN_QUIZ_TITLE_LENGTH = 3
const MAX_QUIZ_TITLE_LENGTH = 100
const MAX_QUIZ_DESCRIPTION_LENGTH = 500
const MIN_QUESTION_TEXT_LENGTH = 3
const MAX_QUESTION_TEXT_LENGTH = 500
const MIN_QUESTION_OPTIONS = 1
const MIN_OPTION_TEXT_LENGTH = 3
const MAX_OPTION_TEXT_LENGTH = 500

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const quizzesStore = useQuizzesStore()

const isDeleteQuizDialogOpen = ref(false)

const quizUuid = computed(() => route.params.uuid as string)
const quiz = computed(() => quizzesStore.quiz)
const isLoading = computed(() => quizzesStore.isLoading)
const isSaving = ref(false)

const currentUserUuid = computed((): string | null => {
  return authStore.user === null ? null : authStore.user.uuid
})

const editableQuiz = ref<EditQuiz | null>(null)

const initEditableQuiz = (): void => {
  if (!quiz.value) {
    return
  }

  editableQuiz.value = {
    uuid: quiz.value.uuid,
    title: quiz.value.title,
    description: quiz.value.description,
    is_public: quiz.value.is_public,
    questions: quiz.value.questions.map((question) => ({
      uiUuid: crypto.randomUUID(),
      uuid: question.uuid,
      text: question.text,
      is_multiple_answers: question.is_multiple_answers,
      options: question.options.map((option) => ({
        uiUuid: crypto.randomUUID(),
        uuid: option.uuid,
        text: option.text,
        is_correct: option.is_correct || false,
      })),
    })),
  }
}

watch(quiz, initEditableQuiz)

onMounted(async () => {
  if (quizUuid.value) {
    try {
      await quizzesStore.getQuiz(quizUuid.value)

      if (!quiz.value) {
        await router.push({ name: 'Quizzes' })

        return
      }

      if (quiz.value.creator_uuid !== currentUserUuid.value) {
        if (quiz.value.is_public) {
          await router.push({ name: 'Quiz', params: { uuid: quizUuid.value } })
        } else {
          await router.push({ name: 'Quizzes' })
        }

        return
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
  await router.push({
    name: 'Quiz',
    params: {
      uuid: quizUuid.value,
    },
  })
}

const toggleIsPublic = (): void => {
  if (!editableQuiz.value) {
    return
  }

  editableQuiz.value.is_public = !editableQuiz.value.is_public
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

const addQuestion = (): void => {
  if (!editableQuiz.value) {
    return
  }

  editableQuiz.value.questions.push({
    uiUuid: crypto.randomUUID(),
    text: '',
    is_multiple_answers: false,
    options: [{ uiUuid: crypto.randomUUID(), text: '', is_correct: true }],
  })
}

const removeQuestion = (uiUuid: string): void => {
  if (!editableQuiz.value) {
    return
  }

  const questionIndex = editableQuiz.value.questions.findIndex(
    (question) => question.uiUuid === uiUuid,
  )

  if (questionIndex !== -1) {
    editableQuiz.value.questions.splice(questionIndex, 1)
  }
}

const addOption = (questionUiUuid: string): void => {
  if (!editableQuiz.value) {
    return
  }

  const question = editableQuiz.value.questions.find(
    (question) => question.uiUuid === questionUiUuid,
  )

  if (question) {
    question.options.push({
      uiUuid: crypto.randomUUID(),
      text: '',
      is_correct: false,
    })
  }
}

const removeOption = (questionUiUuid: string, uiUuid: string): void => {
  if (!editableQuiz.value) {
    return
  }

  const question = editableQuiz.value.questions.find(
    (question) => question.uiUuid === questionUiUuid,
  )

  if (question) {
    const optionIndex = question.options.findIndex((option) => option.uiUuid === uiUuid)

    if (optionIndex !== -1) {
      question.options.splice(optionIndex, 1)
    }
  }
}

const toggleOptionCorrectness = (questionUiUuid: string, uiUuid: string): void => {
  if (!editableQuiz.value) {
    return
  }

  const question = editableQuiz.value.questions.find(
    (question) => question.uiUuid === questionUiUuid,
  )

  if (!question) {
    return
  }

  const option = question.options.find((option) => option.uiUuid === uiUuid)

  if (!option) {
    return
  }

  if (!question.is_multiple_answers) {
    question.options.forEach((option) => {
      option.is_correct = option.uiUuid === uiUuid
    })
  } else {
    option.is_correct = !option.is_correct
  }
}

const toggleMultipleAnswers = (uiUuid: string): void => {
  if (!editableQuiz.value) {
    return
  }

  const question = editableQuiz.value.questions.find((question) => question.uiUuid === uiUuid)

  if (!question) {
    return
  }

  question.is_multiple_answers = !question.is_multiple_answers

  if (!question.is_multiple_answers) {
    let foundCorrect = false

    question.options.forEach((option) => {
      if (option.is_correct && !foundCorrect) {
        foundCorrect = true
      } else {
        option.is_correct = false
      }
    })

    if (!foundCorrect && question.options.length > 0) {
      if (question.options[0]) {
        question.options[0].is_correct = true
      }
    }
  }
}

const isQuizTitleValid = computed((): boolean => {
  if (!editableQuiz.value) {
    return false
  }

  const { title } = editableQuiz.value

  return !!title && title.length >= MIN_QUIZ_TITLE_LENGTH && title.length <= MAX_QUIZ_TITLE_LENGTH
})

const isQuizDescriptionValid = computed((): boolean => {
  if (!editableQuiz.value) {
    return false
  }

  const { description } = editableQuiz.value

  return !description || description.length <= MAX_QUIZ_DESCRIPTION_LENGTH
})

const isQuestionTextValid = (question: EditQuestion): boolean => {
  const { text } = question

  return (
    !!text && text.length >= MIN_QUESTION_TEXT_LENGTH && text.length <= MAX_QUESTION_TEXT_LENGTH
  )
}

const isQuestionOptionsCountValid = (question: EditQuestion): boolean => {
  return question.options.length >= MIN_QUESTION_OPTIONS
}

const isQuestionOptionsCorrectValid = (question: EditQuestion): boolean => {
  return question.options.some((option) => option.is_correct)
}

const isOptionTextValid = (option: EditOption): boolean => {
  const { text } = option

  return !!text && text.length >= MIN_OPTION_TEXT_LENGTH && text.length <= MAX_OPTION_TEXT_LENGTH
}

const isFormValid = computed((): boolean => {
  if (!editableQuiz.value) {
    return false
  }

  if (!isQuizTitleValid.value || !isQuizDescriptionValid.value) {
    return false
  }

  for (const question of editableQuiz.value.questions) {
    if (
      !isQuestionTextValid(question) ||
      !isQuestionOptionsCountValid(question) ||
      !isQuestionOptionsCorrectValid(question)
    ) {
      return false
    }

    for (const option of question.options) {
      if (!isOptionTextValid(option)) {
        return false
      }
    }
  }

  return true
})

const hasChanges = computed((): boolean => {
  if (!editableQuiz.value || !quiz.value) {
    return false
  }

  const normalizeData = (data: any) => ({
    title: data.title,
    description: data.description,
    is_public: data.is_public,
    questions: data.questions.map((question: any) => ({
      text: question.text,
      is_multiple_answers: question.is_multiple_answers,
      options: question.options.map((option: any) => ({
        text: option.text,
        is_correct: option.is_correct || false,
      })),
    })),
  })

  const originalStr = JSON.stringify(normalizeData(quiz.value))
  const editedStr = JSON.stringify(normalizeData(editableQuiz.value))

  return originalStr !== editedStr
})

const saveChanges = async (): Promise<void> => {
  if (!editableQuiz.value || !quiz.value || !isFormValid.value || !hasChanges.value) {
    return
  }

  isSaving.value = true

  try {
    const quizUuid = quiz.value.uuid

    const payload: FullUpdateQuizPayload = {
      title: editableQuiz.value.title,
      description: editableQuiz.value.description,
      is_public: editableQuiz.value.is_public,
      questions: editableQuiz.value.questions.map((question) => ({
        uuid: question.uuid || null,
        text: question.text,
        is_multiple_answers: question.is_multiple_answers,
        options: question.options.map((option) => ({
          uuid: option.uuid || null,
          text: option.text,
          is_correct: option.is_correct,
        })),
      })),
    }

    await quizzesStore.fullUpdateQuiz(quiz.value.uuid, payload)
    await goBack()
  } catch (error) {
  } finally {
    isSaving.value = false
  }
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <AppButton @click="goBack" :disabled="isSaving" title="Cancel" aria-label="Cancel">
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
            @click="openDeleteQuizDialog"
            title="Delete"
            aria-label="Delete"
          >
            <Icon icon="mdi:delete-outline" />
          </AppButton>
        </div>
      </div>
    </header>

    <main class="main" v-if="isLoading && !editableQuiz">
      <div class="empty-state">
        <Icon icon="mdi:loading" class="spin-icon empty-icon" />
        <p class="empty-text">Loading</p>
      </div>
    </main>

    <main class="main" v-else-if="editableQuiz">
      <div class="quiz-content-wrapper">
        <AppListCard>
          <template v-slot:icon>
            <Icon icon="mdi:book-open-variant-outline" />
          </template>

          <template v-slot:content>
            <div class="hero-top">
              <AppInput
                id="quiz-title"
                type="text"
                label="Title"
                placeholder="Title"
                v-model="editableQuiz.title"
                :minlength="MIN_QUIZ_TITLE_LENGTH"
                :maxLength="MAX_QUIZ_TITLE_LENGTH"
                :has-error="!!editableQuiz.title && !isQuizTitleValid"
                :error-message="`Minimum ${MIN_QUIZ_TITLE_LENGTH} characters`"
              >
                <template v-slot:icon>
                  <Icon icon="mdi:format-align-left" />
                </template>
              </AppInput>

              <div
                class="clickable-badge"
                @click="toggleIsPublic"
                title="Change visibility"
                aria-label="Change visibility"
              >
                <AppBadge :class="{ 'badge-public': editableQuiz.is_public }">
                  {{ editableQuiz.is_public ? 'Public' : 'Private' }}
                </AppBadge>
              </div>
            </div>

            <AppTextarea
              id="quiz-description"
              type="text"
              label="Description"
              placeholder="Description"
              v-model="editableQuiz.description"
              :maxLength="MAX_QUIZ_DESCRIPTION_LENGTH"
            />
          </template>
        </AppListCard>

        <div class="questions-list">
          <AppListCard v-for="question in editableQuiz.questions" :key="question.uiUuid">
            <template v-slot:icon>
              <Icon icon="mdi:help-circle-outline" />
            </template>

            <template v-slot:content>
              <div class="question-header">
                <AppTextarea
                  :id="'question-' + question.uiUuid"
                  label="Question text"
                  placeholder="Question text"
                  v-model="question.text"
                  :minlength="MIN_QUESTION_TEXT_LENGTH"
                  :maxLength="MAX_QUESTION_TEXT_LENGTH"
                  :has-error="!!question.text && !isQuestionTextValid(question)"
                  :error-message="`Minimum ${MIN_QUESTION_TEXT_LENGTH} characters`"
                />

                <div
                  class="clickable-badge"
                  @click="toggleMultipleAnswers(question.uiUuid)"
                  title="Change question type"
                  aria-label="Change question type"
                >
                  <AppBadge>
                    {{ question.is_multiple_answers ? 'Multiple choice' : 'Single choice' }}
                  </AppBadge>
                </div>
              </div>

              <div class="options-list">
                <AppListCard
                  v-for="option in question.options"
                  :key="option.uiUuid"
                  :class="['option-item', { 'is-correct': option.is_correct }]"
                >
                  <template v-slot:icon>
                    <div
                      :style="{ cursor: 'pointer' }"
                      @click="toggleOptionCorrectness(question.uiUuid, option.uiUuid)"
                    >
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
                  </template>

                  <template v-slot:content>
                    <AppTextarea
                      :id="'option-' + option.uiUuid"
                      label="Option text"
                      placeholder="Option text"
                      v-model="option.text"
                      :minlength="MIN_OPTION_TEXT_LENGTH"
                      :maxLength="MAX_OPTION_TEXT_LENGTH"
                      :has-error="!!option.text && !isOptionTextValid(option)"
                      :error-message="`Minimum ${MIN_OPTION_TEXT_LENGTH} characters`"
                    />
                  </template>

                  <template v-slot:actions>
                    <AppButton
                      class="btn-delete"
                      @click="removeOption(question.uiUuid, option.uiUuid)"
                      title="Remove option"
                      aria-label="Remove option"
                    >
                      <Icon icon="mdi:cancel-outline" />
                    </AppButton>
                  </template>
                </AppListCard>

                <AppButton
                  @click="addOption(question.uiUuid)"
                  title="Add option"
                  aria-label="Add option"
                >
                  <span>Add option</span>
                </AppButton>
              </div>

              <AppErrorMessage v-if="question.options && !isQuestionOptionsCountValid(question)">
                Minimum {{ MIN_QUESTION_OPTIONS }} option
              </AppErrorMessage>
              <AppErrorMessage v-if="question.options && !isQuestionOptionsCorrectValid(question)">
                Minimum 1 correct option
              </AppErrorMessage>
            </template>

            <template v-slot:actions>
              <AppButton
                class="btn-delete"
                @click="removeQuestion(question.uiUuid)"
                title="Remove question"
                aria-label="Remove question"
              >
                <Icon icon="mdi:cancel-outline" />
              </AppButton>
            </template>
          </AppListCard>

          <AppButton @click="addQuestion" title="Add question" aria-label="Add question">
            <span>Add question</span>
          </AppButton>
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
      <p class="modal-text">This action cannot be undone.</p>
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
  overflow: hidden;
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
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
  gap: 1rem;
}
.empty-icon {
  font-size: 3rem;
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

.clickable-badge {
  cursor: pointer;
  user-select: none;
}
.clickable-badge:hover {
  opacity: 0.8;
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

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import AppButton from '@/components/AppButton.vue'
import AppListCard from '@/components/AppListCard.vue'
import AppBadge from '@/components/AppBadge.vue'
import useTakeStore from '@/stores/take'
import { formatDuration } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()
const takeStore = useTakeStore()

const sessionUuid = computed(() => route.params.uuid as string)

const pendingQueue = ref<string[]>([])
const selectedOptions = ref<string[]>([])

const timeLeft = ref<string>('--:--:--')
const isTimeUp = ref<boolean>(false)
const isTimerDanger = ref<boolean>(false)
let timerInterval: number | null = null

watch(
  () => takeStore.error,
  (newError) => {
    if (newError) {
      if (isSessionCompleted.value) {
        return
      }

      takeStore.disconnectFromSession()
      takeStore.clearState()
      router.push({ name: 'Take' })
    }
  },
)

watch(
  () => takeStore.questions,
  (newQuestions) => {
    if (pendingQueue.value.length === 0 && newQuestions.length > 0 && !isTimeUp.value) {
      pendingQueue.value = newQuestions.map((q) => q.uuid)
    }
  },
  { immediate: true },
)

const currentQuestion = computed(() => {
  if (pendingQueue.value.length === 0) {
    return null
  }

  const uuid = pendingQueue.value[0]

  return takeStore.questions.find((question) => question.uuid === uuid) || null
})

const isSessionCompleted = computed((): boolean => {
  if (takeStore.totalQuestions === null) {
    return false
  }

  return pendingQueue.value.length === 0 || isTimeUp.value
})

const canSkip = computed((): boolean => {
  return pendingQueue.value.length > 1
})

const updateTimer = (): void => {
  if (takeStore.endTimeTs === null) {
    timeLeft.value = '--:--:--'
    isTimerDanger.value = false

    return
  }

  const now = Date.now() / 1000
  const diff = Math.max(0, Math.round(takeStore.endTimeTs - now))

  if (diff <= 0) {
    timeLeft.value = '00:00:00'
    isTimeUp.value = true
    isTimerDanger.value = true

    if (timerInterval) {
      clearInterval(timerInterval)

      timerInterval = null
    }

    return
  }

  timeLeft.value = formatDuration(diff)
  isTimerDanger.value = diff < 60
}

onMounted(() => {
  if (!sessionUuid.value) {
    router.push({ name: 'Take' })

    return
  }

  takeStore.connectToSession(sessionUuid.value)

  timerInterval = window.setInterval(updateTimer, 1000)

  updateTimer()
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }

  takeStore.disconnectFromSession()
  takeStore.clearState()
})

const toggleOption = (optionUuid: string): void => {
  if (!currentQuestion.value) {
    return
  }

  if (currentQuestion.value.is_multiple_answers) {
    const index = selectedOptions.value.indexOf(optionUuid)

    if (index > -1) {
      selectedOptions.value.splice(index, 1)
    } else {
      selectedOptions.value.push(optionUuid)
    }
  } else {
    selectedOptions.value = [optionUuid]
  }
}

const isOptionSelected = (optionUuid: string): boolean => {
  return selectedOptions.value.includes(optionUuid)
}

const handleSubmit = (): void => {
  if (!currentQuestion.value || selectedOptions.value.length === 0) {
    return
  }

  const plainOptions = Array.from(selectedOptions.value)

  takeStore.submitAnswer(currentQuestion.value.uuid, plainOptions)
  pendingQueue.value.shift()

  selectedOptions.value = []
}

const handleSkip = (): void => {
  if (!canSkip.value) {
    return
  }

  const skippedUuid = pendingQueue.value.shift()

  if (skippedUuid) {
    pendingQueue.value.push(skippedUuid)
  }

  selectedOptions.value = []
}

const handleExit = async (): Promise<void> => {
  takeStore.disconnectFromSession()
  await router.push({ name: 'Home' })
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <AppButton @click="handleExit" variant="secondary" title="Exit" aria-label="Exit">
          <Icon icon="mdi:logout" />
        </AppButton>

        <div class="header-actions">
          <div class="timer" :class="{ 'timer-danger': isTimerDanger }">
            <Icon icon="mdi:timer-outline" class="timer-icon" />
            <span>{{ timeLeft }}</span>
          </div>
        </div>
      </div>
    </header>

    <main class="main" v-if="!takeStore.isConnected && !isSessionCompleted">
      <div class="empty-state">
        <Icon icon="mdi:loading" class="spin-icon empty-icon" />
        <p class="empty-text">Connecting to session</p>
      </div>
    </main>

    <main class="main" v-else>
      <div class="session-content-wrapper">
        <div v-if="isSessionCompleted" class="completed-state">
          <Icon icon="mdi:flag-checkered" class="completed-icon" />
          <h2 class="completed-title">Session completed</h2>
          <p class="completed-text" v-if="isTimeUp">Time is up</p>
          <p class="completed-text" v-else>You have answered all questions</p>
          <AppButton
            class="btn-exit"
            @click="handleExit"
            title="Return to home"
            aria-label="Return to home"
          >
            Return to home
          </AppButton>
        </div>

        <div v-else-if="currentQuestion" class="question-container">
          <div class="progress-indicator">
            Question {{ (takeStore.totalQuestions || 0) - pendingQueue.length + 1 }} of
            {{ takeStore.totalQuestions }}
          </div>

          <AppListCard>
            <template v-slot:icon>
              <Icon icon="mdi:help-circle-outline" />
            </template>

            <template v-slot:content>
              <div class="question-header">
                <div class="question-title-wrapper">
                  <h3 class="question-text">{{ currentQuestion.text }}</h3>
                </div>
                <AppBadge>
                  {{ currentQuestion.is_multiple_answers ? 'Multiple choice' : 'Single choice' }}
                </AppBadge>
              </div>

              <div class="options-list">
                <AppListCard
                  v-for="option in currentQuestion.options"
                  :key="option.uuid"
                  :class="['option-item', { 'is-selected': isOptionSelected(option.uuid) }]"
                  @click="toggleOption(option.uuid)"
                  style="cursor: pointer"
                >
                  <template v-slot:icon>
                    <Icon
                      v-if="isOptionSelected(option.uuid)"
                      icon="mdi:check-circle"
                      class="option-icon selected"
                    />
                    <Icon
                      v-else-if="currentQuestion.is_multiple_answers"
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

          <div class="actions">
            <AppButton
              v-if="canSkip"
              class="btn-skip"
              @click="handleSkip"
              title="Skip"
              aria-label="Skip"
            >
              <Icon icon="mdi:skip-next-outline" />
            </AppButton>
            <div class="flex-spacer" v-else></div>
            <AppButton
              :disabled="selectedOptions.length === 0"
              @click="handleSubmit"
              title="Submit"
              aria-label="Submit"
            >
              <Icon icon="mdi:success-bold" />
            </AppButton>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout {
  width: 90vw;
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  padding-bottom: 2rem;
  min-height: 100vh;
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
  align-items: center;
}

.timer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.25rem;
  font-weight: 800;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background-color: var(--color-background-secondary);
  color: var(--color-text);
  font-family: monospace;
  transition: color 0.3s;
}
.timer-icon {
  font-size: 1.5rem;
}
.timer-danger {
  color: red;
}

.main {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.session-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 0.25rem 1rem 0.25rem 0.5rem;
}

.question-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.progress-indicator {
  font-size: 0.9rem;
  font-weight: 600;
  text-align: right;
  padding-right: 0.5rem;
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
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.4;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1rem;
}

.option-item {
  background-color: var(--color-background-secondary);
  transition:
    border-color 0.2s,
    background-color 0.2s,
    transform 0.1s;
}
.option-item:hover {
  border-color: var(--color-primary);
}
.option-item:active {
  transform: scale(0.99);
}
.option-item.is-selected {
  border-color: var(--color-primary);
  background-color: color-mix(in srgb, var(--color-primary) 5%, transparent);
}
.option-item.is-selected:hover {
  border-color: var(--color-primary) !important;
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 1px 3px color-mix(in srgb, var(--color-primary) 20%, transparent) !important;
}

.option-icon {
  font-size: 1.25rem;
}
.option-icon.selected {
  color: var(--color-primary);
}
.option-icon.neutral {
  color: var(--color-text-secondary);
}
.option-text {
  font-size: 1rem;
  line-height: 1.4;
  word-break: break-word;
  overflow-wrap: anywhere;
  flex: 1;
  min-width: 0;
  max-width: 100%;
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}
.flex-spacer {
  flex: 1;
}

.empty-state,
.completed-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 300px;
  gap: 1rem;
  text-align: center;
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

.completed-icon {
  font-size: 4rem;
  color: var(--color-text);
  margin-bottom: 1rem;
}
.completed-title {
  font-size: 2rem;
  font-weight: 900;
  color: var(--color-text);
  margin: 0;
}
.completed-text {
  font-size: 1.1rem;
  margin: 0 0 1.5rem 0;
}
</style>

<script setup lang="ts">
import { onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import useHistoryStore from '@/stores/history'
import AppButton from '@/components/AppButton.vue'
import AppBadge from '@/components/AppBadge.vue'
import AppListCard from '@/components/AppListCard.vue'
import { formatDuration } from '@/utils/formatters'

const route = useRoute()
const router = useRouter()
const historyStore = useHistoryStore()

const sessionUuid = computed(() => route.params.uuid as string)
const session = computed(() => historyStore.session)
const isLoading = computed(() => historyStore.isLoading)

const sessionStatusLabels: Record<string, string> = {
  waiting: 'Waiting',
  active: 'Active',
  completed: 'Completed',
}

onMounted(async () => {
  if (sessionUuid.value) {
    try {
      await historyStore.getSession(sessionUuid.value)

      if (!session.value) {
        await router.push({ name: 'History' })
        return
      }
    } catch (onMountedError) {
      await router.push({ name: 'History' })
    }
  }
})

onBeforeUnmount(() => {
  historyStore.clearSession()
})

const goBack = async (): Promise<void> => {
  await router.push({ name: 'History' })
}

const copyToClipboard = (text: string): void => {
  navigator.clipboard.writeText(text)
}

const isOptionSelected = (questionUuid: string, optionUuid: string): boolean => {
  if (!session.value) return false
  const answer = session.value.answers.find((a) => a.question_uuid === questionUuid)
  return answer?.selected_options.some((o) => o.uuid === optionUuid) ?? false
}

const isOptionCorrect = (questionUuid: string, optionUuid: string): boolean | undefined => {
  if (!session.value) return undefined
  const answer = session.value.answers.find((a) => a.question_uuid === questionUuid)
  const option = answer?.selected_options.find((o) => o.uuid === optionUuid)
  return option?.is_correct
}

const getOptionClass = (questionUuid: string, optionUuid: string): string => {
  const selected = isOptionSelected(questionUuid, optionUuid)
  if (!selected) return ''

  const correct = isOptionCorrect(questionUuid, optionUuid)
  return correct ? 'is-correct-selected' : 'is-incorrect-selected'
}
</script>

<template>
  <div class="view-layout">
    <header class="header">
      <div class="header-content">
        <AppButton @click="goBack">
          <span>Back to history</span>
        </AppButton>
      </div>
    </header>

    <main class="main" v-if="isLoading && !session">
      <div class="empty-state">
        <Icon icon="mdi:loading" class="spin-icon empty-icon" />
        <p class="empty-text">Loading</p>
      </div>
    </main>

    <main class="main" v-else-if="session">
      <div class="session-content-wrapper">
        <AppListCard>
          <template v-slot:icon>
            <Icon icon="mdi:timer-play-outline" />
          </template>

          <template v-slot:content>
            <div class="hero-top">
              <h1 class="hero-title">{{ session.title }}</h1>
              <AppBadge :class="`badge-${session.status}`">
                {{ sessionStatusLabels[session.status] }}
              </AppBadge>
            </div>

            <p class="hero-description">{{ session.description }}</p>

            <div class="hero-bottom">
              <span class="meta-item">
                <Icon icon="mdi:timer-outline" />
                {{ formatDuration(session.time_seconds) }}
              </span>

              <span class="meta-item" v-if="session.status !== 'waiting'">
                <Icon icon="mdi:help-circle-outline" />
                {{ session.total_questions }} questions
              </span>

              <span class="meta-item" v-if="session.status === 'completed'">
                <Icon icon="mdi:star-outline" />
                Score: {{ session.score }} / {{ session.total_score }}
              </span>

              <div class="meta-item" v-if="session.quiz_uuid">
                <Icon icon="mdi:book-open-variant-outline" />

                <div class="item-id" @click="copyToClipboard(session.quiz_uuid)">
                  {{ session.quiz_uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>

              <div class="meta-item" v-if="session.uuid">
                <Icon icon="mdi:identifier" />
                <div
                  class="item-id"
                  @click="copyToClipboard(session.uuid)"
                  title="Copy session uuid"
                >
                  {{ session.uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>
            </div>
          </template>
        </AppListCard>

        <div class="empty-state-small" v-if="session.status === 'waiting'">
          <Icon icon="mdi:timer-sand" class="empty-icon-small" />
          <p>This session is waiting to start. Questions will appear once active.</p>
        </div>

        <div class="questions-list" v-if="session.status !== 'waiting'">
          <div v-if="session.questions.length === 0" class="empty-state-small">
            <Icon icon="mdi:help-circle-outline" class="empty-icon-small" />
            <p>This session has no questions</p>
          </div>

          <AppListCard v-for="question in session.questions" :key="question.uuid">
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
                  :class="['option-item', getOptionClass(question.uuid, option.uuid)]"
                >
                  <template v-slot:icon>
                    <Icon
                      v-if="
                        isOptionSelected(question.uuid, option.uuid) &&
                        isOptionCorrect(question.uuid, option.uuid)
                      "
                      icon="mdi:check-circle"
                      class="option-icon correct"
                    />
                    <Icon
                      v-else-if="
                        isOptionSelected(question.uuid, option.uuid) &&
                        isOptionCorrect(question.uuid, option.uuid) === false
                      "
                      icon="mdi:close-circle"
                      class="option-icon incorrect"
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
</template>

<style scoped>
.view-layout {
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

.main {
  display: flex;
  flex-direction: column;
}
.session-content-wrapper {
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
.option-item.is-correct-selected {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.05);
}
.option-item.is-correct-selected:hover {
  border-color: #10b981 !important;
  box-shadow:
    0 0 1px 1px #10b981,
    0 0 1px 3px rgba(16, 185, 129, 0.5) !important;
}
.option-item.is-incorrect-selected {
  border-color: #ef4444;
  background-color: rgba(239, 68, 68, 0.05);
}
.option-item.is-incorrect-selected:hover {
  border-color: #ef4444 !important;
  box-shadow:
    0 0 1px 1px #ef4444,
    0 0 1px 3px rgba(239, 68, 68, 0.5) !important;
}
.option-icon {
  font-size: 1.25rem;
}
.option-icon.correct {
  color: #10b981;
}
.option-icon.incorrect {
  color: #ef4444;
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
</style>

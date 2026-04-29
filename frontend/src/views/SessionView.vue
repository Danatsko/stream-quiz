<script setup lang="ts">
import { onMounted, onBeforeUnmount, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth'
import useRoomsStore from '@/stores/rooms'
import AppButton from '@/components/AppButton.vue'
import AppModal from '@/components/AppModal.vue'
import AppBadge from '@/components/AppBadge.vue'
import AppListCard from '@/components/AppListCard.vue'
import { formatDateTime, formatDuration } from '@/utils/formatters'
import type {
  SessionMemberBase,
  SessionQuestionBase,
  SessionQuestionOptionBase,
} from '@/types/rooms'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const roomsStore = useRoomsStore()

const isDeleteSessionDialogOpen = ref(false)
const activeTab = ref('Questions')
const expandedMembers = ref<Set<string>>(new Set())

const roomUuid = computed(() => route.params.room_uuid as string)
const sessionUuid = computed(() => route.params.uuid as string)
const session = computed(() => roomsStore.session)
const isLoading = computed(() => roomsStore.isLoading)

const currentUserUuid = computed((): string | null => {
  return authStore.user === null ? null : authStore.user.uuid
})

const sessionStatusLabels: Record<string, string> = {
  waiting: 'Waiting',
  active: 'Active',
  completed: 'Completed',
}

onMounted(async () => {
  if (sessionUuid.value) {
    try {
      await roomsStore.getSession(roomUuid.value, sessionUuid.value)

      if (!session.value) {
        await router.push({ name: 'Room', params: { uuid: roomUuid.value } })
        return
      }
    } catch (onMountedError) {
      await router.push({ name: 'Room', params: { uuid: roomUuid.value } })
    }
  }
})

onBeforeUnmount(() => {
  roomsStore.clearSession()
})

const goBack = async (): Promise<void> => {
  await router.push({ name: 'Room', params: { uuid: roomUuid.value } })
}

const goToEdit = async (): Promise<void> => {
  if (!session.value?.uuid || session.value?.status !== 'waiting') {
    return
  }

  await router.push({
    name: 'SessionEdit',
    params: {
      room_uuid: roomUuid.value,
      uuid: sessionUuid.value,
    },
  })
}

const startSession = async (): Promise<void> => {
  if (!session.value?.uuid) return
  try {
    await roomsStore.startSession(roomUuid.value, session.value.uuid)
    await roomsStore.getSession(roomUuid.value, session.value.uuid)
  } catch (error) {}
}

const copyToClipboard = (text: string): void => {
  navigator.clipboard.writeText(text)
}

const openDeleteSessionDialog = (): void => {
  isDeleteSessionDialogOpen.value = true
}

const closeDeleteSessionDialog = (): void => {
  isDeleteSessionDialogOpen.value = false
}

const confirmDeleteSession = async (): Promise<void> => {
  if (!session.value?.uuid) {
    return
  }

  try {
    await roomsStore.deleteSession(roomUuid.value, session.value.uuid)
    closeDeleteSessionDialog()
    await router.push({ name: 'Room', params: { uuid: roomUuid.value } })
  } catch (error) {}
}

const isOptionSelected = (
  member: SessionMemberBase,
  questionUuid: string,
  optionUuid: string,
): boolean => {
  const answer = member.answers.find((a) => a.question_uuid === questionUuid)
  return answer?.selected_option_uuids.includes(optionUuid) ?? false
}

const toggleMemberExpansion = (uuid: string): void => {
  if (expandedMembers.value.has(uuid)) {
    expandedMembers.value.delete(uuid)
  } else {
    expandedMembers.value.add(uuid)
  }
}

const getMemberUUID = (member: SessionMemberBase, index: string | number): string => {
  return member.user_uuid || `anon-${index}`
}

const getMemberQuestionScore = (member: SessionMemberBase, questionUuid: string): number => {
  const answer = member.answers.find((a) => a.question_uuid === questionUuid)

  return answer?.score ?? 0
}

const getMemberOptionClass = (
  member: SessionMemberBase,
  questionUuid: string,
  option: SessionQuestionOptionBase,
): string => {
  const selected = isOptionSelected(member, questionUuid, option.uuid)

  if (selected && option.is_correct) {
    return 'is-correct-selected'
  }
  if (selected && !option.is_correct) {
    return 'is-incorrect-selected'
  }
  if (!selected && option.is_correct) {
    return 'is-correct-unselected'
  }

  return ''
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <AppButton @click="goBack" title="Back to room" aria-label="Back to room">
          <Icon icon="mdi:chevron-left" />
        </AppButton>

        <div class="header-actions" v-if="session">
          <template v-if="session.status === 'waiting'">
            <AppButton @click="startSession" title="Start session" aria-label="Start session">
              Start session
            </AppButton>
            <AppButton @click="goToEdit" title="Edit" aria-label="Edit">
              <Icon icon="mdi:edit-outline" />
            </AppButton>
            <AppButton
              class="btn-delete"
              @click="openDeleteSessionDialog"
              title="Delete"
              aria-label="Delete"
            >
              <Icon icon="mdi:delete-outline" />
            </AppButton>
          </template>
        </div>
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

              <span class="meta-item" v-if="session.status !== 'waiting'">
                <Icon icon="mdi:account-group-outline" />
                {{ session.total_members }} members
              </span>

              <div class="meta-item" v-if="session.quiz_uuid">
                <Icon icon="mdi:book-open-variant-outline" />

                <div class="item-id" @click="copyToClipboard(session.uuid)" title="Copy UUID">
                  {{ session.quiz_uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>

              <span class="meta-item" v-if="session.created_at">
                <Icon icon="mdi:calendar-plus" />
                {{ formatDateTime(session.created_at) }}
              </span>

              <span class="meta-item" v-if="session.updated_at">
                <Icon icon="mdi:calendar-edit" />
                {{ formatDateTime(session.updated_at) }}
              </span>

              <div class="meta-item" v-if="session.uuid">
                <Icon icon="mdi:identifier" />
                <div class="item-id" @click="copyToClipboard(session.uuid)" title="Copy UUID">
                  {{ session.uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>
            </div>
          </template>
        </AppListCard>

        <div class="main-nav" v-if="session.status !== 'waiting'">
          <div class="main-nav-tab">
            <AppButton
              class="tab-btn"
              :class="{ active: activeTab === 'Questions' }"
              @click="activeTab = 'Questions'"
              title="Questions"
              aria-label="Questions"
            >
              Questions
            </AppButton>
            <AppButton
              v-if="session.status !== 'waiting'"
              class="tab-btn"
              :class="{ active: activeTab === 'Members' }"
              @click="activeTab = 'Members'"
              title="Members"
              aria-label="Members"
            >
              Members
            </AppButton>
          </div>
        </div>

        <div class="empty-state-small" v-if="session.status === 'waiting'">
          <Icon icon="mdi:timer-sand" class="empty-icon-small" />
          <p>This session is waiting to start</p>
          <p>Questions will appear once active</p>
        </div>

        <div
          class="questions-list"
          v-if="activeTab === 'Questions' && session.status !== 'waiting'"
        >
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

        <div class="members-list" v-if="activeTab === 'Members' && session.status !== 'waiting'">
          <div v-if="session.members.length === 0" class="empty-state-small">
            <Icon icon="mdi:account-group-outline" class="empty-icon-small" />
            <p>No members participated in this session</p>
          </div>

          <div
            class="member-card-wrapper"
            v-for="(member, index) in session.members"
            :key="getMemberUUID(member, index)"
          >
            <AppListCard>
              <template v-slot:icon>
                <Icon icon="mdi:account-outline" />
              </template>

              <template v-slot:content>
                <div
                  class="member-header"
                  :class="{ 'is-expanded': expandedMembers.has(getMemberUUID(member, index)) }"
                  @click="toggleMemberExpansion(getMemberUUID(member, index))"
                >
                  <div class="member-header-left">
                    <div class="member-info">
                      <h3 class="member-title">{{ member.username }}</h3>

                      <div class="member-uuid-text" v-if="member.user_uuid">
                        <Icon icon="mdi:identifier" />
                        <div
                          class="item-id"
                          @click="copyToClipboard(member.user_uuid)"
                          title="Copy UUID"
                        >
                          {{ member.user_uuid }}
                          <Icon icon="mdi:content-copy" class="copy-icon" />
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="member-header-right">
                    <AppBadge>Score: {{ member.score }} / {{ session.total_score }}</AppBadge>
                    <Icon
                      :icon="
                        expandedMembers.has(getMemberUUID(member, index))
                          ? 'mdi:chevron-up'
                          : 'mdi:chevron-down'
                      "
                      class="expand-icon"
                    />
                  </div>
                </div>

                <div
                  class="member-questions"
                  v-show="expandedMembers.has(getMemberUUID(member, index))"
                >
                  <div
                    class="member-question-item"
                    v-for="question in session.questions"
                    :key="question.uuid"
                  >
                    <div class="question-header">
                      <div class="question-title-wrapper">
                        <h3 class="question-text">{{ question.text }}</h3>
                      </div>
                      <AppBadge>
                        {{ question.is_multiple_answers ? 'Multiple choice' : 'Single choice' }}
                      </AppBadge>
                      <AppBadge>
                        Score: {{ getMemberQuestionScore(member, question.uuid) }}
                      </AppBadge>
                    </div>

                    <div class="options-list">
                      <AppListCard
                        v-for="option in question.options"
                        :key="option.uuid"
                        :class="[
                          'option-item',
                          getMemberOptionClass(member, question.uuid, option),
                        ]"
                      >
                        <template v-slot:icon>
                          <Icon
                            v-if="
                              option.is_correct &&
                              isOptionSelected(member, question.uuid, option.uuid)
                            "
                            icon="mdi:check-circle"
                            class="option-icon correct"
                          />
                          <Icon
                            v-else-if="
                              !option.is_correct &&
                              isOptionSelected(member, question.uuid, option.uuid)
                            "
                            icon="mdi:close-circle"
                            class="option-icon incorrect"
                          />
                          <Icon
                            v-else-if="
                              option.is_correct &&
                              !isOptionSelected(member, question.uuid, option.uuid)
                            "
                            icon="mdi:check-circle-outline"
                            class="option-icon missed"
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
                  </div>
                </div>
              </template>
            </AppListCard>
          </div>
        </div>
      </div>
    </main>
  </div>

  <AppModal :is-open="isDeleteSessionDialogOpen" @close="closeDeleteSessionDialog">
    <template v-slot:header>
      <h1 class="modal-header-title">Delete session</h1>
    </template>

    <template v-slot:body>
      <p class="modal-text">Are you sure you want to delete this session?</p>
      <p class="modal-text">This action cannot be undone</p>
    </template>

    <template v-slot:footer>
      <AppButton @click="closeDeleteSessionDialog" title="Cancel" aria-label="Cancel"
        >Cancel</AppButton
      >
      <AppButton
        class="btn-delete"
        @click="confirmDeleteSession"
        :disabled="roomsStore.isLoading"
        title="Delete"
        aria-label="Delete"
      >
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

.main-nav {
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

.questions-list,
.members-list {
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

.member-card-wrapper {
  display: flex;
  flex-direction: column;
}
.member-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.2s;
}
.member-header:hover {
  opacity: 0.8;
}
.member-header.is-expanded {
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 1rem;
}
.member-header-left {
  display: flex;
  align-items: center;
}
.member-header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.expand-icon {
  font-size: 1.5rem;
  color: var(--color-border);
}
.member-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
}

.member-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.1rem;
}

.member-uuid-text {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  color: var(--color-text-secondary);
}

.member-question-item {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.option-item.is-correct-selected {
  border-color: #10b981;
  background-color: rgba(16, 185, 129, 0.05);
}
.option-item.is-correct-selected:hover {
  border-color: #10b981 !important;
  box-shadow:
    0 0 1px 1px #10b981,
    0 0 10px 1px rgba(16, 185, 129, 0.5) !important;
}
.option-item.is-incorrect-selected {
  border-color: #ef4444;
  background-color: rgba(239, 68, 68, 0.05);
}
.option-item.is-incorrect-selected:hover {
  border-color: #ef4444 !important;
  box-shadow:
    0 0 1px 1px #ef4444,
    0 0 10px 1px rgba(239, 68, 68, 0.5) !important;
}
.option-item.is-correct-unselected {
  border-color: rgba(16, 185, 129, 0.5);
  border-style: dashed;
}
.option-item.is-correct-unselected:hover {
  border-color: rgba(16, 185, 129, 0.8) !important;
  box-shadow:
    0 0 1px 1px rgba(16, 185, 129, 0.5),
    0 0 10px 1px rgba(16, 185, 129, 0.2) !important;
}
.option-icon.incorrect {
  color: #ef4444;
}
.option-icon.missed {
  color: rgba(16, 185, 129, 0.8);
}

.member-questions {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
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

<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import { computed, onMounted, onBeforeUnmount } from 'vue'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth'
import { useRouter } from 'vue-router'
import AppAsyncList from '@/components/AppAsyncList.vue'
import AppListCard from '@/components/AppListCard.vue'
import useHistoryStore from '@/stores/history'
import { formatDuration } from '@/utils/formatters'
import AppBadge from '@/components/AppBadge.vue'

const sessionStatusLabels: Record<string, string> = {
  completed: 'Completed',
}

const authStore = useAuthStore()
const historyStore = useHistoryStore()
const router = useRouter()

const currentUserUuid = computed((): string | null => {
  return authStore.user === null ? null : authStore.user.uuid
})

const copyToClipboard = (text: string): void => {
  navigator.clipboard.writeText(text)
}

const goToSession = async (uuid: string): Promise<void> => {
  await router.push({
    name: 'HistorySession',
    params: {
      uuid: uuid,
    },
  })
}

onMounted(async () => {
  await historyStore.getSessions()
})

onBeforeUnmount(() => {
  historyStore.clearSessions()
})
</script>

<template>
  <div class="layout">
    <main class="main">
      <AppAsyncList
        :items="historyStore.sessions"
        :is-loading="historyStore.isLoading"
        empty-icon="mdi:timer-play-outline"
        empty-title="There are no sessions"
        empty-text=" "
        @load-more="historyStore.getSessions"
      >
        <AppListCard v-for="session in historyStore.sessions" :key="session.uuid">
          <template v-slot:icon>
            <Icon icon="mdi:timer-play-outline" />
          </template>

          <template v-slot:content>
            <div class="info-top">
              <h3 class="room-title">{{ session.title }}</h3>
              <AppBadge :class="`badge-${session.status}`">
                {{ sessionStatusLabels[session.status] }}
              </AppBadge>
            </div>

            <p class="room-description">{{ session.description }}</p>
            <div class="info-bottom">
              <span class="meta-item">
                <Icon icon="mdi:timer-outline" />
                {{ formatDuration(session.time_seconds) }}
              </span>

              <div class="meta-item" v-if="session.quiz_uuid">
                <Icon icon="mdi:book-open-variant-outline" />

                <div class="room-id" @click="copyToClipboard(session.quiz_uuid)" title="Copy UUID">
                  {{ session.quiz_uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>

              <div class="meta-item" v-if="session.uuid">
                <Icon icon="mdi:identifier" />

                <div class="room-id" @click="copyToClipboard(session.uuid)" title="Copy UUID">
                  {{ session.uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>
            </div>
          </template>

          <template v-slot:actions>
            <AppButton @click="goToSession(session.uuid)" title="View" aria-label="View">
              <Icon icon="mdi:eye-outline" />
            </AppButton>
          </template>
        </AppListCard>
      </AppAsyncList>
    </main>
  </div>
</template>

<style scoped>
.layout {
  height: 100%;
  width: 90vw;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
  padding-bottom: 1rem;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
  padding-right: 1rem;
  padding-top: 1.25rem;
}

.info-top {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  max-width: 100%;
}
.room-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin: 0;
  word-break: break-all;
  overflow-wrap: anywhere;
  hyphens: auto;
  min-width: 0;
  max-width: 100%;
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
.room-id {
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
.room-id:hover {
  color: var(--color-text);
}
.copy-icon {
  font-size: 0.9rem;
}
.room-description {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
.info-bottom {
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
</style>

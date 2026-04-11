<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'
import { useInfiniteScroll } from '@vueuse/core'

const props = defineProps<{
  items: any[]
  isLoading: boolean
  emptyIcon?: string
  emptyTitle?: string
  emptyText?: string
}>()

const emit = defineEmits<{
  (e: 'loadMore'): void
}>()

const listRef = ref<HTMLElement | null>(null)

useInfiniteScroll(
  listRef,
  () => {
    if (!props.isLoading) {
      emit('loadMore')
    }
  },
  { distance: 50 },
)
</script>

<template>
  <div class="async-list-container" ref="listRef">
    <div v-if="isLoading && items.length === 0" class="empty-state">
      <Icon icon="mdi:loading" class="spin-icon empty-icon" />
      <p>Loading</p>
    </div>

    <div v-else-if="!isLoading && items.length === 0" class="empty-state">
      <Icon :icon="emptyIcon || 'mdi:database-remove-outline'" class="empty-icon" />
      <h1 class="empty-title">{{ emptyTitle || 'No items found' }}</h1>
      <p class="empty-text">{{ emptyText || 'Adjust your filters or create a new item.' }}</p>
    </div>

    <template v-else>
      <div class="items-wrapper">
        <slot></slot>
      </div>

      <div v-if="isLoading" class="loading-indicator">
        <Icon icon="mdi:loading" class="spin-icon" />
        Loading
      </div>
    </template>
  </div>
</template>

<style scoped>
.async-list-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  min-height: 0;
  padding: 0.25rem 0.5rem 0.25rem 0.5rem;
  scrollbar-gutter: stable;
}
.async-list-container::-webkit-scrollbar {
  width: 8px;
  cursor: pointer;
}
.async-list-container::-webkit-scrollbar-track {
  background: transparent;
}
.async-list-container::-webkit-scrollbar-thumb {
  background-color: var(--color-border);
  border-radius: 10px;
}
.items-wrapper {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
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
}
.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}
.empty-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}
.empty-text {
  margin: 0 0 1rem 0;
  font-size: 0.95rem;
  color: var(--color-text-secondary);
}
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  font-size: 0.9rem;
  width: 100%;
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

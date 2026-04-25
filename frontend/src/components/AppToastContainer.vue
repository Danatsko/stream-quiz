<script setup lang="ts">
import { Icon } from '@iconify/vue'
import useNotificationsStore from '@/stores/notifications'

const notificationsStore = useNotificationsStore()
</script>

<template>
  <div class="toast-container">
    <TransitionGroup name="toast">
      <div
        v-for="notification in notificationsStore.notifications"
        :key="notification.id"
        class="toast-item"
        :class="`toast-${notification.type}`"
      >
        <Icon
          v-if="notification.type === 'error'"
          icon="mdi:alert-circle-outline"
          class="toast-icon"
        />
        <Icon
          v-else-if="notification.type === 'success'"
          icon="mdi:check-circle-outline"
          class="toast-icon"
        />
        <Icon v-else icon="mdi:information-outline" class="toast-icon" />

        <span class="toast-message">{{ notification.message }}</span>

        <button class="toast-close" @click="notificationsStore.removeNotification(notification.id)">
          <Icon icon="mdi:close" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  z-index: 10000;
  pointer-events: none;
}

.toast-item {
  pointer-events: auto;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  border-radius: 12px;
  background-color: var(--color-background-secondary);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  min-width: 300px;
  max-width: 400px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
}

.toast-error {
  border-left: 4px solid #ef4444;
}

.toast-success {
  border-left: 4px solid #10b981;
}

.toast-info {
  border-left: 4px solid var(--color-primary);
}

.toast-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.toast-error .toast-icon {
  color: #ef4444;
}

.toast-success .toast-icon {
  color: #10b981;
}

.toast-info .toast-icon {
  color: var(--color-primary);
}

.toast-message {
  font-size: 0.95rem;
  line-height: 1.4;
  flex-grow: 1;
  word-break: break-word;
}

.toast-close {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 0.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  transition: color 0.2s;
}

.toast-close:hover {
  color: var(--color-text);
}

.toast-enter-active,
.toast-leave-active,
.toast-move {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.toast-leave-active {
  position: absolute;
}
</style>

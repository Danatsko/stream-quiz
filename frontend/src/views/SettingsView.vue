<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Icon } from '@iconify/vue'
import useAuthStore from '@/stores/auth'
import AppButton from '@/components/AppButton.vue'
import AppListCard from '@/components/AppListCard.vue'

const authStore = useAuthStore()
const router = useRouter()

const user = computed(() => authStore.user)

const handleLogout = async (): Promise<void> => {
  try {
    await authStore.logout()
    await router.push({ name: 'Home' })
  } catch (error) {}
}

const copyToClipboard = (text: string): void => {
  navigator.clipboard.writeText(text)
}
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <div class="header-actions">
          <AppButton class="btn-logout" @click="handleLogout" :disabled="authStore.isLoading">
            <span v-if="authStore.isLoading">Processing</span>
            <Icon v-else icon="mdi:logout" />
          </AppButton>
        </div>
      </div>
    </header>

    <main class="main" v-if="user">
      <div class="settings-content-wrapper">
        <AppListCard>
          <template v-slot:icon>
            <Icon icon="mdi:account-circle-outline" />
          </template>

          <template v-slot:content>
            <div class="info-top">
              <h3 class="item-title">Account information</h3>
            </div>

            <div class="info-bottom">
              <span class="meta-item">
                <Icon icon="mdi:account-outline" />
                <span class="meta-value">{{ user.username }}</span>
              </span>

              <span class="meta-item">
                <Icon icon="mdi:email-outline" />
                <span class="meta-value">{{ user.email }}</span>
              </span>

              <div class="meta-item" v-if="user.uuid">
                <Icon icon="mdi:identifier" />
                <div class="item-id" @click="copyToClipboard(user.uuid)" title="Copy uuid">
                  {{ user.uuid }}
                  <Icon icon="mdi:content-copy" class="copy-icon" />
                </div>
              </div>
            </div>
          </template>
        </AppListCard>
      </div>
    </main>
  </div>
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
  justify-content: flex-end;
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
.settings-content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  padding: 0.25rem 1rem 0.25rem 0.5rem;
}

.info-top {
  display: flex;
  align-items: flex-start;
  gap: 0.8rem;
  max-width: 100%;
  margin-bottom: 0.5rem;
}
.item-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
  word-break: break-all;
  overflow-wrap: anywhere;
}

.info-bottom {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}
.meta-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.meta-value {
  color: var(--color-text-secondary);
  word-break: break-all;
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

.btn-logout {
  color: red;
  border-color: red;
  background-color: color-mix(in srgb, red 10%, black);
}
.btn-logout:hover {
  background-color: color-mix(in srgb, red 20%, black);
  border-color: red;
  box-shadow:
    0 0 1px 1px red,
    0 0 1px 3px color-mix(in srgb, red 50%, transparent);
}
</style>

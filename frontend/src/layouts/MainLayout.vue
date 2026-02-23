<script setup lang="ts">
import AppLogo from '@/components/AppLogo.vue'
import { Icon } from '@iconify/vue'

const navLinks = [
  { label: 'Take', pathName: 'Take', icon: 'mdi:play-outline' },
  { label: 'Quizzes', pathName: 'Quizzes', icon: 'mdi:quiz-outline' },
  { label: 'Rooms', pathName: 'Rooms', icon: 'mdi:cube-outline' },
  { label: 'History', pathName: 'History', icon: 'mdi:clock-outline' },
]
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="container header-content">
        <div class="header-left">
          <AppLogo />
        </div>

        <nav class="header-center">
          <RouterLink
            class="link-wrapper"
            v-for="link in navLinks"
            :key="link.pathName"
            :to="{ name: link.pathName }"
          >
            <Icon class="link-icon" :icon="link.icon" />
            <span class="link">{{ link.label }}</span>
          </RouterLink>
        </nav>

        <nav class="header-right">
          <RouterLink class="link-wrapper" :to="{ name: 'Settings' }">
            <Icon class="link-icon" icon="mdi:cog-outline" />
            <p class="link">Settings</p>
          </RouterLink>
        </nav>
      </div>
    </header>
    <div class="main">
      <div class="main-content">
        <RouterView />
      </div>
    </div>
  </div>
</template>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2.5rem;
}

.header {
  padding: 0.5rem 0;
  flex-shrink: 0;
}
.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}
.header-center {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: center;
  flex: 1;
}
.link-wrapper {
  color: #2a2a2a;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.3rem;
  text-decoration: none;
  font-weight: 500;
  font-size: 1rem;
  padding: 0 0.5rem;
  border-radius: 9999px;
}
.link-wrapper:hover {
  cursor: pointer;
}
.link-wrapper.router-link-active {
  cursor: default;
  pointer-events: none;
}
.link-icon {
  font-size: 1.2rem;
  z-index: 1;
}
.link-wrapper:hover .link,
.link-wrapper.router-link-active .link {
  background: var(--linear-gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight: 500;
}
.link-wrapper:hover .link-icon,
.link-wrapper.router-link-active .link-icon {
  color: var(--color-primary);
}
.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  flex: 1;
}

.main {
  border-top: 1px solid #2a2a2a;
  position: relative;
  box-sizing: border-box;
  flex-direction: column;
  display: flex;
  flex-grow: 1;
  overflow: hidden;
  min-height: 0;
}
.main-content {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: stretch;
  overflow: hidden;
  min-height: 0;
}
</style>

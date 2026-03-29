<script setup lang="ts">
import AppFooter from '@/components/AppFooter.vue'
import { Icon } from '@iconify/vue'
import AppHeader from '@/components/AppHeader.vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const navLinks = [
  { label: 'Take', pathName: 'Take', icon: 'mdi:play-outline' },
  { label: 'Quizzes', pathName: 'Quizzes', icon: 'mdi:book-open-variant-outline' },
  { label: 'Rooms', pathName: 'Rooms', icon: 'mdi:cube-outline' },
  { label: 'History', pathName: 'History', icon: 'mdi:history' },
]
</script>

<template>
  <div class="layout" :class="{ 'is-scrollable': route.meta.nativeScroll }">
    <AppHeader>
      <div class="header-slot-inner">
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
    </AppHeader>

    <div class="main">
      <div class="main-content">
        <RouterView />
      </div>
    </div>

    <AppFooter />
  </div>
</template>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout.is-scrollable {
  height: auto;
  min-height: 100vh;
}

.header-slot-inner {
  display: flex;
  width: 100%;
  justify-content: space-between;
}
.header-center {
  display: flex;
  gap: 1rem;
  align-items: center;
  justify-content: center;
  flex: 1;
}
.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
}
.link-wrapper {
  color: var(--color-border);
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

.main {
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
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

.layout.is-scrollable .main,
.layout.is-scrollable .main-content {
  overflow: visible;
}
</style>

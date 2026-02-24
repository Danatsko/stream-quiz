<script setup lang="ts">
import homeVector from '@/assets/homeVector.svg'
import AppLogo from '@/components/AppLogo.vue'
</script>

<template>
  <div class="layout">
    <header class="header">
      <div class="header-content">
        <AppLogo />
      </div>
    </header>

    <main class="main">
      <div class="main-left">
        <div class="main-left-glow main-left-glow-left"></div>
        <div class="main-left-glow main-left-glow-right"></div>
        <img :src="homeVector" class="main-left-vector main-left-vector-top" alt="" />
        <div class="main-left-content">
          <AppLogo />
        </div>
        <img :src="homeVector" class="main-left-vector main-left-vector-bottom" alt="" />
      </div>
      <div class="main-right">
        <div class="main-right-content">
          <RouterView />
        </div>
      </div>
    </main>

    <footer class="footer">
      <div class="footer-content">
        <p class="footer-copyright">Copyright © 2026 StreamQuiz</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.layout {
  height: 100vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  padding: 0.5rem 0;
  flex-shrink: 0;
}
.header-content {
  margin: 0 auto;
  padding: 0 2.5rem;
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: row;
  overflow: hidden;
  border-top: 1px solid #2a2a2a;
  border-bottom: 1px solid #2a2a2a;
}

.main-left {
  position: relative;
  border-right: 1px solid #2a2a2a;
  padding: 0.5rem 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60vw;
}
.main-left-content {
  position: relative;
  z-index: 10;
  display: flex;
  gap: 1rem;
}
.main-left-content :deep(.logo-text) {
  font-size: 5rem;
}
.main-left-vector {
  position: absolute;
  left: 0;
  width: 100%;
  height: 50%;
  object-fit: cover;
  z-index: 0;
  pointer-events: none;
  user-select: none;
}
.main-left-vector-top {
  top: 0;
}
.main-left-vector-bottom {
  bottom: 0;
  transform: rotate(180deg);
}
.main-left-glow {
  position: absolute;
  width: 35vw;
  max-width: 350px;
  aspect-ratio: 1 / 1;
  border-radius: 50%;
  filter: blur(150px);
  z-index: 0;
  opacity: 0.5;
  pointer-events: none;
  user-select: none;
}
.main-left-glow-left {
  left: -15%;
  background-color: var(--color-primary);
}
.main-left-glow-right {
  right: -15%;
  background-color: var(--color-secondary);
}

.main-right {
  background: white;
  border-left: 1px solid #2a2a2a;
  position: relative;
  padding: 0.5rem 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40vw;
}
.main-right-content {
  display: flex;
  gap: 1rem;
  justify-content: center;
  align-items: center;
}

.footer {
  padding: 0.5rem 0;
  flex-shrink: 0;
}
.footer-content {
  display: flex;
  justify-content: center;
}
.footer-copyright {
  max-width: 300px;
  font-size: 0.75rem;
  font-weight: 300;
}
</style>

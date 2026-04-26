<script setup lang="ts">
import AppButton from '@/components/AppButton.vue'
import AppFooter from '@/components/AppFooter.vue'
import homeVector from '@/assets/homeVector.svg'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/AppHeader.vue'

const router = useRouter()

const goToLogin = async (): Promise<void> => {
  await router.push({ name: 'Login' })
}
const goToRegistration = async (): Promise<void> => {
  await router.push({ name: 'Registration' })
}
</script>

<template>
  <div class="layout">
    <AppHeader>
      <nav class="header-nav-actions">
        <AppButton @click="goToLogin" title="Sign in" aria-label="Sign in"> Sign in </AppButton>
        <AppButton
          class="header-btn-signup"
          @click="goToRegistration"
          title="Sign up"
          aria-label="Sign up"
        >
          Sign up
        </AppButton>
      </nav>
    </AppHeader>

    <main class="main">
      <div class="main-glow main-glow-left"></div>
      <div class="main-glow main-glow-right"></div>
      <img :src="homeVector" class="main-vector main-vector-top" alt="" />
      <div class="container main-content">
        <div class="main-text-block">
          <h1 class="main-title">Learn & Quiz</h1>
          <p class="main-subtitle">The ultimate quiz platform for students and teachers.</p>
          <p class="main-description">
            Join thousands of students and teachers on the ultimate quiz platform. Test your
            knowledge and compete with peers.
          </p>
        </div>
      </div>
      <img :src="homeVector" class="main-vector main-vector-bottom" alt="" />
    </main>

    <AppFooter />
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 2.5rem;
}

.header-nav-actions {
  display: flex;
  gap: 1rem;
}
.header-btn-signup {
  background: var(--linear-gradient-primary);
}

.main {
  position: relative;
  border-top: 1px solid var(--color-border);
  border-bottom: 1px solid var(--color-border);
  padding: 0.5rem 0;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-grow: 1;
}
.main-glow {
  position: absolute;
  width: 50vw;
  max-width: 500px;
  aspect-ratio: 1 / 1;
  border-radius: 50%;
  filter: blur(150px);
  z-index: 0;
  opacity: 0.5;
  pointer-events: none;
  user-select: none;
}
.main-glow-left {
  left: -15%;
  background-color: var(--color-primary);
}
.main-glow-right {
  right: -15%;
  background-color: var(--color-secondary);
}
.main-vector {
  position: absolute;
  left: 0;
  width: 100%;
  height: 50%;
  object-fit: cover;
  z-index: 0;
  pointer-events: none;
  user-select: none;
}
.main-vector-top {
  top: 0;
}
.main-vector-bottom {
  bottom: 0;
  transform: rotate(180deg);
}
.main-content {
  position: relative;
  z-index: 10;
  display: flex;
  gap: 1rem;
}
.main-text-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}
.main-title {
  font-size: 3rem;
  font-weight: 900;
  margin: 0.5rem 0;
}
.main-subtitle {
  font-size: 1.5rem;
  font-weight: 500;
  margin: 0.5rem 0;
  color: var(--color-text-secondary);
}
.main-description {
  max-width: 500px;
  font-size: 1rem;
  font-weight: 300;
  margin: 0.5rem 0;
  color: var(--color-text-secondary);
}
</style>

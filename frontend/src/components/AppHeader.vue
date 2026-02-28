<script setup lang="ts">
import AppLogo from '@/components/AppLogo.vue'
</script>

<template>
  <header class="header">
    <div class="header-content">
      <div class="header-logo-wrapper">
        <AppLogo />
      </div>
      <div class="header-slot-wrapper">
        <slot></slot>
      </div>
    </div>
  </header>
</template>

<style scoped>
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
.header-logo-wrapper {
  display: flex;
  align-items: center;
}
.header-slot-wrapper {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}
</style>

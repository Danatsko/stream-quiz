<script setup lang="ts"></script>

<template>
  <span class="badge">
    <slot></slot>
  </span>
</template>

<style scoped>
.badge {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.5rem;
  border-radius: 9999px;
  white-space: nowrap;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  background-color: var(--color-background-secondary);
  border: 1px solid color-mix(in srgb, var(--color-text-secondary) 30%, transparent);
  color: var(--color-text-secondary);
}
</style>

<script setup lang="ts"></script>

<template>
  <button class="btn">
    <slot></slot>
  </button>
</template>

<style scoped>
.btn {
  background: var(--color-background);
  display: flex;
  align-items: center;
  text-align: center;
  justify-content: center;
  padding: 0.75rem 1rem;
  border-radius: 9px;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  border: 1px solid var(--color-border);
  user-select: none;
  color: var(--color-text);
  transition: all 0.2s ease;
}
.btn:hover {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 10px 1px var(--color-secondary);
}
.btn:active {
  transform: scale(0.95);
}
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
</style>

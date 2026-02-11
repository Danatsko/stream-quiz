<script setup lang="ts"></script>

<template>
  <button class="btn">
    <slot></slot>
  </button>
</template>

<style scoped>
.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 9999px;
  font-weight: 500;
  font-family: inherit;
  font-size: 1rem;
  cursor: pointer;
  border: 1px solid transparent;
  user-select: none;
  transition:
    opacity 0.1s ease,
    transform 0.1s ease,
    background-color 0.1s ease;
}
.btn:hover {
  opacity: 0.9;
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

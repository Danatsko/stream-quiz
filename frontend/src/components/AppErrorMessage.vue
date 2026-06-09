<script setup lang="ts"></script>

<template>
  <small class="error-text">
    <slot></slot>
  </small>
</template>

<style scoped>
.error-text {
  color: red;
  font-size: 0.75rem;
  margin-top: 0.2rem;
  display: block;
  min-height: 1rem;
  transition: opacity 0.3s ease;
}
</style>

<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    alignItems?: string
  }>(),
  {
    alignItems: 'center',
  },
)
</script>

<template>
  <div class="data-card" :style="{ alignItems: props.alignItems }">
    <div class="card-icon-wrapper" v-if="$slots.icon">
      <slot name="icon"></slot>
    </div>

    <div class="card-info">
      <slot name="content"></slot>
    </div>

    <div class="card-actions" v-if="$slots.actions">
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<style scoped>
.data-card {
  display: flex;
  gap: 1.5rem;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1.2rem;
  transition: border-color 0.2s;
  flex-shrink: 0;
  width: 100%;
  box-sizing: border-box;
}
.data-card:hover {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 1px 3px var(--color-secondary);
}
.card-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex-shrink: 0;
  font-size: 1.5rem;
}
.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.4rem;
  min-width: 0;
}
.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  margin-left: auto;
}
</style>

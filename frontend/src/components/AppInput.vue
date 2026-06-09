<script setup lang="ts">
import AppErrorMessage from '@/components/AppErrorMessage.vue'

defineOptions({
  inheritAttrs: false,
})

withDefaults(
  defineProps<{
    modelValue: string | number | null
    id?: string
    label?: string
    type?: string
    placeholder?: string
    hasError?: boolean
    errorMessage?: string
  }>(),
  {
    type: 'text',
    placeholder: '',
    hasError: false,
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string | number): void
}>()

const handleChange = (event: Event): void => {
  const target = event.target as HTMLInputElement
  const trimmedValue = target.value.trim()

  if (target.value !== trimmedValue) {
    target.value = trimmedValue

    emit('update:modelValue', trimmedValue)
  }
}
</script>

<template>
  <div class="form-group">
    <label v-if="label" :for="id">{{ label }}</label>

    <div class="input-wrapper">
      <div class="icon-wrapper" v-if="$slots.icon">
        <slot name="icon"></slot>
      </div>

      <input
        :id="id"
        class="input"
        :class="{
          'input-error': hasError,
          'has-icon': !!$slots.icon,
        }"
        :type="type"
        :placeholder="placeholder"
        :value="modelValue"
        @input="emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @change="handleChange"
        v-bind="$attrs"
      />
    </div>

    <AppErrorMessage
      class="absolute-error"
      :style="{ visibility: hasError && errorMessage ? 'visible' : 'hidden' }"
    >
      {{ errorMessage }}
    </AppErrorMessage>
  </div>
</template>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
  position: relative;
  padding-bottom: 1.2rem;
}

label {
  font-size: 0.9rem;
  font-weight: 600;
}

.input-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
}

.icon-wrapper {
  position: absolute;
  left: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  pointer-events: none;
  z-index: 1;
  color: var(--color-text-secondary);
}

.icon-wrapper :deep(*) {
  font-size: inherit;
}

.input {
  width: 100%;
  padding: 0.75rem 1rem;
  box-sizing: border-box;
  background-color: transparent;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--color-text);
  outline: none;
  font-family: inherit;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.input.has-icon {
  padding-left: 2.5rem;
}

.input:focus {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 10px 1px var(--color-secondary);
}

.input.input-error {
  border-color: red;
}
.input.input-error:focus {
  border-color: red;
  box-shadow: 0 0 1px 1px red;
}
.absolute-error {
  position: absolute;
  bottom: 0;
  left: 0;
  margin: 0;
}
</style>

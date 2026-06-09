<script setup lang="ts">
import AppErrorMessage from '@/components/AppErrorMessage.vue'

defineOptions({
  inheritAttrs: false,
})

withDefaults(
  defineProps<{
    modelValue: string | null
    id?: string
    label?: string
    placeholder?: string
    hasError?: boolean
    errorMessage?: string
  }>(),
  {
    placeholder: '',
    hasError: false,
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

const handleChange = (event: Event): void => {
  const target = event.target as HTMLTextAreaElement
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
      <textarea
        :id="id"
        class="input textarea"
        :class="{ 'input-error': hasError }"
        :placeholder="placeholder"
        :value="modelValue || ''"
        @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
        @change="handleChange"
        rows="5"
        v-bind="$attrs"
      ></textarea>
    </div>

    <AppErrorMessage
      class="absolute-error"
      :style="{ visibility: hasError && errorMessage ? 'visible' : 'hidden' }"
    >
      {{ errorMessage || '\u00A0' }}
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

.input.textarea {
  resize: unset;
  min-height: 100px;
  line-height: 1.5;
}

.input.textarea::-webkit-scrollbar {
  width: 8px;
  cursor: pointer;
}

.input.textarea::-webkit-scrollbar-track {
  background: transparent;
  cursor: pointer;
}

.input.textarea::-webkit-scrollbar-thumb {
  background-color: var(--color-border);
  border-radius: 10px;
  cursor: pointer;
}

.absolute-error {
  position: absolute;
  bottom: 0;
  left: 0;
  margin: 0;
}
</style>

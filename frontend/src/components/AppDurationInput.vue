<script setup lang="ts">
import { ref, watch } from 'vue'
import AppErrorMessage from '@/components/AppErrorMessage.vue'

const props = withDefaults(
  defineProps<{
    modelValue: number | null
    id?: string
    label?: string
    hasError?: boolean
    errorMessage?: string
  }>(),
  {
    hasError: false,
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: number | null): void
}>()

const hours = ref('')
const minutes = ref('')
const seconds = ref('')

watch(
  () => props.modelValue,
  (newVal) => {
    if (newVal === null) {
      hours.value = ''
      minutes.value = ''
      seconds.value = ''
      return
    }

    const currentLocalSeconds =
      parseInt(hours.value || '0', 10) * 3600 +
      parseInt(minutes.value || '0', 10) * 60 +
      parseInt(seconds.value || '0', 10)

    if (newVal !== currentLocalSeconds) {
      const h = Math.floor(newVal / 3600)
      const m = Math.floor((newVal % 3600) / 60)
      const s = newVal % 60
      hours.value = h.toString().padStart(2, '0')
      minutes.value = m.toString().padStart(2, '0')
      seconds.value = s.toString().padStart(2, '0')
    }
  },
  { immediate: true },
)

const updateModelValue = (): void => {
  if (!hours.value && !minutes.value && !seconds.value) {
    emit('update:modelValue', null)
    return
  }

  const h = parseInt(hours.value || '0', 10)
  const m = parseInt(minutes.value || '0', 10)
  const s = parseInt(seconds.value || '0', 10)

  emit('update:modelValue', h * 3600 + m * 60 + s)
}

const handleInput = (type: 'h' | 'm' | 's', event: Event): void => {
  const target = event.target as HTMLInputElement
  let val = target.value.replace(/\D/g, '')

  if (type === 'h') {
    val = val.slice(0, 3)
    hours.value = val
  } else if (type === 'm') {
    val = val.slice(0, 2)

    if (parseInt(val, 10) > 59) {
      val = '59'
    }

    minutes.value = val
  } else if (type === 's') {
    val = val.slice(0, 2)

    if (parseInt(val, 10) > 59) {
      val = '59'
    }

    seconds.value = val
  }

  target.value = val

  updateModelValue()
}

const formatOnBlur = (type: 'h' | 'm' | 's'): void => {
  if (type === 'h' && hours.value) {
    hours.value = hours.value.padStart(2, '0')
  }
  if (type === 'm' && minutes.value) {
    minutes.value = minutes.value.padStart(2, '0')
  }
  if (type === 's' && seconds.value) {
    seconds.value = seconds.value.padStart(2, '0')
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

      <div
        class="duration-input-wrapper"
        :class="{
          'input-error': hasError,
          'has-icon': !!$slots.icon,
        }"
        :id="id"
      >
        <input
          class="duration-segment hours"
          type="text"
          placeholder="HH"
          :value="hours"
          @input="handleInput('h', $event)"
          @blur="formatOnBlur('h')"
        />
        <span class="separator">:</span>
        <input
          class="duration-segment"
          type="text"
          placeholder="MM"
          :value="minutes"
          @input="handleInput('m', $event)"
          @blur="formatOnBlur('m')"
        />
        <span class="separator">:</span>
        <input
          class="duration-segment"
          type="text"
          placeholder="SS"
          :value="seconds"
          @input="handleInput('s', $event)"
          @blur="formatOnBlur('s')"
        />
      </div>
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

.duration-input-wrapper {
  display: flex;
  align-items: center;
  width: max-content;
  padding: 0.75rem 1rem;
  box-sizing: border-box;
  background-color: transparent;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 1rem;
  color: var(--color-text);
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
  cursor: text;
}
.duration-input-wrapper.has-icon {
  padding-left: 2.5rem;
}
.duration-input-wrapper:focus-within {
  border-color: var(--color-primary);
  box-shadow:
    0 0 1px 1px var(--color-primary),
    0 0 10px 1px var(--color-secondary);
}
.duration-input-wrapper.input-error {
  border-color: red;
}
.duration-input-wrapper.input-error:focus-within {
  border-color: red;
  box-shadow: 0 0 1px 1px red;
}

.duration-segment {
  background: transparent;
  border: none;
  color: var(--color-text);
  font-size: 1rem;
  font-family: inherit;
  text-align: center;
  width: 3ch;
  outline: none;
  padding: 0;
}
.duration-segment.hours {
  width: 3.5ch;
}
.duration-segment::placeholder {
  color: var(--color-text-secondary);
  opacity: 0.5;
}
.separator {
  font-weight: bold;
  color: var(--color-text-secondary);
  user-select: none;
  margin: 0 0.1rem;
}

.absolute-error {
  position: absolute;
  bottom: 0;
  left: 0;
  margin: 0;
}
</style>

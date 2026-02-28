<script setup lang="ts">
import { nextTick, ref, watch } from 'vue'
import { useScrollLock, onKeyStroke } from '@vueuse/core'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const modalWindowRef = ref<HTMLElement | null>(null)
const isLocked = useScrollLock(document.body)

onKeyStroke('Escape', (e) => {
  if (props.isOpen) {
    e.preventDefault()
    emit('close')
  }
})

onKeyStroke('Tab', (e) => {
  if (!props.isOpen || !modalWindowRef.value) return

  const focusableElements = modalWindowRef.value.querySelectorAll<HTMLElement>(
    'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
  )

  if (focusableElements.length === 0) {
    e.preventDefault()
    return
  }

  const firstElement = focusableElements[0]
  const lastElement = focusableElements[focusableElements.length - 1]

  if (e.shiftKey) {
    if (document.activeElement === firstElement || document.activeElement === document.body) {
      e.preventDefault()
      lastElement.focus()
    }
  } else {
    if (document.activeElement === lastElement) {
      e.preventDefault()
      firstElement.focus()
    }
  }
})

watch(
  () => props.isOpen,
  async (newVal) => {
    isLocked.value = newVal

    if (newVal) {
      await nextTick()
      if (modalWindowRef.value) {
        const firstFocusable = modalWindowRef.value.querySelector<HTMLElement>(
          'button:not([disabled]), input:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
        )
        firstFocusable?.focus()
      }
    }
  },
)
</script>

<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay">
      <div class="modal-window" ref="modalWindowRef">
        <div class="modal-header">
          <slot name="header"></slot>
        </div>

        <div class="modal-body">
          <slot name="body"></slot>
        </div>

        <div class="modal-footer">
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}
.modal-window {
  background-color: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
  box-shadow:
    0 20px 25px -5px rgba(0, 0, 0, 0.5),
    0 10px 10px -5px rgba(0, 0, 0, 0.2);
  animation: modalFadeIn 0.2s ease-out;
}
@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.modal-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1.5rem;
}
.modal-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.modal-footer {
  padding: 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  align-items: center;
}
</style>

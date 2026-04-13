<script setup>
import { storeToRefs } from 'pinia'

import { useToastStore } from '../stores/toast'

const toastStore = useToastStore()
const { toasts } = storeToRefs(toastStore)
</script>

<template>
  <div
    class="toast-container position-fixed bottom-0 end-0 p-3 sklad-toast-stack"
    aria-live="polite"
    aria-atomic="false"
  >
    <TransitionGroup name="sklad-toast" tag="div" class="d-flex flex-column align-items-end gap-2">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast show align-items-center border-0 shadow"
        :class="t.variant === 'success' ? 'text-bg-success' : 'text-bg-danger'"
        role="alert"
      >
        <div class="d-flex w-100 align-items-center">
          <div class="toast-body py-2 small">
            {{ t.message }}
          </div>
          <button
            type="button"
            class="btn-close btn-close-white me-2 m-auto flex-shrink-0"
            aria-label="Закрыть"
            @click="toastStore.dismiss(t.id)"
          />
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.sklad-toast-stack {
  z-index: 1090;
  max-width: min(22rem, 100vw - 1.5rem);
  pointer-events: none;
}

.sklad-toast-stack :deep(.toast) {
  pointer-events: auto;
  min-width: 14rem;
}

.sklad-toast-enter-active,
.sklad-toast-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.sklad-toast-enter-from,
.sklad-toast-leave-to {
  opacity: 0;
  transform: translateX(0.75rem);
}
</style>

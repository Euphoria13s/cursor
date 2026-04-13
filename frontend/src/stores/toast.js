import { defineStore } from 'pinia'
import { ref } from 'vue'

const DEFAULT_MS = 3000

let idSeq = 0

export const useToastStore = defineStore('toast', () => {
  const toasts = ref([])

  function dismiss(id) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  /**
   * @param {string} message
   * @param {'success'|'danger'} variant
   * @param {number} durationMs — 0 = без автоскрытия
   */
  function show(message, variant = 'success', durationMs = DEFAULT_MS) {
    const id = ++idSeq
    toasts.value = [...toasts.value, { id, message, variant }]
    if (durationMs > 0) {
      setTimeout(() => dismiss(id), durationMs)
    }
    return id
  }

  function success(message, durationMs = DEFAULT_MS) {
    return show(message, 'success', durationMs)
  }

  function danger(message, durationMs = DEFAULT_MS) {
    return show(message, 'danger', durationMs)
  }

  return {
    toasts,
    show,
    success,
    danger,
    dismiss,
  }
})

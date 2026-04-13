<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPage: {
    type: Number,
    required: true,
  },
  totalPages: {
    type: Number,
    required: true,
  },
})

const emit = defineEmits(['page-change'])

/** До 7 номеров страниц вокруг текущей */
const pageNumbers = computed(() => {
  const t = props.totalPages
  const c = props.currentPage
  if (t < 1) return []
  const width = 7
  const start = Math.max(1, Math.min(c - Math.floor(width / 2), t - width + 1))
  const end = Math.min(t, start + width - 1)
  const s = Math.max(1, end - width + 1)
  const list = []
  for (let i = s; i <= end; i += 1) {
    list.push(i)
  }
  return list
})

const showPagination = computed(() => props.totalPages > 1)

function go(page) {
  if (page < 1 || page > props.totalPages || page === props.currentPage) return
  emit('page-change', page)
}
</script>

<template>
  <nav v-if="showPagination" class="mt-3" aria-label="Страницы">
    <ul class="pagination justify-content-center flex-wrap mb-0">
      <li class="page-item" :class="{ disabled: currentPage <= 1 }">
        <button
          type="button"
          class="page-link"
          :disabled="currentPage <= 1"
          @click="go(currentPage - 1)"
        >
          Назад
        </button>
      </li>
      <li
        v-for="n in pageNumbers"
        :key="n"
        class="page-item"
        :class="{ active: n === currentPage }"
      >
        <button
          type="button"
          class="page-link"
          :aria-current="n === currentPage ? 'page' : undefined"
          @click="go(n)"
        >
          {{ n }}
        </button>
      </li>
      <li class="page-item" :class="{ disabled: currentPage >= totalPages }">
        <button
          type="button"
          class="page-link"
          :disabled="currentPage >= totalPages"
          @click="go(currentPage + 1)"
        >
          Вперёд
        </button>
      </li>
    </ul>
  </nav>
</template>

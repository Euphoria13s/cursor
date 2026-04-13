<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import PaginationComponent from '../components/PaginationComponent.vue'
import { useWriteoffStore } from '../stores/writeoffs'
import { useToastStore } from '../stores/toast'
import { apiErrorMessage } from '../utils/apiErrorMessage'
import { formatDate, formatDocStatus, truncate } from '../utils/formatters'

const router = useRouter()
const store = useWriteoffStore()
const toast = useToastStore()

const filters = reactive({
  status: '',
  date_from: '',
  date_to: '',
  reason: '',
})

const currentPage = ref(1)

let reasonDebounceTimer = null

function buildParams() {
  const params = { page: currentPage.value }
  if (filters.date_from) params.writeoff_date__gte = filters.date_from
  if (filters.date_to) params.writeoff_date__lte = filters.date_to
  if (filters.status) params.status = filters.status
  const q = filters.reason.trim()
  if (q) params.search = q
  return params
}

async function load() {
  await store.fetchAll(buildParams())
}

function applyFilters() {
  currentPage.value = 1
  load()
}

function onReasonInput() {
  clearTimeout(reasonDebounceTimer)
  reasonDebounceTimer = setTimeout(() => {
    applyFilters()
  }, 300)
}

function resetFilters() {
  filters.status = ''
  filters.date_from = ''
  filters.date_to = ''
  filters.reason = ''
  clearTimeout(reasonDebounceTimer)
  currentPage.value = 1
  load()
}

function onPageChange(page) {
  if (page < 1 || page > store.totalPages) return
  currentPage.value = page
  load()
}

function rowClick(id, e) {
  if (e.target.closest('a,button')) return
  router.push({ name: 'writeoff-detail', params: { id: String(id) } })
}

function goEdit(id, e) {
  e.stopPropagation()
  router.push({ name: 'writeoff-edit', params: { id: String(id) } })
}

async function onDelete(id, e) {
  e.stopPropagation()
  if (!window.confirm('Удалить документ списания?')) return
  try {
    await store.remove(id)
    toast.success('Списание удалено')
  } catch (e) {
    toast.danger(apiErrorMessage(e, 'Не удалось удалить документ'))
  }
}

function authorLabel(row) {
  if (row.author_name && String(row.author_name).trim()) return row.author_name
  if (row.created_by != null) return `#${row.created_by}`
  return '—'
}

onMounted(() => {
  load()
})
</script>

<template>
  <div class="sklad-list-page">
    <div class="mb-3">
      <h1 class="h4 mb-1">
        Списания
      </h1>
      <p class="text-muted small mb-0">
        Документы расхода со склада
      </p>
    </div>

    <div
      class="position-relative sklad-list-fetch"
      :class="{ 'sklad-list-fetch--busy': store.loading }"
      :aria-busy="store.loading ? 'true' : undefined"
    >
      <div class="card border-0 shadow-sm rounded-3 mb-3">
        <div class="card-body py-3">
          <div class="row g-2 align-items-end flex-wrap">
            <div class="col-6 col-md-3 col-lg">
              <label class="form-label small text-muted mb-1">Дата с</label>
              <input
                v-model="filters.date_from"
                type="date"
                class="form-control"
                :disabled="store.loading"
                @change="applyFilters"
              >
            </div>
            <div class="col-6 col-md-3 col-lg">
              <label class="form-label small text-muted mb-1">Дата по</label>
              <input
                v-model="filters.date_to"
                type="date"
                class="form-control"
                :disabled="store.loading"
                @change="applyFilters"
              >
            </div>
            <div class="col-6 col-md-3 col-lg">
              <label class="form-label small text-muted mb-1">Статус</label>
              <select v-model="filters.status" class="form-select" :disabled="store.loading" @change="applyFilters">
              <option value="">
                Все
              </option>
              <option value="draft">
                Черновик
              </option>
              <option value="posted">
                Проведён
              </option>
              <option value="cancelled">
                Отменён
              </option>
              </select>
            </div>
            <div class="col-12 col-md-6 col-lg">
              <label class="form-label small text-muted mb-1">Поиск по причине / тексту</label>
              <input
                v-model="filters.reason"
                type="search"
                class="form-control"
                placeholder="Ключевые слова…"
                autocomplete="off"
                :disabled="store.loading"
                @input="onReasonInput"
              >
            </div>
            <div class="col-12 d-flex flex-wrap gap-2 justify-content-md-end ms-md-auto">
              <button type="button" class="btn btn-outline-secondary" :disabled="store.loading" @click="resetFilters">
                <i class="bi bi-x-lg me-1" aria-hidden="true" />
                Сбросить фильтры
              </button>
              <button
                type="button"
                class="btn btn-primary"
                @click="router.push({ name: 'writeoff-create' })"
              >
                <i class="bi bi-plus-lg me-1" aria-hidden="true" />
                Новое списание
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="card border-0 shadow-sm rounded-3 overflow-hidden">
        <div v-if="!store.loading && !store.items.length" class="text-center py-5 px-3">
        <i class="bi bi-arrow-up-circle display-4 text-muted" aria-hidden="true" />
        <p class="text-muted mt-2 mb-0">
          Списания не найдены.
        </p>
        </div>

        <div v-else-if="!store.loading" class="table-responsive">
        <table class="table table-hover align-middle mb-0 small">
          <thead class="table-light">
            <tr>
              <th>Номер</th>
              <th>Дата</th>
              <th>Причина</th>
              <th>Автор</th>
              <th>Статус</th>
              <th>Комментарий</th>
              <th class="text-end" style="width: 7rem">
                Действия
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in store.items"
              :key="row.id"
              class="sklad-table__row"
              role="button"
              tabindex="0"
              @click="rowClick(row.id, $event)"
              @keydown.enter="router.push({ name: 'writeoff-detail', params: { id: String(row.id) } })"
            >
              <td class="fw-medium font-monospace">
                {{ row.document_number }}
              </td>
              <td class="text-nowrap">
                {{ formatDate(row.writeoff_date) }}
              </td>
              <td>{{ truncate(row.reason, 36) }}</td>
              <td>{{ authorLabel(row) }}</td>
              <td>
                <span class="badge rounded-pill text-bg-light border">
                  {{ formatDocStatus(row.status) }}
                </span>
              </td>
              <td class="text-muted">
                {{ truncate(row.comment, 36) }}
              </td>
              <td class="text-end" @click.stop>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-primary me-1"
                  title="Редактировать"
                  @click="goEdit(row.id, $event)"
                >
                  <i class="bi bi-pencil" aria-hidden="true" />
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-danger"
                  title="Удалить"
                  @click="onDelete(row.id, $event)"
                >
                  <i class="bi bi-trash" aria-hidden="true" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        </div>
      </div>

      <div
        v-if="store.loading"
        class="sklad-list-fetch-overlay d-flex align-items-center justify-content-center rounded-3"
        aria-live="polite"
      >
        <div class="text-center py-4 px-3">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Загрузка…</span>
          </div>
          <p class="text-muted small mt-2 mb-0">
            Загрузка данных…
          </p>
        </div>
      </div>
    </div>

    <PaginationComponent
      v-if="!store.loading"
      :current-page="currentPage"
      :total-pages="store.totalPages"
      @page-change="onPageChange"
    />
  </div>
</template>

<style scoped>
.sklad-list-fetch--busy {
  min-height: 14rem;
}

.sklad-list-fetch-overlay {
  position: absolute;
  inset: 0;
  z-index: 20;
  background: rgba(255, 255, 255, 0.9);
  pointer-events: auto;
}

.sklad-table__row {
  cursor: pointer;
}
.sklad-table__row:hover {
  background-color: var(--bs-light);
}
</style>

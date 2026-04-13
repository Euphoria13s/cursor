<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import PaginationComponent from '../components/PaginationComponent.vue'
import { useCategoryStore } from '../stores/categories'
import { useToastStore } from '../stores/toast'
import { apiErrorMessage } from '../utils/apiErrorMessage'
import { formatDateTime, truncate } from '../utils/formatters'

const router = useRouter()
const store = useCategoryStore()
const toast = useToastStore()

const filters = reactive({
  search: '',
})

const currentPage = ref(1)

let searchDebounceTimer = null

function buildParams() {
  const params = { page: currentPage.value }
  const q = filters.search.trim()
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

function onSearchInput() {
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(() => {
    applyFilters()
  }, 300)
}

function resetFilters() {
  filters.search = ''
  clearTimeout(searchDebounceTimer)
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
  router.push({ name: 'category-detail', params: { id: String(id) } })
}

function goEdit(id, e) {
  e.stopPropagation()
  router.push({ name: 'category-edit', params: { id: String(id) } })
}

async function onDelete(id, e) {
  e.stopPropagation()
  if (!window.confirm('Удалить категорию?')) return
  try {
    await store.remove(id)
    toast.success('Категория удалена')
  } catch (e) {
    toast.danger(apiErrorMessage(e, 'Не удалось удалить категорию'))
  }
}

onMounted(() => {
  load()
})
</script>

<template>
  <div class="sklad-list-page">
    <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
      <div>
        <h1 class="h4 mb-1">
          Категории
        </h1>
        <p class="text-muted small mb-0">
          Справочник категорий товаров
        </p>
      </div>
    </div>

    <div
      class="position-relative sklad-list-fetch"
      :class="{ 'sklad-list-fetch--busy': store.loading }"
      :aria-busy="store.loading ? 'true' : undefined"
    >
      <div class="card border-0 shadow-sm rounded-3 mb-3">
        <div class="card-body py-3">
          <div class="row g-2 align-items-end flex-wrap">
            <div class="col-12 col-md">
              <label class="form-label small text-muted mb-1">Поиск по названию или описанию</label>
              <input
                v-model="filters.search"
                type="search"
                class="form-control"
                placeholder="Введите текст…"
                autocomplete="off"
                :disabled="store.loading"
                @input="onSearchInput"
              >
            </div>
            <div class="col-auto d-flex flex-wrap gap-2">
              <button type="button" class="btn btn-outline-secondary" :disabled="store.loading" @click="resetFilters">
                <i class="bi bi-x-lg me-1" aria-hidden="true" />
                Сбросить фильтры
              </button>
              <button
                type="button"
                class="btn btn-primary"
                @click="router.push({ name: 'category-create' })"
              >
                <i class="bi bi-plus-lg me-1" aria-hidden="true" />
                Добавить категорию
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="card border-0 shadow-sm rounded-3 overflow-hidden">
        <div v-if="!store.loading && !store.items.length" class="text-center py-5 px-3">
        <i class="bi bi-inbox display-4 text-muted" aria-hidden="true" />
        <p class="text-muted mt-2 mb-0">
          Категории не найдены. Создайте первую категорию.
        </p>
        </div>

        <div v-else-if="!store.loading" class="table-responsive">
        <table class="table table-hover align-middle mb-0 sklad-table">
          <thead class="table-light">
            <tr>
              <th scope="col">
                Название
              </th>
              <th scope="col">
                Описание
              </th>
              <th scope="col" class="text-nowrap">
                Создано
              </th>
              <th scope="col" class="text-end" style="width: 9rem">
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
              @keydown.enter="router.push({ name: 'category-detail', params: { id: String(row.id) } })"
            >
              <td class="fw-medium">
                {{ row.name }}
              </td>
              <td class="text-muted small">
                {{ truncate(row.description, 64) }}
              </td>
              <td class="text-muted small text-nowrap">
                {{ formatDateTime(row.created_at) }}
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

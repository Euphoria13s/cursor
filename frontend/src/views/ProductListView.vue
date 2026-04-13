<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import PaginationComponent from '../components/PaginationComponent.vue'
import { useCategoryStore } from '../stores/categories'
import { useProductStore } from '../stores/products'
import { useToastStore } from '../stores/toast'
import { apiErrorMessage } from '../utils/apiErrorMessage'
import { boolRu, formatMoney, truncate } from '../utils/formatters'

const router = useRouter()
const productStore = useProductStore()
const categoryStore = useCategoryStore()
const toast = useToastStore()

const filters = reactive({
  search: '',
  category: '',
  is_active: '',
  /** '' | 'below' | 'ok' — частично клиентский фильтр по текущей странице */
  stock: '',
})

const currentPage = ref(1)

let searchDebounceTimer = null

const categoryOptions = computed(() => categoryStore.items || [])

function categoryName(catId) {
  if (catId == null) return '—'
  const c = categoryOptions.value.find((x) => x.id === catId)
  return c ? c.name : `Категория #${catId}`
}

function buildParams() {
  const params = { page: currentPage.value }
  const q = filters.search.trim()
  if (q) params.search = q
  if (filters.category !== '' && filters.category != null) {
    params.category = filters.category
  }
  if (filters.is_active === 'true') params.is_active = true
  if (filters.is_active === 'false') params.is_active = false
  return params
}

async function load() {
  await productStore.fetchAll(buildParams())
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
  filters.category = ''
  filters.is_active = ''
  filters.stock = ''
  clearTimeout(searchDebounceTimer)
  currentPage.value = 1
  load()
}

watch(
  () => [filters.category, filters.is_active],
  () => {
    applyFilters()
  },
)

const tableRows = computed(() => {
  const items = productStore.items || []
  if (filters.stock === 'below') {
    return items.filter((p) => {
      const cs = Number(p.current_stock)
      const ms = Number(p.min_stock)
      if (Number.isNaN(cs) || Number.isNaN(ms)) return false
      return cs <= ms
    })
  }
  if (filters.stock === 'ok') {
    return items.filter((p) => {
      const cs = Number(p.current_stock)
      const ms = Number(p.min_stock)
      if (Number.isNaN(cs) || Number.isNaN(ms)) return false
      return cs > ms
    })
  }
  return items
})

function onPageChange(page) {
  if (page < 1 || page > productStore.totalPages) return
  currentPage.value = page
  load()
}

function rowClick(id, e) {
  if (e.target.closest('a,button')) return
  router.push({ name: 'product-detail', params: { id: String(id) } })
}

function goEdit(id, e) {
  e.stopPropagation()
  router.push({ name: 'product-edit', params: { id: String(id) } })
}

async function onDelete(id, e) {
  e.stopPropagation()
  if (!window.confirm('Удалить товар?')) return
  try {
    await productStore.remove(id)
    toast.success('Товар удалён')
  } catch (e) {
    toast.danger(apiErrorMessage(e, 'Не удалось удалить товар'))
  }
}

onMounted(async () => {
  await categoryStore.fetchAll({ page: 1, page_size: 500 })
  currentPage.value = 1
  await load()
})
</script>

<template>
  <div class="sklad-list-page">
    <div class="mb-3">
      <h1 class="h4 mb-1">
        Товары
      </h1>
      <p class="text-muted small mb-0">
        Номенклатура и остатки
      </p>
    </div>

    <div
      class="position-relative sklad-list-fetch"
      :class="{ 'sklad-list-fetch--busy': productStore.loading }"
      :aria-busy="productStore.loading ? 'true' : undefined"
    >
      <div class="card border-0 shadow-sm rounded-3 mb-3">
        <div class="card-body py-3">
          <div class="row g-2 align-items-end flex-wrap">
            <div class="col-12 col-md-6 col-lg">
              <label class="form-label small text-muted mb-1">Поиск</label>
              <input
                v-model="filters.search"
                type="search"
                class="form-control"
                placeholder="Название или SKU"
                autocomplete="off"
                :disabled="productStore.loading"
                @input="onSearchInput"
              >
            </div>
            <div class="col-6 col-md-3 col-lg">
              <label class="form-label small text-muted mb-1">Категория</label>
              <select v-model="filters.category" class="form-select" :disabled="productStore.loading">
              <option value="">
                Все
              </option>
              <option v-for="c in categoryOptions" :key="c.id" :value="String(c.id)">
                {{ c.name }}
              </option>
              </select>
            </div>
            <div class="col-6 col-md-3 col-lg">
              <label class="form-label small text-muted mb-1">Активен</label>
              <select v-model="filters.is_active" class="form-select" :disabled="productStore.loading">
              <option value="">
                Все
              </option>
              <option value="true">
                Активные
              </option>
              <option value="false">
                Неактивные
              </option>
              </select>
            </div>
            <div class="col-12 col-md-6 col-lg">
              <label class="form-label small text-muted mb-1">Остаток</label>
              <select v-model="filters.stock" class="form-select" :disabled="productStore.loading">
              <option value="">
                Все
              </option>
              <option value="below">
                Ниже минимума
              </option>
              <option value="ok">
                В норме
              </option>
              </select>
              <div v-if="filters.stock" class="form-text">
                Уточнение по остатку применяется к строкам текущей страницы
              </div>
            </div>
            <div class="col-12 d-flex flex-wrap gap-2 ms-lg-auto">
              <button type="button" class="btn btn-outline-secondary" :disabled="productStore.loading" @click="resetFilters">
                <i class="bi bi-x-lg me-1" aria-hidden="true" />
                Сбросить фильтры
              </button>
              <button type="button" class="btn btn-outline-secondary" disabled title="Экспорт (демо)">
              <i class="bi bi-download me-1" aria-hidden="true" />
              Экспорт
              </button>
              <button
                type="button"
                class="btn btn-primary"
                @click="router.push({ name: 'product-create' })"
              >
                <i class="bi bi-plus-lg me-1" aria-hidden="true" />
                Добавить товар
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="card border-0 shadow-sm rounded-3 overflow-hidden">
        <div v-if="!productStore.loading && !tableRows.length" class="text-center py-5 px-3">
        <i class="bi bi-box-seam display-4 text-muted" aria-hidden="true" />
        <p class="text-muted mt-2 mb-0">
          Товары не найдены.
        </p>
        </div>

        <div v-else-if="!productStore.loading" class="table-responsive">
        <table class="table table-hover align-middle mb-0 small">
          <thead class="table-light">
            <tr>
              <th>Название</th>
              <th>SKU</th>
              <th>Категория</th>
              <th>Ед.</th>
              <th class="text-end">
                Остаток
              </th>
              <th class="text-end">
                Мин.
              </th>
              <th class="text-end">
                Цена закупки
              </th>
              <th>Активен</th>
              <th class="text-end" style="width: 7rem">
                Действия
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="row in tableRows"
              :key="row.id"
              class="sklad-table__row"
              role="button"
              tabindex="0"
              @click="rowClick(row.id, $event)"
              @keydown.enter="router.push({ name: 'product-detail', params: { id: String(row.id) } })"
            >
              <td class="fw-medium">
                {{ truncate(row.name, 40) }}
              </td>
              <td class="font-monospace">
                {{ row.sku }}
              </td>
              <td>{{ categoryName(row.category) }}</td>
              <td>{{ row.unit }}</td>
              <td class="text-end">
                {{ row.current_stock }}
              </td>
              <td class="text-end">
                {{ row.min_stock }}
              </td>
              <td class="text-end text-nowrap">
                {{ formatMoney(row.purchase_price) }}
              </td>
              <td>{{ boolRu(row.is_active) }}</td>
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
        v-if="productStore.loading"
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
      v-if="!productStore.loading"
      :current-page="currentPage"
      :total-pages="productStore.totalPages"
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

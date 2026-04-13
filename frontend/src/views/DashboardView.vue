<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useProductStore } from '../stores/products'
import { useReceiptStore } from '../stores/receipts'
import { useWriteoffStore } from '../stores/writeoffs'
import { formatDate, formatDocStatus, formatMoney } from '../utils/formatters'

const router = useRouter()
const productStore = useProductStore()
const receiptStore = useReceiptStore()
const writeoffStore = useWriteoffStore()

const pageLoading = ref(true)
const loadError = ref('')

function todayISO() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** Начало периода «последние 7 дней» (включая сегодня): 6 дней назад */
function weekStartISO() {
  const d = new Date()
  d.setDate(d.getDate() - 6)
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const products = computed(() => productStore.items || [])
const receipts = computed(() => receiptStore.items || [])
const writeoffs = computed(() => writeoffStore.items || [])

const kpiBelowMin = computed(() => {
  let n = 0
  for (const p of products.value) {
    const cs = Number(p.current_stock)
    const ms = Number(p.min_stock)
    if (Number.isNaN(cs) || Number.isNaN(ms)) continue
    if (cs <= ms) n += 1
  }
  return n
})

const kpiDocsToday = computed(() => {
  const t = todayISO()
  let n = 0
  for (const r of receipts.value) {
    if (String(r.receipt_date) === t) n += 1
  }
  for (const w of writeoffs.value) {
    if (String(w.writeoff_date) === t) n += 1
  }
  return n
})

const kpiActiveProducts = computed(() =>
  products.value.filter((p) => p.is_active === true).length,
)

const kpiWriteoffsWeek = computed(() => {
  const from = weekStartISO()
  const to = todayISO()
  let n = 0
  for (const w of writeoffs.value) {
    const d = String(w.writeoff_date || '')
    if (d >= from && d <= to) n += 1
  }
  return n
})

const recentDocuments = computed(() => {
  const rows = []

  for (const r of receipts.value) {
    rows.push({
      kind: 'receipt',
      id: r.id,
      typeLabel: 'Поступление',
      documentNumber: r.document_number,
      date: r.receipt_date,
      sortKey: String(r.receipt_date || ''),
      counterparty: r.supplier_name,
      author: authorLabel(r),
      status: r.status,
    })
  }

  for (const w of writeoffs.value) {
    rows.push({
      kind: 'writeoff',
      id: w.id,
      typeLabel: 'Списание',
      documentNumber: w.document_number,
      date: w.writeoff_date,
      sortKey: String(w.writeoff_date || ''),
      counterparty: w.reason,
      author: authorLabel(w),
      status: w.status,
    })
  }

  rows.sort((a, b) => {
    if (a.sortKey === b.sortKey) return (b.id || 0) - (a.id || 0)
    return a.sortKey < b.sortKey ? 1 : a.sortKey > b.sortKey ? -1 : 0
  })

  return rows.slice(0, 10)
})

const deficientProducts = computed(() => {
  const list = products.value
    .map((p) => {
      const cs = Number(p.current_stock)
      const ms = Number(p.min_stock)
      const deficit = Number.isNaN(cs) || Number.isNaN(ms) ? -Infinity : ms - cs
      return { p, cs, ms, deficit }
    })
    .filter((x) => !Number.isNaN(x.cs) && !Number.isNaN(x.ms) && x.cs <= x.ms)
    .sort((a, b) => b.deficit - a.deficit)
    .slice(0, 6)
    .map((x) => x.p)

  return list
})

function authorLabel(row) {
  if (row.author_name && String(row.author_name).trim()) return row.author_name
  if (row.created_by != null && row.created_by !== '') {
    if (typeof row.created_by === 'object') {
      return (
        row.created_by.username ||
        row.created_by.email ||
        `—`
      )
    }
    return `#${row.created_by}`
  }
  return '—'
}

function stockLine(p) {
  const cs = formatMoney(p.current_stock)
  const ms = formatMoney(p.min_stock)
  return `${cs} / min ${ms}`
}

function onDocRowClick(row) {
  if (row.kind === 'receipt') {
    router.push({ name: 'receipt-detail', params: { id: String(row.id) } })
  } else {
    router.push({ name: 'writeoff-detail', params: { id: String(row.id) } })
  }
}

function onProductRowClick(id) {
  router.push({ name: 'product-detail', params: { id: String(id) } })
}

async function load() {
  pageLoading.value = true
  loadError.value = ''
  try {
    await Promise.all([
      productStore.fetchAll({ page: 1, page_size: 500 }),
      receiptStore.fetchAll({ page: 1, page_size: 500 }),
      writeoffStore.fetchAll({ page: 1, page_size: 500 }),
    ])
  } catch {
    loadError.value = 'Не удалось загрузить данные для дашборда. Проверьте соединение с сервером.'
  } finally {
    pageLoading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="sklad-dashboard">
    <div class="mb-4">
      <h1 class="h4 mb-1">
        Дашборд
      </h1>
      <p class="text-muted small mb-0">
        Обзор ключевых показателей и последних документов
      </p>
    </div>

    <div v-if="pageLoading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка…</span>
      </div>
      <p class="text-muted small mt-2 mb-0">
        Загрузка данных…
      </p>
    </div>

    <template v-else>
      <div v-if="loadError" class="alert alert-warning border-0 shadow-sm rounded-3 mb-4" role="alert">
        {{ loadError }}
      </div>

      <!-- KPI -->
      <div class="row g-3 mb-4">
        <div class="col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm rounded-3 h-100">
            <div class="card-body d-flex border-start border-4 border-warning ps-3 py-3">
              <div class="flex-grow-1 min-w-0">
                <div class="text-muted small mb-1">
                  Позиции ниже минимума
                </div>
                <div class="fs-4 fw-semibold">
                  {{ kpiBelowMin }}
                </div>
              </div>
              <div class="text-warning opacity-75 align-self-start">
                <i class="bi bi-exclamation-triangle fs-4" aria-hidden="true" />
              </div>
            </div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm rounded-3 h-100">
            <div class="card-body d-flex border-start border-4 border-primary ps-3 py-3">
              <div class="flex-grow-1 min-w-0">
                <div class="text-muted small mb-1">
                  Документы за сегодня
                </div>
                <div class="fs-4 fw-semibold">
                  {{ kpiDocsToday }}
                </div>
              </div>
              <div class="text-primary opacity-75 align-self-start">
                <i class="bi bi-calendar-day fs-4" aria-hidden="true" />
              </div>
            </div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm rounded-3 h-100">
            <div class="card-body d-flex border-start border-4 border-success ps-3 py-3">
              <div class="flex-grow-1 min-w-0">
                <div class="text-muted small mb-1">
                  Активных товаров
                </div>
                <div class="fs-4 fw-semibold">
                  {{ kpiActiveProducts }}
                </div>
              </div>
              <div class="text-success opacity-75 align-self-start">
                <i class="bi bi-box-seam fs-4" aria-hidden="true" />
              </div>
            </div>
          </div>
        </div>
        <div class="col-sm-6 col-xl-3">
          <div class="card border-0 shadow-sm rounded-3 h-100">
            <div class="card-body d-flex border-start border-4 border-info ps-3 py-3">
              <div class="flex-grow-1 min-w-0">
                <div class="text-muted small mb-1">
                  Списания за неделю
                </div>
                <div class="fs-4 fw-semibold">
                  {{ kpiWriteoffsWeek }}
                </div>
              </div>
              <div class="text-info opacity-75 align-self-start">
                <i class="bi bi-arrow-up-circle fs-4" aria-hidden="true" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Быстрые действия -->
      <div class="card border-0 shadow-sm rounded-3 mb-4">
        <div class="card-body p-4">
          <h2 class="h6 text-muted mb-3">
            Быстрые действия
          </h2>
          <div class="d-flex flex-wrap gap-2">
            <router-link
              :to="{ name: 'receipt-create' }"
              class="btn btn-outline-primary btn-sm"
            >
              <i class="bi bi-plus-lg me-1" aria-hidden="true" />
              Новое поступление
            </router-link>
            <router-link
              :to="{ name: 'writeoff-create' }"
              class="btn btn-outline-primary btn-sm"
            >
              <i class="bi bi-plus-lg me-1" aria-hidden="true" />
              Новое списание
            </router-link>
            <button
              type="button"
              class="btn btn-outline-secondary btn-sm"
              disabled
              title="Раздел в разработке"
            >
              <i class="bi bi-stack me-1" aria-hidden="true" />
              Остатки
            </button>
            <button
              type="button"
              class="btn btn-outline-secondary btn-sm"
              disabled
              title="Раздел в разработке"
            >
              <i class="bi bi-graph-up-arrow me-1" aria-hidden="true" />
              Отчёт по движению
            </button>
          </div>
        </div>
      </div>

      <div class="row g-4 align-items-start">
        <!-- Последние документы -->
        <div class="col-lg-8">
          <div class="card border-0 shadow-sm rounded-3">
            <div class="card-body p-0">
              <div class="px-4 pt-4 pb-2">
                <h2 class="h6 text-muted mb-0">
                  Последние документы
                </h2>
              </div>
              <div v-if="!recentDocuments.length" class="px-4 pb-4 text-muted small">
                Нет документов для отображения
              </div>
              <div v-else class="table-responsive">
                <table class="table table-hover table-sm align-middle mb-0 sklad-dash-table">
                  <thead class="table-light">
                    <tr>
                      <th>Тип</th>
                      <th>Номер</th>
                      <th>Дата</th>
                      <th>Контрагент / причина</th>
                      <th>Автор</th>
                      <th>Статус</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="row in recentDocuments"
                      :key="`${row.kind}-${row.id}`"
                      role="button"
                      class="sklad-dash-row"
                      @click="onDocRowClick(row)"
                    >
                      <td class="text-nowrap">
                        <span
                          class="badge rounded-pill"
                          :class="row.kind === 'receipt' ? 'bg-primary-subtle text-primary' : 'bg-danger-subtle text-danger'"
                        >
                          {{ row.typeLabel }}
                        </span>
                      </td>
                      <td class="font-monospace small">
                        {{ row.documentNumber || '—' }}
                      </td>
                      <td class="text-nowrap small">
                        {{ formatDate(row.date) }}
                      </td>
                      <td class="small">
                        {{ row.counterparty || '—' }}
                      </td>
                      <td class="small">
                        {{ row.author }}
                      </td>
                      <td class="small">
                        {{ formatDocStatus(row.status) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- Дефицитные позиции -->
        <div class="col-lg-4">
          <div class="card border-0 shadow-sm rounded-3">
            <div class="card-body p-0">
              <div class="px-4 pt-4 pb-2">
                <h2 class="h6 text-muted mb-0">
                  <i class="bi bi-exclamation-octagon text-warning me-1" aria-hidden="true" />
                  Дефицитные позиции
                </h2>
              </div>
              <div v-if="!deficientProducts.length" class="px-4 pb-4 text-muted small">
                Нет позиций с остатком на уровне минимума или ниже
              </div>
              <div v-else class="table-responsive">
                <table class="table table-sm align-middle mb-0 sklad-dash-table">
                  <thead class="table-light">
                    <tr>
                      <th>SKU</th>
                      <th class="text-end">
                        Остаток
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="p in deficientProducts"
                      :key="p.id"
                      role="button"
                      class="sklad-dash-row"
                      @click="onProductRowClick(p.id)"
                    >
                      <td class="font-monospace small">
                        {{ p.sku || '—' }}
                      </td>
                      <td class="text-end small text-nowrap">
                        {{ stockLine(p) }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.sklad-dash-table thead th {
  font-weight: 500;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  color: var(--bs-secondary-color);
  border-bottom-width: 1px;
}

.sklad-dash-row {
  cursor: pointer;
}

.sklad-dash-row:hover {
  background-color: var(--bs-light);
}
</style>

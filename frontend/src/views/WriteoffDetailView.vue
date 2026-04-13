<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import api from '../services/api'
import { useProductStore } from '../stores/products'
import { useWriteoffStore } from '../stores/writeoffs'
import { useToastStore } from '../stores/toast'
import { apiErrorMessage } from '../utils/apiErrorMessage'
import { formatDate, formatDateTime, formatDocStatus, formatMoney } from '../utils/formatters'

const route = useRoute()
const router = useRouter()
const writeoffStore = useWriteoffStore()
const productStore = useProductStore()
const toast = useToastStore()

const id = computed(() => route.params.id)

const detail = ref(null)
const lines = ref([])
const loadError = ref('')
const deleteError = ref('')
const loading = ref(true)

function textOrDash(v) {
  if (v == null) return '—'
  const s = String(v).trim()
  return s === '' ? '—' : s
}

function authorDisplay(row) {
  if (!row) return '—'
  if (row.author_name && String(row.author_name).trim()) return row.author_name
  if (row.created_by != null && row.created_by !== '') {
    return typeof row.created_by === 'object'
      ? textOrDash(row.created_by.username || row.created_by.email)
      : `Пользователь #${row.created_by}`
  }
  return '—'
}

function productRow(line) {
  const pid = typeof line.product === 'object' ? line.product?.id : line.product
  const p = productStore.items.find((x) => x.id === pid)
  return {
    name: p?.name || (pid != null ? `Товар #${pid}` : '—'),
    sku: p?.sku || '—',
  }
}

async function load() {
  loading.value = true
  loadError.value = ''
  detail.value = null
  lines.value = []
  try {
    detail.value = await writeoffStore.fetchOne(id.value)
    await productStore.fetchAll({ page_size: 500 })
  } catch {
    loadError.value = 'Не удалось загрузить документ списания.'
    loading.value = false
    return
  }
  try {
    const { data } = await api.get('/writeoff-lines/', {
      params: { writeoff: id.value, page_size: 500 },
    })
    lines.value = data.results || data || []
  } catch {
    lines.value = []
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push({ name: 'writeoffs' })
}

function goEdit() {
  router.push({ name: 'writeoff-edit', params: { id: id.value } })
}

async function onDelete() {
  if (!window.confirm('Удалить документ списания?')) return
  deleteError.value = ''
  try {
    await writeoffStore.remove(id.value)
    toast.success('Списание удалено')
    router.push({ name: 'writeoffs' })
  } catch (e) {
    deleteError.value = ''
    toast.danger(apiErrorMessage(e, 'Не удалось удалить документ'))
  }
}

onMounted(load)
</script>

<template>
  <div class="sklad-detail-page">
    <div class="mb-4 d-flex flex-wrap align-items-start justify-content-between gap-3">
      <div>
        <h1 class="h4 mb-1">
          Документ списания
        </h1>
        <p v-if="detail" class="text-muted small mb-0 font-monospace">
          {{ detail.document_number }}
        </p>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <button
          v-if="detail && !loadError"
          type="button"
          class="btn btn-outline-primary btn-sm"
          @click="goEdit"
        >
          <i class="bi bi-pencil-square me-1" aria-hidden="true" />
          Редактировать
        </button>
        <button
          v-if="detail && !loadError"
          type="button"
          class="btn btn-outline-danger btn-sm"
          @click="onDelete"
        >
          <i class="bi bi-trash me-1" aria-hidden="true" />
          Удалить
        </button>
        <button type="button" class="btn btn-outline-secondary btn-sm" @click="goBack">
          <i class="bi bi-arrow-left me-1" aria-hidden="true" />
          Назад
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка…</span>
      </div>
      <p class="text-muted small mt-2 mb-0">
        Загрузка данных…
      </p>
    </div>

    <div v-else-if="loadError" class="alert alert-warning border-0 shadow-sm rounded-3" role="alert">
      {{ loadError }}
    </div>

    <template v-else-if="detail">
      <div v-if="deleteError" class="alert alert-danger py-2" role="alert">
        {{ deleteError }}
      </div>

      <div class="card border-0 shadow-sm rounded-3 mb-3">
        <div class="card-body p-4">
          <h2 class="h6 text-muted mb-3">
            Реквизиты документа
          </h2>
          <dl class="row mb-0 sklad-dl">
            <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
              Номер
            </dt>
            <dd class="col-sm-8 col-lg-9 mb-3 font-monospace">
              {{ textOrDash(detail.document_number) }}
            </dd>
            <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
              Дата
            </dt>
            <dd class="col-sm-8 col-lg-9 mb-3">
              {{ formatDate(detail.writeoff_date) }}
            </dd>
            <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
              Причина
            </dt>
            <dd class="col-sm-8 col-lg-9 mb-3">
              {{ textOrDash(detail.reason) }}
            </dd>
            <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
              Статус
            </dt>
            <dd class="col-sm-8 col-lg-9 mb-3">
              <span class="badge rounded-pill bg-light text-dark border">{{ formatDocStatus(detail.status) }}</span>
            </dd>
            <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
              Комментарий
            </dt>
            <dd class="col-sm-8 col-lg-9 mb-3">
              {{ textOrDash(detail.comment) }}
            </dd>
            <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
              Оформил
            </dt>
            <dd class="col-sm-8 col-lg-9 mb-3">
              {{ authorDisplay(detail) }}
            </dd>
            <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
              Создано
            </dt>
            <dd class="col-sm-8 col-lg-9 mb-0">
              {{ formatDateTime(detail.created_at) }}
            </dd>
          </dl>
        </div>
      </div>

      <div class="card border-0 shadow-sm rounded-3">
        <div class="card-body p-4">
          <h2 class="h6 text-muted mb-3">
            Позиции документа
          </h2>

          <div v-if="!lines.length" class="text-muted small border rounded-3 p-3 bg-white">
            Позиции отсутствуют
          </div>

          <div v-else class="table-responsive">
            <table class="table table-sm table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Товар</th>
                  <th>SKU</th>
                  <th class="text-end">
                    Количество
                  </th>
                  <th class="text-end">
                    Цена
                  </th>
                  <th class="text-end">
                    Сумма
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="line in lines" :key="line.id">
                  <td>{{ productRow(line).name }}</td>
                  <td class="font-monospace small">
                    {{ productRow(line).sku }}
                  </td>
                  <td class="text-end text-nowrap">
                    {{ formatMoney(line.quantity) }}
                  </td>
                  <td class="text-end text-nowrap">
                    {{ formatMoney(line.unit_price) }}
                  </td>
                  <td class="text-end text-nowrap fw-medium">
                    {{ formatMoney(line.line_total) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.sklad-dl dt {
  padding-top: 0.125rem;
}
</style>

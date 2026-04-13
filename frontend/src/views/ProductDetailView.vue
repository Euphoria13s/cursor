<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useCategoryStore } from '../stores/categories'
import { useProductStore } from '../stores/products'
import { useToastStore } from '../stores/toast'
import { apiErrorMessage } from '../utils/apiErrorMessage'
import { boolRu, formatDateTime, formatMoney } from '../utils/formatters'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const categoryStore = useCategoryStore()
const toast = useToastStore()

const id = computed(() => route.params.id)

const detail = ref(null)
const loadError = ref('')
const deleteError = ref('')
const loading = ref(true)

function textOrDash(v) {
  if (v == null) return '—'
  const s = String(v).trim()
  return s === '' ? '—' : s
}

const categoryLabel = computed(() => {
  const p = detail.value
  if (!p) return '—'
  const c = p.category
  if (c && typeof c === 'object' && c.name) return c.name
  const cid = typeof c === 'object' ? c?.id : c
  if (cid == null || cid === '') return '—'
  const found = categoryStore.items.find((x) => x.id === cid)
  return found ? found.name : `— (#${cid})`
})

async function load() {
  loading.value = true
  loadError.value = ''
  detail.value = null
  try {
    await categoryStore.fetchAll({ page_size: 500 })
    detail.value = await productStore.fetchOne(id.value)
  } catch {
    loadError.value = 'Не удалось загрузить товар. Возможно, запись удалена или нет доступа.'
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push({ name: 'products' })
}

function goEdit() {
  router.push({ name: 'product-edit', params: { id: id.value } })
}

async function onDelete() {
  if (!window.confirm('Удалить товар?')) return
  deleteError.value = ''
  try {
    await productStore.remove(id.value)
    toast.success('Товар удалён')
    router.push({ name: 'products' })
  } catch (e) {
    deleteError.value = ''
    toast.danger(apiErrorMessage(e, 'Не удалось удалить товар'))
  }
}

onMounted(load)
</script>

<template>
  <div class="sklad-detail-page">
    <div class="mb-4 d-flex flex-wrap align-items-start justify-content-between gap-3">
      <div>
        <h1 class="h4 mb-1">
          Карточка товара
        </h1>
        <p v-if="detail" class="text-muted small mb-0">
          {{ detail.name }} · <span class="font-monospace">{{ detail.sku }}</span>
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

    <div v-else-if="detail" class="row g-4">
      <div v-if="deleteError" class="col-12">
        <div class="alert alert-danger py-2 mb-0" role="alert">
          {{ deleteError }}
        </div>
      </div>

      <div class="col-lg-8">
        <div class="card border-0 shadow-sm rounded-3">
          <div class="card-body p-4">
            <h2 class="h6 text-muted mb-3">
              Основные данные
            </h2>
            <dl class="row mb-0 sklad-dl">
              <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
                Наименование
              </dt>
              <dd class="col-sm-8 col-lg-9 mb-3">
                {{ textOrDash(detail.name) }}
              </dd>
              <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
                SKU
              </dt>
              <dd class="col-sm-8 col-lg-9 mb-3 font-monospace">
                {{ textOrDash(detail.sku) }}
              </dd>
              <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
                Категория
              </dt>
              <dd class="col-sm-8 col-lg-9 mb-3">
                {{ categoryLabel }}
              </dd>
              <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
                Единица измерения
              </dt>
              <dd class="col-sm-8 col-lg-9 mb-3">
                {{ textOrDash(detail.unit) }}
              </dd>
              <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
                Закупочная цена
              </dt>
              <dd class="col-sm-8 col-lg-9 mb-3">
                {{ formatMoney(detail.purchase_price) }}
              </dd>
              <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
                Текущий остаток
              </dt>
              <dd class="col-sm-8 col-lg-9 mb-3">
                <span class="rounded-2 bg-light px-2 py-1 d-inline-block">{{ formatMoney(detail.current_stock) }}</span>
              </dd>
              <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
                Минимальный остаток
              </dt>
              <dd class="col-sm-8 col-lg-9 mb-3">
                {{ formatMoney(detail.min_stock) }}
              </dd>
              <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
                Активен
              </dt>
              <dd class="col-sm-8 col-lg-9 mb-3">
                {{ detail.is_active == null ? '—' : boolRu(detail.is_active) }}
              </dd>
              <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
                Описание
              </dt>
              <dd class="col-sm-8 col-lg-9 mb-3">
                {{ textOrDash(detail.description) }}
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

        <div class="card border-0 shadow-sm rounded-3 mt-3">
          <div class="card-body p-4">
            <h2 class="h6 text-muted mb-2">
              Связанные документы
            </h2>
            <p class="small text-muted mb-0">
              Движения по товару отображаются в журналах поступлений и списаний при проведении документов.
            </p>
          </div>
        </div>
      </div>

      <div class="col-lg-4">
        <div class="card border-0 shadow-sm rounded-3 bg-light">
          <div class="card-body p-3">
            <h2 class="h6 mb-3">
              <i class="bi bi-info-circle text-primary me-1" aria-hidden="true" />
              Подсказка
            </h2>
            <ul class="small text-muted mb-0 ps-3">
              <li class="mb-2">
                SKU должен быть уникальным в системе
              </li>
              <li class="mb-2">
                Текущий остаток меняется только проведёнными документами
              </li>
              <li>
                Новую категорию можно добавить в разделе «Категории»
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sklad-dl dt {
  padding-top: 0.125rem;
}
</style>

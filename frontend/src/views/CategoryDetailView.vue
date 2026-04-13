<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useCategoryStore } from '../stores/categories'
import { useToastStore } from '../stores/toast'
import { apiErrorMessage } from '../utils/apiErrorMessage'
import { formatDateTime } from '../utils/formatters'

const route = useRoute()
const router = useRouter()
const store = useCategoryStore()
const toast = useToastStore()

const id = computed(() => route.params.id)

const detail = ref(null)
const loadError = ref('')
const deleteError = ref('')
const loading = ref(true)

async function load() {
  loading.value = true
  loadError.value = ''
  detail.value = null
  try {
    detail.value = await store.fetchOne(id.value)
  } catch {
    loadError.value = 'Не удалось загрузить категорию. Возможно, запись удалена или нет доступа.'
  } finally {
    loading.value = false
  }
}

function textOrDash(v) {
  if (v == null) return '—'
  const s = String(v).trim()
  return s === '' ? '—' : s
}

function goBack() {
  router.push({ name: 'categories' })
}

function goEdit() {
  router.push({ name: 'category-edit', params: { id: id.value } })
}

async function onDelete() {
  if (!window.confirm('Удалить категорию?')) return
  deleteError.value = ''
  try {
    await store.remove(id.value)
    toast.success('Категория удалена')
    router.push({ name: 'categories' })
  } catch (e) {
    deleteError.value = ''
    toast.danger(apiErrorMessage(e, 'Не удалось удалить категорию'))
  }
}

onMounted(load)
</script>

<template>
  <div class="sklad-detail-page">
    <div class="mb-4 d-flex flex-wrap align-items-start justify-content-between gap-3">
      <div>
        <h1 class="h4 mb-1">
          Категория
        </h1>
        <p v-if="detail" class="text-muted small mb-0">
          {{ detail.name }}
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

      <div class="card border-0 shadow-sm rounded-3">
        <div class="card-body p-4">
          <h2 class="h6 text-muted mb-3">
            Данные категории
          </h2>
          <dl class="row mb-0 sklad-dl">
            <dt class="col-sm-4 col-lg-3 text-muted small fw-normal">
              Название
            </dt>
            <dd class="col-sm-8 col-lg-9 mb-3">
              {{ textOrDash(detail.name) }}
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
    </template>
  </div>
</template>

<style scoped>
.sklad-dl dt {
  padding-top: 0.125rem;
}
</style>

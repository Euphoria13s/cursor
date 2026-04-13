<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useCategoryStore } from '../stores/categories'
import { useProductStore } from '../stores/products'
import { useToastStore } from '../stores/toast'
import { apiErrorMessage } from '../utils/apiErrorMessage'
import { mapDrfErrors } from '../utils/apiErrors'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const categoryStore = useCategoryStore()
const toast = useToastStore()

const id = computed(() => route.params.id)
const isEdit = computed(() => Boolean(id.value))

const form = reactive({
  name: '',
  sku: '',
  category: '',
  unit: '',
  purchase_price: '',
  min_stock: '',
  current_stock_display: '—',
  is_active: true,
  description: '',
})
const fieldErrors = reactive({
  name: '',
  sku: '',
  category: '',
  unit: '',
  purchase_price: '',
  min_stock: '',
  description: '',
  _form: '',
})
const submitting = ref(false)

const categories = computed(() => categoryStore.items || [])

function validateClient() {
  const keys = ['name', 'sku', 'category', 'unit', 'purchase_price', 'min_stock', 'description', '_form']
  keys.forEach((k) => {
    if (k in fieldErrors) fieldErrors[k] = ''
  })
  let ok = true
  if (!form.name.trim()) {
    fieldErrors.name = 'Укажите наименование'
    ok = false
  }
  if (!form.sku.trim()) {
    fieldErrors.sku = 'Укажите SKU'
    ok = false
  }
  if (form.category === '' || form.category == null) {
    fieldErrors.category = 'Выберите категорию'
    ok = false
  }
  if (!form.unit.trim()) {
    fieldErrors.unit = 'Укажите единицу измерения'
    ok = false
  }
  const pp = Number(String(form.purchase_price).replace(',', '.'))
  if (form.purchase_price === '' || Number.isNaN(pp) || pp < 0) {
    fieldErrors.purchase_price = 'Укажите корректную цену'
    ok = false
  }
  const ms = Number(String(form.min_stock).replace(',', '.'))
  if (form.min_stock === '' || Number.isNaN(ms) || ms < 0) {
    fieldErrors.min_stock = 'Укажите минимальный остаток'
    ok = false
  }
  return ok
}

function buildPayload() {
  return {
    name: form.name.trim(),
    sku: form.sku.trim(),
    category: Number(form.category),
    unit: form.unit.trim(),
    description: form.description.trim(),
    purchase_price: String(form.purchase_price).replace(',', '.'),
    min_stock: String(form.min_stock).replace(',', '.'),
    is_active: form.is_active,
  }
}

async function load() {
  await categoryStore.fetchAll({ page: 1, page_size: 500 })
  if (!isEdit.value) return
  fieldErrors._form = ''
  try {
    await productStore.fetchOne(id.value)
    const p = productStore.currentItem
    if (!p) return
    form.name = p.name || ''
    form.sku = p.sku || ''
    form.category = p.category != null ? String(p.category) : ''
    form.unit = p.unit || ''
    form.purchase_price = p.purchase_price != null ? String(p.purchase_price) : ''
    form.min_stock = p.min_stock != null ? String(p.min_stock) : ''
    form.current_stock_display =
      p.current_stock != null ? String(p.current_stock) : '—'
    form.is_active = Boolean(p.is_active)
    form.description = p.description || ''
  } catch (e) {
    fieldErrors._form = 'Не удалось загрузить товар'
    toast.danger(apiErrorMessage(e, 'Не удалось загрузить товар'))
  }
}

async function onSubmit() {
  fieldErrors._form = ''
  if (!validateClient()) return

  submitting.value = true
  try {
    const payload = buildPayload()
    if (isEdit.value) {
      await productStore.update(id.value, payload)
      toast.success('Товар сохранён')
    } else {
      await productStore.create(payload)
      toast.success('Товар создан')
    }
    router.push({ name: 'products' })
  } catch (e) {
    mapDrfErrors(e, fieldErrors, [
      'name',
      'sku',
      'category',
      'unit',
      'purchase_price',
      'min_stock',
      'description',
      '_form',
    ])
    toast.danger(apiErrorMessage(e))
  } finally {
    submitting.value = false
  }
}

function onCancel() {
  router.push({ name: 'products' })
}

onMounted(load)
</script>

<template>
  <div class="sklad-form-page">
    <div class="mb-4">
      <h1 class="h4 mb-1">
        Карточка товара
      </h1>
      <p class="text-muted small mb-0">
        {{ isEdit ? 'Редактирование' : 'Создание новой позиции' }}
      </p>
    </div>

    <div v-if="isEdit && productStore.loading && !submitting" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка…</span>
      </div>
    </div>

    <div v-else class="row g-4">
      <div class="col-lg-8">
        <div class="card border-0 shadow-sm rounded-3">
          <div class="card-body p-4">
            <div v-if="fieldErrors._form" class="alert alert-danger py-2" role="alert">
              {{ fieldErrors._form }}
            </div>

            <form @submit.prevent="onSubmit">
              <div class="mb-3">
                <label class="form-label">Наименование <span class="text-danger">*</span></label>
                <input
                  v-model="form.name"
                  type="text"
                  class="form-control"
                  :class="{ 'is-invalid': fieldErrors.name }"
                >
                <div v-if="fieldErrors.name" class="invalid-feedback d-block">
                  {{ fieldErrors.name }}
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">SKU <span class="text-danger">*</span></label>
                <input
                  v-model="form.sku"
                  type="text"
                  class="form-control font-monospace"
                  :class="{ 'is-invalid': fieldErrors.sku }"
                >
                <div v-if="fieldErrors.sku" class="invalid-feedback d-block">
                  {{ fieldErrors.sku }}
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Категория <span class="text-danger">*</span></label>
                <select
                  v-model="form.category"
                  class="form-select"
                  :class="{ 'is-invalid': fieldErrors.category }"
                >
                  <option disabled value="">
                    Выберите категорию
                  </option>
                  <option v-for="c in categories" :key="c.id" :value="String(c.id)">
                    {{ c.name }}
                  </option>
                </select>
                <div v-if="fieldErrors.category" class="invalid-feedback d-block">
                  {{ fieldErrors.category }}
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Единица измерения <span class="text-danger">*</span></label>
                <input
                  v-model="form.unit"
                  type="text"
                  class="form-control"
                  placeholder="шт, кг…"
                  :class="{ 'is-invalid': fieldErrors.unit }"
                >
                <div v-if="fieldErrors.unit" class="invalid-feedback d-block">
                  {{ fieldErrors.unit }}
                </div>
              </div>

              <div class="row g-3 mb-3">
                <div class="col-md-6">
                  <label class="form-label">Закупочная цена <span class="text-danger">*</span></label>
                  <input
                    v-model="form.purchase_price"
                    type="text"
                    inputmode="decimal"
                    class="form-control"
                    :class="{ 'is-invalid': fieldErrors.purchase_price }"
                  >
                  <div v-if="fieldErrors.purchase_price" class="invalid-feedback d-block">
                    {{ fieldErrors.purchase_price }}
                  </div>
                </div>
                <div class="col-md-6">
                  <label class="form-label">Минимальный остаток <span class="text-danger">*</span></label>
                  <input
                    v-model="form.min_stock"
                    type="text"
                    inputmode="decimal"
                    class="form-control"
                    :class="{ 'is-invalid': fieldErrors.min_stock }"
                  >
                  <div v-if="fieldErrors.min_stock" class="invalid-feedback d-block">
                    {{ fieldErrors.min_stock }}
                  </div>
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label text-muted">Текущий остаток</label>
                <input
                  :value="form.current_stock_display"
                  type="text"
                  class="form-control bg-light"
                  readonly
                  tabindex="-1"
                >
                <div class="form-text">
                  Изменяется только документами поступления и списания
                </div>
              </div>

              <div class="mb-3 form-check">
                <input id="p-active" v-model="form.is_active" type="checkbox" class="form-check-input">
                <label class="form-check-label" for="p-active">Активен</label>
              </div>

              <div class="mb-4">
                <label class="form-label">Описание</label>
                <textarea
                  v-model="form.description"
                  class="form-control"
                  :class="{ 'is-invalid': fieldErrors.description }"
                  rows="3"
                />
                <div v-if="fieldErrors.description" class="invalid-feedback d-block">
                  {{ fieldErrors.description }}
                </div>
              </div>

              <div class="d-flex flex-wrap gap-2">
                <button type="submit" class="btn btn-primary" :disabled="submitting">
                  <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
                  {{ submitting ? 'Сохранение…' : 'Сохранить' }}
                </button>
                <button type="button" class="btn btn-outline-secondary" :disabled="submitting" @click="onCancel">
                  Отмена
                </button>
              </div>
            </form>
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

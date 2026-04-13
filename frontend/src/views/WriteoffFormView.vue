<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import api from '../services/api'
import { useProductStore } from '../stores/products'
import { useWriteoffStore } from '../stores/writeoffs'
import { useToastStore } from '../stores/toast'
import { apiErrorMessage } from '../utils/apiErrorMessage'
import { mapDrfErrors } from '../utils/apiErrors'

const route = useRoute()
const router = useRouter()
const writeoffStore = useWriteoffStore()
const productStore = useProductStore()
const toast = useToastStore()

const id = computed(() => route.params.id)
const isEdit = computed(() => Boolean(id.value))

const STATUS_OPTIONS = [
  { value: 'draft', label: 'Черновик' },
  { value: 'posted', label: 'Проведён' },
  { value: 'cancelled', label: 'Отменён' },
]

const header = reactive({
  document_number: '',
  writeoff_date: '',
  reason: '',
  status: 'draft',
  comment: '',
})

const lines = ref([])

const fieldErrors = reactive({
  document_number: '',
  writeoff_date: '',
  reason: '',
  status: '',
  comment: '',
  lines: '',
  _form: '',
})

const submitting = ref(false)

const products = computed(() => productStore.items || [])

function newLine() {
  return {
    _key: `${Date.now()}-${Math.random()}`,
    id: null,
    product: '',
    quantity: '',
    unit_price: '',
  }
}

function addLine() {
  lines.value.push(newLine())
}

function removeLine(index) {
  lines.value.splice(index, 1)
}

function lineTotal(line) {
  const q = Number(String(line.quantity).replace(',', '.'))
  const p = Number(String(line.unit_price).replace(',', '.'))
  if (Number.isNaN(q) || Number.isNaN(p)) return '—'
  return (q * p).toFixed(2)
}

async function fetchWriteoffLines(writeoffId) {
  const { data } = await api.get('/writeoff-lines/', {
    params: { writeoff: writeoffId, page_size: 500 },
  })
  return data.results || data || []
}

async function deleteAllLines(writeoffId) {
  const existing = await fetchWriteoffLines(writeoffId)
  await Promise.all(existing.map((l) => api.delete(`/writeoff-lines/${l.id}/`)))
}

async function saveLines(writeoffId) {
  for (const line of lines.value) {
    const qty = Number(String(line.quantity).replace(',', '.'))
    const up = Number(String(line.unit_price).replace(',', '.'))
    if (!line.product || Number.isNaN(qty) || qty <= 0 || Number.isNaN(up) || up < 0) continue
    const lt = (qty * up).toFixed(2)
    await api.post('/writeoff-lines/', {
      writeoff: writeoffId,
      product: Number(line.product),
      quantity: String(qty),
      unit_price: String(up.toFixed(2)),
      line_total: lt,
    })
  }
}

function validateClient() {
  Object.keys(fieldErrors).forEach((k) => {
    fieldErrors[k] = ''
  })
  let ok = true
  if (!header.document_number.trim()) {
    fieldErrors.document_number = 'Укажите номер'
    ok = false
  }
  if (!header.writeoff_date) {
    fieldErrors.writeoff_date = 'Укажите дату'
    ok = false
  }
  if (!header.reason.trim()) {
    fieldErrors.reason = 'Укажите причину'
    ok = false
  }
  if (!header.status) {
    fieldErrors.status = 'Выберите статус'
    ok = false
  }
  const validLines = lines.value.filter((l) => {
    const q = Number(String(l.quantity).replace(',', '.'))
    const p = Number(String(l.unit_price).replace(',', '.'))
    return l.product && !Number.isNaN(q) && q > 0 && !Number.isNaN(p) && p >= 0
  })
  if (!validLines.length) {
    fieldErrors.lines = 'Добавьте хотя бы одну строку с товаром, количеством и ценой'
    ok = false
  }
  return ok
}

function buildHeaderPayload() {
  return {
    document_number: header.document_number.trim(),
    writeoff_date: header.writeoff_date,
    reason: header.reason.trim(),
    status: header.status,
    comment: header.comment.trim(),
  }
}

async function load() {
  await productStore.fetchAll({ page: 1, page_size: 500 })
  if (!isEdit.value) {
    lines.value = [newLine()]
    return
  }
  fieldErrors._form = ''
  try {
    await writeoffStore.fetchOne(id.value)
    const w = writeoffStore.currentItem
    if (!w) return
    header.document_number = w.document_number || ''
    header.writeoff_date = w.writeoff_date || ''
    header.reason = w.reason || ''
    header.status = w.status || 'draft'
    header.comment = w.comment || ''

    const raw = await fetchWriteoffLines(id.value)
    if (raw.length) {
      lines.value = raw.map((l) => ({
        _key: `${l.id}-${Math.random()}`,
        id: l.id,
        product: String(l.product),
        quantity: String(l.quantity),
        unit_price: String(l.unit_price),
      }))
    } else {
      lines.value = [newLine()]
    }
  } catch (e) {
    fieldErrors._form = 'Не удалось загрузить документ'
    toast.danger(apiErrorMessage(e, 'Не удалось загрузить документ'))
  }
}

async function onSubmit() {
  fieldErrors._form = ''
  if (!validateClient()) return

  submitting.value = true
  try {
    const head = buildHeaderPayload()
    if (isEdit.value) {
      await writeoffStore.update(id.value, head)
      await deleteAllLines(id.value)
      await saveLines(Number(id.value))
      toast.success('Списание сохранено')
    } else {
      const created = await writeoffStore.create(head)
      const wid = created?.id
      if (wid == null) throw new Error('Нет id документа')
      await saveLines(wid)
      toast.success('Списание создано')
    }
    router.push({ name: 'writeoffs' })
  } catch (e) {
    mapDrfErrors(e, fieldErrors, [
      'document_number',
      'writeoff_date',
      'reason',
      'status',
      'comment',
      'lines',
      '_form',
    ])
    toast.danger(apiErrorMessage(e))
  } finally {
    submitting.value = false
  }
}

function onCancel() {
  router.push({ name: 'writeoffs' })
}

onMounted(load)
</script>

<template>
  <div class="sklad-form-page">
    <div class="mb-4 d-flex flex-wrap align-items-start justify-content-between gap-2">
      <div>
        <h1 class="h4 mb-1">
          Документ списания
        </h1>
        <p class="text-muted small mb-0">
          {{ isEdit ? 'Редактирование' : 'Новое списание' }}
        </p>
      </div>
      <button type="button" class="btn btn-outline-secondary btn-sm" @click="onCancel">
        <i class="bi bi-arrow-left me-1" aria-hidden="true" />
        К списку
      </button>
    </div>

    <div v-if="isEdit && writeoffStore.loading && !submitting" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка…</span>
      </div>
    </div>

    <div v-else>
      <div v-if="fieldErrors._form" class="alert alert-danger" role="alert">
        {{ fieldErrors._form }}
      </div>

      <div class="card border-0 shadow-sm rounded-3 mb-3">
        <div class="card-body p-4">
          <h2 class="h6 text-muted mb-3">
            Шапка документа
          </h2>
          <div class="row g-3">
            <div class="col-md-4">
              <label class="form-label">Номер документа <span class="text-danger">*</span></label>
              <input
                v-model="header.document_number"
                type="text"
                class="form-control"
                :class="{ 'is-invalid': fieldErrors.document_number }"
              >
              <div v-if="fieldErrors.document_number" class="invalid-feedback d-block">
                {{ fieldErrors.document_number }}
              </div>
            </div>
            <div class="col-md-4">
              <label class="form-label">Дата <span class="text-danger">*</span></label>
              <input
                v-model="header.writeoff_date"
                type="date"
                class="form-control"
                :class="{ 'is-invalid': fieldErrors.writeoff_date }"
              >
              <div v-if="fieldErrors.writeoff_date" class="invalid-feedback d-block">
                {{ fieldErrors.writeoff_date }}
              </div>
            </div>
            <div class="col-md-4">
              <label class="form-label">Статус <span class="text-danger">*</span></label>
              <select v-model="header.status" class="form-select" :class="{ 'is-invalid': fieldErrors.status }">
                <option v-for="opt in STATUS_OPTIONS" :key="opt.value" :value="opt.value">
                  {{ opt.label }}
                </option>
              </select>
              <div v-if="fieldErrors.status" class="invalid-feedback d-block">
                {{ fieldErrors.status }}
              </div>
            </div>
            <div class="col-12">
              <label class="form-label">Причина <span class="text-danger">*</span></label>
              <textarea
                v-model="header.reason"
                class="form-control"
                :class="{ 'is-invalid': fieldErrors.reason }"
                rows="2"
              />
              <div v-if="fieldErrors.reason" class="invalid-feedback d-block">
                {{ fieldErrors.reason }}
              </div>
            </div>
            <div class="col-12">
              <label class="form-label">Комментарий</label>
              <textarea
                v-model="header.comment"
                class="form-control"
                :class="{ 'is-invalid': fieldErrors.comment }"
                rows="2"
              />
              <div v-if="fieldErrors.comment" class="invalid-feedback d-block">
                {{ fieldErrors.comment }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card border-0 shadow-sm rounded-3 mb-3">
        <div class="card-body p-4">
          <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-3">
            <h2 class="h6 text-muted mb-0">
              Строки документа
            </h2>
            <button type="button" class="btn btn-sm btn-outline-primary" @click="addLine">
              <i class="bi bi-plus-lg me-1" aria-hidden="true" />
              Добавить строку
            </button>
          </div>
          <div v-if="fieldErrors.lines" class="alert alert-warning py-2 small mb-3">
            {{ fieldErrors.lines }}
          </div>

          <div class="table-responsive">
            <table class="table table-sm align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th style="min-width: 12rem">
                    Товар
                  </th>
                  <th style="width: 7rem">
                    Кол-во
                  </th>
                  <th style="width: 7rem">
                    Цена
                  </th>
                  <th style="width: 7rem">
                    Сумма
                  </th>
                  <th style="width: 3rem" />
                </tr>
              </thead>
              <tbody>
                <tr v-for="(line, idx) in lines" :key="line._key">
                  <td>
                    <select v-model="line.product" class="form-select form-select-sm">
                      <option value="" disabled>
                        Выберите товар
                      </option>
                      <option v-for="p in products" :key="p.id" :value="String(p.id)">
                        {{ p.name }} ({{ p.sku }})
                      </option>
                    </select>
                  </td>
                  <td>
                    <input v-model="line.quantity" type="text" class="form-control form-control-sm" inputmode="decimal">
                  </td>
                  <td>
                    <input v-model="line.unit_price" type="text" class="form-control form-control-sm" inputmode="decimal">
                  </td>
                  <td class="small text-muted">
                    {{ lineTotal(line) }}
                  </td>
                  <td>
                    <button
                      type="button"
                      class="btn btn-sm btn-outline-danger"
                      :disabled="lines.length <= 1"
                      title="Удалить строку"
                      @click="removeLine(idx)"
                    >
                      <i class="bi bi-trash" aria-hidden="true" />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div class="d-flex flex-wrap gap-2">
        <button type="button" class="btn btn-primary" :disabled="submitting" @click="onSubmit">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
          {{ submitting ? 'Сохранение…' : 'Сохранить' }}
        </button>
        <button type="button" class="btn btn-outline-secondary" :disabled="submitting" @click="onCancel">
          Отмена
        </button>
      </div>
    </div>
  </div>
</template>

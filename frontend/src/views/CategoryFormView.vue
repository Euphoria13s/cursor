<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useCategoryStore } from '../stores/categories'
import { useToastStore } from '../stores/toast'
import { apiErrorMessage } from '../utils/apiErrorMessage'
import { mapDrfErrors } from '../utils/apiErrors'

const route = useRoute()
const router = useRouter()
const store = useCategoryStore()
const toast = useToastStore()

const id = computed(() => route.params.id)
const isEdit = computed(() => Boolean(id.value))

const form = reactive({
  name: '',
  description: '',
})
const fieldErrors = reactive({
  name: '',
  description: '',
  _form: '',
})
const submitting = ref(false)

const pageTitle = computed(() =>
  isEdit.value ? 'Редактирование категории' : 'Создание категории',
)

function validateClient() {
  fieldErrors.name = ''
  fieldErrors.description = ''
  let ok = true
  if (!form.name.trim()) {
    fieldErrors.name = 'Укажите название'
    ok = false
  }
  return ok
}

async function load() {
  if (!isEdit.value) return
  fieldErrors._form = ''
  try {
    await store.fetchOne(id.value)
    const c = store.currentItem
    if (c) {
      form.name = c.name || ''
      form.description = c.description || ''
    }
  } catch (e) {
    fieldErrors._form = 'Не удалось загрузить категорию'
    toast.danger(apiErrorMessage(e, 'Не удалось загрузить категорию'))
  }
}

async function onSubmit() {
  fieldErrors._form = ''
  fieldErrors.name = ''
  fieldErrors.description = ''
  if (!validateClient()) return

  submitting.value = true
  try {
    const payload = {
      name: form.name.trim(),
      description: form.description.trim(),
    }
    if (isEdit.value) {
      await store.update(id.value, payload)
      toast.success('Категория сохранена')
    } else {
      await store.create(payload)
      toast.success('Категория создана')
    }
    router.push({ name: 'categories' })
  } catch (e) {
    mapDrfErrors(e, fieldErrors, ['name', 'description', '_form'])
    toast.danger(apiErrorMessage(e))
  } finally {
    submitting.value = false
  }
}

function onCancel() {
  router.push({ name: 'categories' })
}

onMounted(() => {
  load()
})
</script>

<template>
  <div class="sklad-form-page">
    <div class="mb-4">
      <h1 class="h4 mb-1">
        {{ pageTitle }}
      </h1>
      <p class="text-muted small mb-0">
        Справочник категорий товаров
      </p>
    </div>

    <div v-if="isEdit && store.loading && !submitting" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Загрузка…</span>
      </div>
    </div>

    <div v-else class="card border-0 shadow-sm rounded-3">
      <div class="card-body p-4">
        <div v-if="fieldErrors._form" class="alert alert-danger py-2" role="alert">
          {{ fieldErrors._form }}
        </div>

        <form @submit.prevent="onSubmit">
          <div class="mb-3">
            <label for="cat-name" class="form-label">Название <span class="text-danger">*</span></label>
            <input
              id="cat-name"
              v-model="form.name"
              type="text"
              class="form-control"
              :class="{ 'is-invalid': fieldErrors.name }"
              maxlength="150"
              autocomplete="off"
            >
            <div v-if="fieldErrors.name" class="invalid-feedback d-block">
              {{ fieldErrors.name }}
            </div>
          </div>

          <div class="mb-4">
            <label for="cat-desc" class="form-label">Описание</label>
            <textarea
              id="cat-desc"
              v-model="form.description"
              class="form-control"
              :class="{ 'is-invalid': fieldErrors.description }"
              rows="4"
              placeholder="Необязательно"
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
</template>

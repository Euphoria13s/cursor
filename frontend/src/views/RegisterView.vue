<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''

  if (password.value !== passwordConfirm.value) {
    error.value = 'Пароли не совпадают'
    toast.danger(error.value)
    return
  }

  loading.value = true
  try {
    await auth.register({
      username: username.value,
      password: password.value,
      email: email.value,
    })
    router.push('/')
  } catch (e) {
    const err = e.response?.data?.error
    if (err === 'exists') {
      error.value = 'Пользователь с таким именем уже существует'
    } else if (err === 'required fields') {
      error.value = 'Заполните логин и пароль'
    } else {
      error.value = e.response?.data?.detail || 'Ошибка регистрации'
    }
    toast.danger(error.value)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-vh-100 d-flex align-items-center justify-content-center bg-light px-3 py-4">
    <div class="w-100" style="max-width: 420px">
      <div class="text-center mb-4">
        <i class="bi bi-person-plus display-4 text-primary" aria-hidden="true" />
        <h1 class="h3 mt-2 mb-0">Регистрация</h1>
        <p class="text-muted small mb-0">Создайте учётную запись</p>
      </div>

      <form class="card shadow-sm border-0" @submit.prevent="submit">
        <div class="card-body p-4">
          <div v-if="error" class="alert alert-danger py-2 mb-3" role="alert">
            {{ error }}
          </div>

          <div class="mb-3">
            <label class="form-label" for="reg-username">Имя пользователя</label>
            <input
              id="reg-username"
              v-model="username"
              type="text"
              class="form-control"
              required
              autocomplete="username"
              :disabled="loading"
            >
          </div>

          <div class="mb-3">
            <label class="form-label" for="reg-email">Email</label>
            <input
              id="reg-email"
              v-model="email"
              type="email"
              class="form-control"
              autocomplete="email"
              placeholder="name@example.com"
              :disabled="loading"
            >
          </div>

          <div class="mb-3">
            <label class="form-label" for="reg-password">Пароль</label>
            <input
              id="reg-password"
              v-model="password"
              type="password"
              class="form-control"
              required
              autocomplete="new-password"
              minlength="1"
              :disabled="loading"
            >
          </div>

          <div class="mb-4">
            <label class="form-label" for="reg-password-confirm">Подтверждение пароля</label>
            <input
              id="reg-password-confirm"
              v-model="passwordConfirm"
              type="password"
              class="form-control"
              required
              autocomplete="new-password"
              placeholder="Повторите пароль"
              :disabled="loading"
            >
          </div>

          <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
            {{ loading ? 'Регистрация…' : 'Зарегистрироваться' }}
          </button>

          <p class="mt-4 mb-0 text-center text-muted small">
            Уже есть аккаунт?
            <router-link to="/login" class="text-decoration-none">Войти</router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

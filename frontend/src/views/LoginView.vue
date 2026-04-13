<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'
import { useToastStore } from '../stores/toast'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await auth.login({ username: username.value, password: password.value })
    const next = route.query.redirect
    if (typeof next === 'string' && next.startsWith('/')) {
      router.push(next)
    } else {
      router.push('/')
    }
  } catch (e) {
    const code = e.response?.data?.error
    if (code === 'invalid') {
      error.value = 'Неверный логин или пароль'
    } else {
      error.value = e.response?.data?.detail || e.message || 'Ошибка входа'
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
        <i class="bi bi-box-arrow-in-right display-4 text-primary" aria-hidden="true" />
        <h1 class="h3 mt-2 mb-0">Вход</h1>
        <p class="text-muted small mb-0">Система складского учёта</p>
      </div>

      <form class="card shadow-sm border-0" @submit.prevent="submit">
        <div class="card-body p-4">
          <div v-if="error" class="alert alert-danger py-2 mb-3" role="alert">
            {{ error }}
          </div>

          <div class="mb-3">
            <label class="form-label" for="login-username">Имя пользователя</label>
            <input
              id="login-username"
              v-model="username"
              type="text"
              class="form-control"
              required
              autocomplete="username"
              placeholder="username"
              :disabled="loading"
            >
          </div>

          <div class="mb-4">
            <label class="form-label" for="login-password">Пароль</label>
            <input
              id="login-password"
              v-model="password"
              type="password"
              class="form-control"
              required
              autocomplete="current-password"
              placeholder="••••••••"
              :disabled="loading"
            >
          </div>

          <button type="submit" class="btn btn-primary w-100 py-2" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true" />
            {{ loading ? 'Вход…' : 'Войти' }}
          </button>

          <p class="mt-4 mb-0 text-center text-muted small">
            Нет аккаунта?
            <router-link to="/register" class="text-decoration-none">Зарегистрироваться</router-link>
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

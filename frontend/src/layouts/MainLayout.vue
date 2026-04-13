<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const sidebarOpen = ref(false)

const displayName = computed(() => {
  const u = auth.user
  if (!u) return 'Пользователь'
  if (u.username) return u.username
  if (u.id != null) return `Пользователь #${u.id}`
  return 'Пользователь'
})

function logout() {
  auth.logout()
  router.push({ name: 'login' })
}

function closeSidebar() {
  sidebarOpen.value = false
}

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

function onResize() {
  if (window.innerWidth >= 768) {
    sidebarOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', onResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', onResize)
})
</script>

<template>
  <div class="sklad-layout min-vh-100 d-flex">
    <!-- Мобильный затемнитель -->
    <div
      v-show="sidebarOpen"
      class="sklad-backdrop d-md-none"
      aria-hidden="true"
      @click="closeSidebar"
    />

    <!-- Боковая панель -->
    <aside
      class="sklad-sidebar bg-white border-end"
      :class="{ 'sklad-sidebar--open': sidebarOpen }"
    >
      <div class="sklad-sidebar-inner d-flex flex-column h-100">
        <div class="p-3 border-bottom">
          <router-link
            to="/"
            class="sklad-brand text-decoration-none fw-semibold text-body d-flex align-items-center gap-2"
            @click="closeSidebar"
          >
            <i class="bi bi-box-seam-fill text-primary fs-4" aria-hidden="true" />
            <span>Склад</span>
          </router-link>
        </div>

        <nav class="flex-grow-1 py-3 px-2 overflow-auto">
          <ul class="nav nav-pills flex-column gap-1">
            <li class="nav-item">
              <router-link
                :to="{ name: 'dashboard' }"
                class="nav-link d-flex align-items-center gap-2"
                active-class="active"
                @click="closeSidebar"
              >
                <i class="bi bi-speedometer2" aria-hidden="true" />
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link
                to="/categories"
                class="nav-link d-flex align-items-center gap-2"
                active-class="active"
                @click="closeSidebar"
              >
                <i class="bi bi-folder2-open" aria-hidden="true" />
                Категории
              </router-link>
            </li>
            <li class="nav-item">
              <router-link
                to="/products"
                class="nav-link d-flex align-items-center gap-2"
                active-class="active"
                @click="closeSidebar"
              >
                <i class="bi bi-box-seam" aria-hidden="true" />
                Товары
              </router-link>
            </li>
            <li class="nav-item">
              <router-link
                to="/receipts"
                class="nav-link d-flex align-items-center gap-2"
                active-class="active"
                @click="closeSidebar"
              >
                <i class="bi bi-arrow-down-circle" aria-hidden="true" />
                Поступления
              </router-link>
            </li>
            <li class="nav-item">
              <router-link
                to="/writeoffs"
                class="nav-link d-flex align-items-center gap-2"
                active-class="active"
                @click="closeSidebar"
              >
                <i class="bi bi-arrow-up-circle" aria-hidden="true" />
                Списания
              </router-link>
            </li>
          </ul>
        </nav>
      </div>
    </aside>

    <!-- Основная колонка: шапка + контент -->
    <div class="sklad-main flex-grow-1 d-flex flex-column min-vh-100 min-w-0">
      <header class="sklad-header bg-white border-bottom shadow-sm sticky-top py-2 px-3 px-md-4">
        <div class="d-flex align-items-center justify-content-between gap-3">
          <button
            type="button"
            class="btn btn-outline-secondary d-md-none"
            aria-label="Открыть меню"
            @click="toggleSidebar"
          >
            <i class="bi bi-list fs-5" aria-hidden="true" />
          </button>
          <div class="d-none d-md-block text-muted small">
            Система складского учёта
          </div>
          <div class="d-flex align-items-center gap-2 ms-auto">
            <span class="text-muted small text-truncate" style="max-width: 12rem" :title="displayName">
              <i class="bi bi-person-circle me-1" aria-hidden="true" />
              {{ displayName }}
            </span>
            <button type="button" class="btn btn-outline-danger btn-sm" @click="logout">
              <i class="bi bi-box-arrow-right me-1" aria-hidden="true" />
              Выход
            </button>
          </div>
        </div>
      </header>

      <main class="sklad-content flex-grow-1 bg-light p-3 p-md-4">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.sklad-layout {
  --sklad-sidebar-width: 260px;
}

.sklad-sidebar {
  width: var(--sklad-sidebar-width);
  flex-shrink: 0;
  z-index: 1040;
}

.sklad-sidebar-inner {
  min-height: 100vh;
}

@media (min-width: 768px) {
  .sklad-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
  }

  .sklad-main {
    margin-left: var(--sklad-sidebar-width);
  }
}

@media (max-width: 767.98px) {
  .sklad-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.12);
  }

  .sklad-sidebar--open {
    transform: translateX(0);
  }

  .sklad-main {
    width: 100%;
  }
}

.sklad-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  z-index: 1030;
}

.nav-pills .nav-link {
  color: var(--bs-body-color);
  border-radius: 0.375rem;
}

.nav-pills .nav-link:hover {
  background-color: var(--bs-light);
}

.nav-pills .nav-link.active {
  background-color: var(--bs-primary);
  color: #fff;
}

.nav-pills .nav-link.active i {
  opacity: 1;
}
</style>

import { createRouter, createWebHistory } from 'vue-router'

import { TOKEN_KEY } from '../services/api'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: () => import('../layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/DashboardView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'categories',
          name: 'categories',
          component: () => import('../views/CategoryListView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'categories/create',
          name: 'category-create',
          component: () => import('../views/CategoryFormView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'categories/:id/edit',
          name: 'category-edit',
          component: () => import('../views/CategoryFormView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'categories/:id',
          name: 'category-detail',
          component: () => import('../views/CategoryDetailView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'products',
          name: 'products',
          component: () => import('../views/ProductListView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'products/create',
          name: 'product-create',
          component: () => import('../views/ProductFormView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'products/:id/edit',
          name: 'product-edit',
          component: () => import('../views/ProductFormView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'products/:id',
          name: 'product-detail',
          component: () => import('../views/ProductDetailView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'receipts',
          name: 'receipts',
          component: () => import('../views/ReceiptListView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'receipts/create',
          name: 'receipt-create',
          component: () => import('../views/ReceiptFormView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'receipts/:id/edit',
          name: 'receipt-edit',
          component: () => import('../views/ReceiptFormView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'receipts/:id',
          name: 'receipt-detail',
          component: () => import('../views/ReceiptDetailView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'writeoffs',
          name: 'writeoffs',
          component: () => import('../views/WriteoffListView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'writeoffs/create',
          name: 'writeoff-create',
          component: () => import('../views/WriteoffFormView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'writeoffs/:id/edit',
          name: 'writeoff-edit',
          component: () => import('../views/WriteoffFormView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'writeoffs/:id',
          name: 'writeoff-detail',
          component: () => import('../views/WriteoffDetailView.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
  ],
})

router.beforeEach((to, _from, next) => {
  const needsAuth = to.matched.some((record) => record.meta.requiresAuth)
  const token = localStorage.getItem(TOKEN_KEY)
  if (needsAuth && !token) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router

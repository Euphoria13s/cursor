import { defineStore } from 'pinia'
import { ref } from 'vue'

import api from '../services/api'

const DEFAULT_PAGE_SIZE = 20

export const useReceiptStore = defineStore('receipts', () => {
  const items = ref([])
  const currentItem = ref(null)
  const loading = ref(false)
  const totalPages = ref(0)
  const filters = ref({})

  async function fetchAll(params = {}) {
    loading.value = true
    try {
      const query = { ...filters.value, ...params }
      const { data } = await api.get('/receipts/', { params: query })

      if (data?.results) {
        items.value = data.results
        if (typeof data.count === 'number') {
          const pageSize = Number(query.page_size) || DEFAULT_PAGE_SIZE
          totalPages.value = data.count > 0 ? Math.ceil(data.count / pageSize) : 0
        }
      } else if (Array.isArray(data)) {
        items.value = data
        totalPages.value = 1
      } else {
        items.value = []
        totalPages.value = 0
      }

      return data
    } catch (error) {
      console.error('[receipts] fetchAll', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function fetchOne(id) {
    loading.value = true
    try {
      const { data } = await api.get(`/receipts/${id}/`)
      currentItem.value = data
      return data
    } catch (error) {
      console.error('[receipts] fetchOne', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function create(data) {
    loading.value = true
    try {
      const { data: created } = await api.post('/receipts/', data)
      items.value = [created, ...items.value]
      currentItem.value = created
      return created
    } catch (error) {
      console.error('[receipts] create', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function update(id, data) {
    loading.value = true
    try {
      const { data: updated } = await api.patch(`/receipts/${id}/`, data)
      const idx = items.value.findIndex((item) => item.id === id)
      if (idx !== -1) {
        items.value[idx] = updated
      }
      if (currentItem.value?.id === id) {
        currentItem.value = updated
      }
      return updated
    } catch (error) {
      console.error('[receipts] update', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  async function remove(id) {
    loading.value = true
    try {
      await api.delete(`/receipts/${id}/`)
      items.value = items.value.filter((item) => item.id !== id)
      if (currentItem.value?.id === id) {
        currentItem.value = null
      }
    } catch (error) {
      console.error('[receipts] remove', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  return {
    items,
    currentItem,
    loading,
    totalPages,
    filters,
    fetchAll,
    fetchOne,
    create,
    update,
    remove,
  }
})

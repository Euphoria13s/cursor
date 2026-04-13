/** Дата/время для отображения в таблицах */
export function formatDateTime(value) {
  if (value == null || value === '') return '—'
  const d = value instanceof Date ? value : new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  return d.toLocaleString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/** Только дата */
export function formatDate(value) {
  if (value == null || value === '') return '—'
  const s = String(value)
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
    const [y, m, day] = s.split('-')
    return `${day}.${m}.${y}`
  }
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return s
  return d.toLocaleDateString('ru-RU')
}

export function formatMoney(value) {
  if (value == null || value === '') return '—'
  const n = Number(value)
  if (Number.isNaN(n)) return String(value)
  return n.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export const DOC_STATUS_LABELS = {
  draft: 'Черновик',
  posted: 'Проведён',
  cancelled: 'Отменён',
}

export function formatDocStatus(code) {
  if (code == null || code === '') return '—'
  return DOC_STATUS_LABELS[code] || code
}

export function boolRu(value) {
  return value ? 'Да' : 'Нет'
}

export function truncate(text, max = 48) {
  if (text == null || text === '') return '—'
  const s = String(text)
  return s.length <= max ? s : `${s.slice(0, max)}…`
}

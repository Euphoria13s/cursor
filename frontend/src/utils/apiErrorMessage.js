/**
 * Краткое сообщение об ошибке API для тоста (без привязки к полям формы).
 * @param {unknown} error
 * @param {string} [fallback]
 */
export function apiErrorMessage(error, fallback = 'Не удалось выполнить операцию') {
  const data = error?.response?.data
  if (data && typeof data === 'object') {
    if (data.detail != null) {
      const d = data.detail
      return Array.isArray(d) ? d.join(' ') : String(d)
    }
    const entries = Object.entries(data)
    if (entries.length) {
      const [key, val] = entries[0]
      const msg = Array.isArray(val)
        ? val.map((x) => (typeof x === 'string' ? x : JSON.stringify(x))).join(' ')
        : typeof val === 'object' && val !== null
          ? JSON.stringify(val)
          : String(val)
      const line = key === 'non_field_errors' ? msg : `${key}: ${msg}`
      return line.length > 220 ? `${line.slice(0, 217)}…` : line
    }
  }
  if (error?.message) return String(error.message)
  return fallback
}

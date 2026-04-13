/**
 * Разбор ответа DRF (400) и запись сообщений в объект fieldErrors.
 * @param {unknown} error — из catch
 * @param {Record<string, string>} fieldErrors — реактивный или обычный объект полей
 * @param {string[]} knownFields — ключи полей формы + '_form'
 */
export function mapDrfErrors(error, fieldErrors, knownFields) {
  for (const k of knownFields) {
    if (k in fieldErrors) fieldErrors[k] = ''
  }
  const data = error.response?.data
  if (!data || typeof data !== 'object') {
    fieldErrors._form = error.message || 'Ошибка запроса'
    return
  }
  if (data.detail != null) {
    const d = data.detail
    fieldErrors._form = Array.isArray(d) ? d.join(' ') : String(d)
    return
  }
  const extra = []
  for (const [key, val] of Object.entries(data)) {
    const msg = Array.isArray(val)
      ? val.map((x) => (typeof x === 'string' ? x : JSON.stringify(x))).join(' ')
      : typeof val === 'object' && val !== null
        ? JSON.stringify(val)
        : String(val)
    if (knownFields.includes(key) && key in fieldErrors) {
      fieldErrors[key] = msg
    } else if (key === 'non_field_errors') {
      extra.push(msg)
    } else {
      extra.push(`${key}: ${msg}`)
    }
  }
  if (extra.length) {
    fieldErrors._form = [fieldErrors._form, ...extra].filter(Boolean).join(' ')
  }
  if (!fieldErrors._form && !knownFields.some((k) => k !== '_form' && fieldErrors[k])) {
    fieldErrors._form = 'Проверьте введённые данные'
  }
}

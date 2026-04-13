import { describe, it, expect } from 'vitest'

describe('API smoke tests', () => {
  it('api placeholder passes', () => {
    const response = { ok: true }
    expect(response.ok).toBe(true)
  })
})